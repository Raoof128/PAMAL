# 🛡️ Privileged Access Management (PAM) Automation Lab

**"Mini CyberArk Vault" with Automated Secret Rotation**

This project is a lightweight, enterprise-grade PAM system designed to demonstrate core concepts of privileged access security: secure vaulting, automated rotation, just-in-time (JIT) access, and comprehensive auditing.

---

## 🚀 Features

*   **🔐 Secure Vault**: AES-256-GCM encryption with PBKDF2 key derivation. Secrets are never stored in plaintext.
*   **🔄 Automated Rotation**: Automatically rotates passwords for Windows, Linux, and Databases (simulated targets).
*   **⏱️ Just-In-Time Access**: Users request access, admins approve, and short-lived credentials are issued.
*   **📜 Policy Engine**: Enforce rules like "Linux Admins need approval" or "Rotate every 24 hours".
*   **👁️ Audit Logging**: Every action (request, approval, retrieval, rotation) is logged for compliance.
*   **💻 CLI Tool**: A powerful `pamctl` CLI to manage the entire system.

---

## 🏗️ Architecture

```mermaid
graph TD
    User[User / CLI] -->|Request Access| API[FastAPI Gateway]
    Admin[Admin] -->|Approve Request| API
    API -->|Check Policy| Policy[Policy Engine]
    API -->|Store/Retrieve| Vault[Vault Engine (AES-256)]
    Vault -->|Persist| DB[(SQLite DB)]
    
    Rotator[Rotation Engine] -->|Schedule| Vault
    Rotator -->|Update Password| Target[Target Systems (Simulated)]
    
    API -->|Log Event| Audit[Audit Logger]
    Rotator -->|Log Event| Audit
```

---

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.9+
*   `pip`

### 1. Clone & Install
```bash
git clone https://github.com/yourusername/pam_lab.git
cd pam_lab
pip install -r requirements.txt
```

### 2. Run the Server
Start the PAM API server:
```bash
uvicorn api.server:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

---

## 🎮 Usage Guide (CLI)

Use the `pamctl` tool to interact with the system.

### 1. Initialize & List Secrets
Populate the vault with demo data:
```bash
python3 cli/pamctl.py init
python3 cli/pamctl.py list
```

### 2. Request Access (JIT Workflow)
Request access to a privileged account:
```bash
python3 cli/pamctl.py request linux-prod-01 --reason "Emergency Patching"
```
*Output:* `Request ID: <REQ_ID>` (Status: pending_approval)

### 3. Approve Request (Admin)
Approve the request using the ID from the previous step:
```bash
python3 cli/pamctl.py approve <REQ_ID>
```

### 4. Retrieve Password
Now the user can retrieve the password (valid for the policy duration):
```bash
python3 cli/pamctl.py get <REQ_ID>
```

### 5. Rotate Password
Manually trigger a password rotation:
```bash
python3 cli/pamctl.py rotate linux-prod-01
```

### 6. View Audit Logs
Check the audit trail:
```bash
python3 cli/pamctl.py audit
```

---

## 🛠️ Development

### Dev Container
This project includes a `.devcontainer` configuration. Open the folder in VS Code and click "Reopen in Container" to get a fully configured environment with Python, Docker, and all extensions pre-installed.

### Pre-commit Hooks
We use `pre-commit` to ensure code quality.
```bash
pip install pre-commit
pre-commit install
```
This will run `ruff`, `mypy`, and other checks automatically on every commit.

### 🧪 Running Tests

Run the test suite with coverage:
```bash
make test
```

---

## 📂 Project Structure

*   `api/`: FastAPI server and policy logic.
*   `vault/`: Core crypto engine (AES-256) and database storage.
*   `rotation/`: Logic for rotating passwords on target systems.
*   `workflow/`: Handles access requests and approvals.
*   `audit/`: Centralized logging.
*   `cli/`: Command-line interface tool.

---

## ⚠️ Disclaimer
This is a **LAB** environment designed for educational purposes. While it uses strong encryption (AES-256), it is not a replacement for commercial PAM solutions like CyberArk or HashiCorp Vault in production environments without further hardening (e.g., HSM integration, TLS, robust auth).
