from unittest.mock import MagicMock

import pytest

from audit.audit_log import AuditLogger
from rotation.rotator import Rotator
from vault.vault_engine import VaultEngine


@pytest.fixture
def mock_vault():
    vault = MagicMock(spec=VaultEngine)
    vault.get_metadata.return_value = {
        "id": "test-rot-01",
        "type": "linux",
        "metadata": {"host": "192.168.1.50", "username": "root"}
    }
    return vault

@pytest.fixture
def mock_auditor():
    return MagicMock(spec=AuditLogger)

def test_rotator_linux(mock_vault, mock_auditor):
    rotator = Rotator(mock_vault, mock_auditor)
    
    # Mock the simulator to avoid actual network calls
    rotator.linux_sim.change_password = MagicMock(return_value=True)
    
    success = rotator.rotate_secret("test-rot-01")
    
    assert success is True
    rotator.linux_sim.change_password.assert_called_once()
    mock_vault.update_secret_value.assert_called_once()
    mock_auditor.log_event.assert_called()

def test_rotator_failure(mock_vault, mock_auditor):
    rotator = Rotator(mock_vault, mock_auditor)
    
    # Mock failure
    rotator.linux_sim.change_password = MagicMock(return_value=False)
    
    success = rotator.rotate_secret("test-rot-01")
    
    assert success is False
    mock_vault.update_secret_value.assert_not_called()
