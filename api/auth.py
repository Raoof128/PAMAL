from typing import Optional

from fastapi import Header, HTTPException

# In a real PAM, this would verify JWTs or check against an Identity Provider (IdP)
# For this lab, we use a simple header-based mock authentication.

def get_current_user(x_user: Optional[str] = Header(None)) -> str:
    """
    Mock authentication dependency.
    In production, replace this with OAuth2/OIDC token validation.
    """
    if not x_user:
        raise HTTPException(status_code=401, detail="Missing X-User header. Authentication required.")
    
    # Simulate user validation
    # Here you could check if the user exists in a user DB
    return x_user
