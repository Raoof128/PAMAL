from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from api.auth import get_current_user
from api.config import settings
from api.policies import PolicyEngine
from audit.audit_log import AuditLogger
from rotation.rotator import Rotator
from vault.vault_engine import VaultEngine
from workflow.access_requests import AccessWorkflow

app = FastAPI(
    title="PAM Automation Lab",
    description="A lightweight Privileged Access Management system.",
    version="1.0.0"
)

# Initialize components
vault = VaultEngine(settings.pam_master_key, db_path=settings.db_path)
auditor = AuditLogger(log_file=settings.audit_log_file)
rotator = Rotator(vault, auditor)
policy_engine = PolicyEngine(policy_file=settings.policy_file)
workflow = AccessWorkflow()

# --- Models ---
class SecretCreate(BaseModel):
    id: str
    name: str
    type: str
    value: str
    metadata: Optional[dict] = {}

class SecretResponse(BaseModel):
    id: str
    name: str
    type: str
    last_rotated: str

class AccessRequest(BaseModel):
    user: str
    secret_id: str
    reason: str

class ApprovalRequest(BaseModel):
    admin_user: str
    request_id: str
    decision: str  # APPROVED / DENIED

class CredentialResponse(BaseModel):
    secret: str
    expires_at: str

# --- Endpoints ---

@app.post("/secrets", status_code=201)
def create_secret(secret: SecretCreate, user: str = Depends(get_current_user)):
    """Create a new secret in the vault."""
    try:
        vault.store_secret(secret.id, secret.name, secret.type, secret.value, secret.metadata)
        auditor.log_event("CREATE_SECRET", user, secret.id)
        return {"status": "created", "id": secret.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/secrets", response_model=List[SecretResponse])
def list_secrets(user: str = Depends(get_current_user)):
    """List all secrets (metadata only)."""
    auditor.log_event("LIST_SECRETS", user)
    return vault.list_secrets()

@app.post("/request")
def request_access(req: AccessRequest):
    """Request access to a privileged secret."""
    # Check policy
    meta = vault.get_metadata(req.secret_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Secret not found")
    
    role = meta['metadata'].get('role', 'linux-admin')
    
    policy = policy_engine.check_access(req.user, role)
    if not policy['allowed']:
        auditor.log_event("ACCESS_DENIED", req.user, req.secret_id, {"reason": policy.get('reason')}, False)
        raise HTTPException(status_code=403, detail=policy.get('reason', 'Access denied'))

    if policy['approval_required']:
        req_id = workflow.create_request(req.user, req.secret_id, req.reason)
        auditor.log_event("REQUEST_CREATED", req.user, req.secret_id, {"req_id": req_id})
        return {"status": "pending_approval", "request_id": req_id, "message": "Admin approval required"}
    else:
        # Auto-approve
        req_id = workflow.create_request(req.user, req.secret_id, req.reason)
        workflow.approve_request(req_id, "SYSTEM", policy['ttl_minutes'])
        auditor.log_event("AUTO_APPROVED", req.user, req.secret_id)
        return {"status": "approved", "request_id": req_id, "ttl_minutes": policy['ttl_minutes']}

@app.post("/approve")
def approve_request(approval: ApprovalRequest, user: str = Depends(get_current_user)):
    """Approve a pending access request (Admin only)."""
    # In a real system, we would check if 'user' has admin privileges here.
    auditor.log_event("APPROVE_ATTEMPT", user, details={"req_id": approval.request_id})
    
    req = workflow.get_request(approval.request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    if approval.decision == "APPROVED":
        meta = vault.get_metadata(req['secret_id'])
        if not meta:
             raise HTTPException(status_code=404, detail="Secret associated with request not found")
             
        role = meta['metadata'].get('role', 'linux-admin')
        policy = policy_engine.check_access(req['user'], role)
        
        workflow.approve_request(approval.request_id, approval.admin_user, policy.get('ttl_minutes', 15))
        auditor.log_event("REQUEST_APPROVED", approval.admin_user, req['secret_id'], {"req_id": approval.request_id})
        return {"status": "approved"}
    else:
        auditor.log_event("REQUEST_DENIED", approval.admin_user, req['secret_id'], {"req_id": approval.request_id})
        return {"status": "denied"}

@app.get("/credential/{request_id}", response_model=CredentialResponse)
def get_credential(request_id: str, user: str = Depends(get_current_user)):
    """Retrieve a secret using a valid, approved request ID."""
    if not workflow.is_access_valid(request_id, user):
        auditor.log_event(
            "RETRIEVAL_FAILED", user, details={"req_id": request_id, "reason": "invalid_or_expired"}, success=False
        )
        raise HTTPException(status_code=403, detail="Access invalid or expired")

    req = workflow.get_request(request_id)
    if not req:
         raise HTTPException(status_code=404, detail="Request not found")

    secret_value = vault.get_secret(req['secret_id'])
    if not secret_value:
        raise HTTPException(status_code=404, detail="Secret data not found")
    
    auditor.log_event("SECRET_RETRIEVED", user, req['secret_id'], {"req_id": request_id})
    return {"secret": secret_value, "expires_at": req['expires_at']}

@app.post("/rotate/{secret_id}")
def rotate_secret(secret_id: str, user: str = Depends(get_current_user)):
    """Manually trigger rotation for a secret."""
    success = rotator.rotate_secret(secret_id, triggered_by=user)
    if success:
        return {"status": "rotated"}
    else:
        raise HTTPException(status_code=500, detail="Rotation failed")

@app.get("/audit")
def get_audit_logs(limit: int = 20, user: str = Depends(get_current_user)):
    """Retrieve audit logs."""
    auditor.log_event("AUDIT_ACCESS", user)
    return auditor.get_logs(limit)
