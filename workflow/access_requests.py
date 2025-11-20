import uuid
from datetime import datetime, timedelta
from typing import Optional


class AccessWorkflow:
    def __init__(self):
        # In-memory store for requests (use DB in prod)
        self.requests = {} 

    def create_request(self, user: str, secret_id: str, reason: str) -> str:
        req_id = str(uuid.uuid4())[:8]
        self.requests[req_id] = {
            "id": req_id,
            "user": user,
            "secret_id": secret_id,
            "reason": reason,
            "status": "PENDING",
            "created_at": datetime.now().isoformat(),
            "expires_at": None
        }
        return req_id

    def approve_request(self, req_id: str, approver: str, ttl_minutes: int) -> Optional[dict]:
        if req_id not in self.requests:
            return None
        
        req = self.requests[req_id]
        if req['status'] != 'PENDING':
            return req

        req['status'] = 'APPROVED'
        req['approver'] = approver
        req['approved_at'] = datetime.now().isoformat()
        req['expires_at'] = (datetime.now() + timedelta(minutes=ttl_minutes)).isoformat()
        
        return req

    def get_request(self, req_id: str):
        return self.requests.get(req_id)

    def is_access_valid(self, req_id: str, user: str) -> bool:
        req = self.requests.get(req_id)
        if not req:
            return False
        
        if req['user'] != user:
            return False
            
        if req['status'] != 'APPROVED':
            return False

        if not req['expires_at']:
            return False

        expires = datetime.fromisoformat(req['expires_at'])
        if datetime.now() > expires:
            return False

        return True
