import logging
import secrets
import string

from audit.audit_log import AuditLogger
from vault.vault_engine import VaultEngine

from .simulators import DatabaseSimulator, LinuxSimulator, WindowsSimulator

logger = logging.getLogger(__name__)

class Rotator:
    def __init__(self, vault: VaultEngine, auditor: AuditLogger):
        self.vault = vault
        self.auditor = auditor
        self.win_sim = WindowsSimulator()
        self.linux_sim = LinuxSimulator()
        self.db_sim = DatabaseSimulator()

    def generate_password(self, length: int = 24) -> str:
        """Generate a strong random password."""
        chars = string.ascii_letters + string.digits + "!@#$%^&*()"
        return ''.join(secrets.choice(chars) for _ in range(length))

    def rotate_secret(self, secret_id: str, triggered_by: str = "system") -> bool:
        """Perform rotation for a specific secret."""
        meta = self.vault.get_metadata(secret_id)
        if not meta:
            logger.error(f"Secret {secret_id} not found during rotation.")
            return False

        secret_type = meta['type']
        target_host = meta['metadata'].get('host', 'localhost')
        username = meta['metadata'].get('username', 'admin')

        logger.info(f"🔄 Starting rotation for {secret_id} ({secret_type})...")
        
        new_password = self.generate_password()
        success = False

        try:
            if secret_type == 'windows':
                success = self.win_sim.change_password(target_host, username, new_password)
            elif secret_type == 'linux':
                success = self.linux_sim.change_password(target_host, username, new_password)
            elif secret_type == 'database':
                success = self.db_sim.change_password(target_host, username, new_password)
            else:
                logger.error(f"Unknown secret type: {secret_type}")
                return False

            if success:
                self.vault.update_secret_value(secret_id, new_password)
                self.auditor.log_event(
                    action="ROTATE_SECRET",
                    user=triggered_by,
                    secret_id=secret_id,
                    details={"host": target_host, "status": "rotated"},
                    success=True
                )
                logger.info(f"✅ Rotation complete for {secret_id}.")
                return True
            else:
                raise Exception("Target system update failed")

        except Exception as e:
            self.auditor.log_event(
                action="ROTATE_FAILURE",
                user=triggered_by,
                secret_id=secret_id,
                details={"error": str(e)},
                success=False
            )
            logger.error(f"❌ Rotation failed for {secret_id}: {e}")
            return False
