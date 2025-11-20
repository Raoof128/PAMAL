import os

import yaml

DEFAULT_POLICIES = """
policies:
  - role: linux-admin
    approval_required: true
    ttl_minutes: 15
    rotation_hours: 24
    allowed_users: ["alice", "bob", "raouf"]

  - role: windows-admin
    approval_required: true
    ttl_minutes: 30
    rotation_hours: 12
    allowed_users: ["raouf", "charlie"]

  - role: db-readonly
    approval_required: false
    ttl_minutes: 60
    rotation_hours: 168
    allowed_users: ["*"]
"""

class PolicyEngine:
    def __init__(self, policy_file="policies.yaml"):
        self.policy_file = policy_file
        self.policies = self._load_policies()

    def _load_policies(self):
        if not os.path.exists(self.policy_file):
            with open(self.policy_file, "w") as f:
                f.write(DEFAULT_POLICIES)
        
        with open(self.policy_file, "r") as f:
            data = yaml.safe_load(f)
            return {p['role']: p for p in data.get('policies', [])}

    def check_access(self, user: str, role: str) -> dict:
        """Check if a user can access a role and return policy details."""
        policy = self.policies.get(role)
        if not policy:
            return {"allowed": False, "reason": "Role not defined"}

        allowed_users = policy.get('allowed_users', [])
        if "*" not in allowed_users and user not in allowed_users:
            return {"allowed": False, "reason": "User not authorized for this role"}

        return {
            "allowed": True,
            "approval_required": policy.get('approval_required', False),
            "ttl_minutes": policy.get('ttl_minutes', 15)
        }
