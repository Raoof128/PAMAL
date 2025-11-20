import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoEngine:
    def __init__(self, master_key: str):
        self.master_key = master_key.encode()
        self.backend = default_backend()

    def _derive_key(self, salt: bytes) -> bytes:
        """Derive a 32-byte key from the master key using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        return kdf.derive(self.master_key)

    def encrypt(self, plaintext: str) -> dict:
        """Encrypt plaintext using AES-256-GCM."""
        salt = os.urandom(16)
        key = self._derive_key(salt)
        iv = os.urandom(12)  # GCM recommended IV length

        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=self.backend
        ).encryptor()

        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()

        return {
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "iv": base64.b64encode(iv).decode('utf-8'),
            "salt": base64.b64encode(salt).decode('utf-8'),
            "tag": base64.b64encode(encryptor.tag).decode('utf-8')
        }

    def decrypt(self, encrypted_data: dict) -> str:
        """Decrypt ciphertext using AES-256-GCM."""
        salt = base64.b64decode(encrypted_data['salt'])
        iv = base64.b64decode(encrypted_data['iv'])
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        tag = base64.b64decode(encrypted_data['tag'])

        key = self._derive_key(salt)

        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=self.backend
        ).decryptor()

        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode('utf-8')
