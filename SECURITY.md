# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a vulnerability in this project, please follow these steps:

1.  **Do NOT open a public issue.**
2.  Email the maintainers directly at `security@example.com` (replace with actual email).
3.  Include a detailed description of the vulnerability, steps to reproduce, and potential impact.

We will acknowledge your report within 48 hours and work to provide a fix as soon as possible.

## Security Best Practices used in this Project

*   **Encryption**: All secrets are encrypted using AES-256-GCM.
*   **Key Derivation**: Keys are derived using PBKDF2-HMAC-SHA256 with a unique salt per secret.
*   **No Plaintext Storage**: Secrets are never stored in plaintext on disk.
*   **Audit Logging**: All privileged actions are logged.

## Disclaimer

This is a **LAB** environment designed for educational purposes and demonstration of PAM concepts. While it uses strong cryptographic primitives, it is not intended to replace certified enterprise PAM solutions in critical production environments without further hardening (e.g., Hardware Security Modules, centralized identity management, TLS everywhere).
