import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class AuditLogger:
    def __init__(self, log_file: str = "audit.log"):
        self.log_file = log_file
        self.logger = logging.getLogger("pam_audit")
        self.logger.setLevel(logging.INFO)
        
        # Prevent adding multiple handlers if instantiated multiple times
        if not self.logger.handlers:
            # File Handler
            fh = logging.FileHandler(self.log_file)
            fh.setLevel(logging.INFO)
            formatter = logging.Formatter('%(message)s') # We log raw JSON
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
            
            # Console Handler (for demo visibility)
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def log_event(
        self, 
        action: str, 
        user: str, 
        secret_id: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None, 
        success: bool = True
    ) -> None:
        """Log a PAM event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user": user,
            "secret_id": secret_id,
            "success": success,
            "details": details or {}
        }
        
        # Log structured JSON
        self.logger.info(json.dumps(event))

    def get_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve last N logs."""
        if not os.path.exists(self.log_file):
            return []
            
        logs = []
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
        except Exception:
            return []
            
        return logs[-limit:]
