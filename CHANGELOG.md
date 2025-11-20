# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-21

### Added
- Initial release of the PAM Automation Lab.
- **Vault Engine**: AES-256-GCM encryption with SQLite backend.
- **Rotation Engine**: Automated password rotation for simulated Windows, Linux, and DB targets.
- **API**: FastAPI-based gateway for secret management and access requests.
- **CLI**: `pamctl` command-line tool for interacting with the system.
- **Audit**: Structured JSON logging for all events.
- **Policy**: Role-based access control and approval workflows.
- **Docker**: Containerization support with Docker Compose.
