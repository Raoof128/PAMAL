import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from .crypto import CryptoEngine


class VaultEngine:
    def __init__(self, master_password: str, db_path: str):
        self.crypto = CryptoEngine(master_password)
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initialize the SQLite database."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS secrets (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    ciphertext TEXT NOT NULL,
                    iv TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT,
                    last_rotated TEXT
                )
            ''')
            conn.commit()

    def store_secret(
        self, 
        secret_id: str, 
        name: str, 
        secret_type: str, 
        value: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Encrypt and store a secret."""
        encrypted = self.crypto.encrypt(value)
        
        meta_json = json.dumps(metadata or {})
        now = datetime.now().isoformat()

        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO secrets 
                (id, name, type, ciphertext, iv, salt, tag, metadata, created_at, last_rotated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                secret_id, name, secret_type,
                encrypted['ciphertext'], encrypted['iv'], encrypted['salt'], encrypted['tag'],
                meta_json, now, now
            ))
            conn.commit()

    def get_secret(self, secret_id: str) -> Optional[str]:
        """Retrieve and decrypt a secret."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute('SELECT ciphertext, iv, salt, tag FROM secrets WHERE id = ?', (secret_id,))
            row = c.fetchone()

        if not row:
            return None

        encrypted_data = {
            'ciphertext': row[0],
            'iv': row[1],
            'salt': row[2],
            'tag': row[3]
        }
        return self.crypto.decrypt(encrypted_data)

    def get_metadata(self, secret_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for a secret."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute(
                'SELECT id, name, type, metadata, created_at, last_rotated FROM secrets WHERE id = ?', 
                (secret_id,)
            )
            row = c.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "metadata": json.loads(row[3]),
            "created_at": row[4],
            "last_rotated": row[5]
        }

    def list_secrets(self) -> List[Dict[str, Any]]:
        """List all secrets (metadata only)."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute('SELECT id, name, type, last_rotated FROM secrets')
            rows = c.fetchall()
        
        return [
            {"id": r[0], "name": r[1], "type": r[2], "last_rotated": r[3]}
            for r in rows
        ]

    def update_secret_value(self, secret_id: str, new_value: str) -> None:
        """Update the value of an existing secret (rotation)."""
        encrypted = self.crypto.encrypt(new_value)
        now = datetime.now().isoformat()
        
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute('''
                UPDATE secrets 
                SET ciphertext = ?, iv = ?, salt = ?, tag = ?, last_rotated = ?
                WHERE id = ?
            ''', (
                encrypted['ciphertext'], encrypted['iv'], encrypted['salt'], encrypted['tag'],
                now, secret_id
            ))
            conn.commit()
