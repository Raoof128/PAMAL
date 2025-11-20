import os

import pytest

from vault.crypto import CryptoEngine
from vault.vault_engine import VaultEngine

TEST_DB = "test_vault.db"
MASTER_KEY = "test_master_key_123"

@pytest.fixture
def vault():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    return VaultEngine(MASTER_KEY, db_path=TEST_DB)

def test_crypto_engine():
    crypto = CryptoEngine(MASTER_KEY)
    plaintext = "SecretPassword!"
    encrypted = crypto.encrypt(plaintext)
    
    assert encrypted['ciphertext'] != plaintext
    decrypted = crypto.decrypt(encrypted)
    assert decrypted == plaintext

def test_vault_storage(vault):
    vault.store_secret("test-01", "Test Secret", "linux", "MySecret123", {"host": "localhost"})
    
    secret = vault.get_secret("test-01")
    assert secret == "MySecret123"
    
    meta = vault.get_metadata("test-01")
    assert meta['id'] == "test-01"
    assert meta['type'] == "linux"

def test_vault_rotation(vault):
    vault.store_secret("test-02", "Rotation Test", "linux", "OldPass")
    vault.update_secret_value("test-02", "NewPass")
    
    secret = vault.get_secret("test-02")
    assert secret == "NewPass"
