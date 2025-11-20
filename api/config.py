from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    pam_master_key: str = Field(..., description="Master key for vault encryption")
    db_path: str = Field("pam_vault.db", description="Path to the SQLite vault database")
    audit_log_file: str = Field("audit.log", description="Path to the audit log file")
    policy_file: str = Field("policies.yaml", description="Path to the policy definition file")
    
    # Auth settings (for future expansion)
    secret_key: str = Field("unsafe-secret-key-change-me", description="Secret key for JWT signing")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
