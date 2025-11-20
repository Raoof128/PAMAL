import os

import pytest

# Ensure PAM_MASTER_KEY is set for tests if not present
if "PAM_MASTER_KEY" not in os.environ:
    os.environ["PAM_MASTER_KEY"] = "test-master-key-for-pytest"

# Use a separate DB for API tests
if "DB_PATH" not in os.environ:
    os.environ["DB_PATH"] = "test_api.db"

@pytest.fixture(autouse=True)
def clean_db():
    """Clean up the test database before and after each test run."""
    # Import here to avoid circular imports or early initialization issues
    from api.server import vault
    
    db_path = os.environ.get("DB_PATH", "test_api.db")
    
    # Setup: clean and init
    if os.path.exists(db_path):
        os.remove(db_path)
    vault._init_db()
    
    yield
    
    # Teardown: clean
    if os.path.exists(db_path):
        os.remove(db_path)
