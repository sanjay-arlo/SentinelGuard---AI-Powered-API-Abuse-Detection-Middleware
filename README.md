# SentinelGuard - API Abuse Detection Middleware

A **production-oriented prototype** of FastAPI middleware that sits between NGINX and backend services and demonstrates behavioral rate limiting, abuse detection and risk scoring.

## Scope

SentinelGuard is a portfolio engineering project. It is designed to demonstrate architecture, security patterns, asynchronous processing and detection logic; it has not been represented as a deployed production security service.

## Overview

The middleware analyzes request behaviour rather than relying only on request volume. The prototype covers:
- Slow-drip bot patterns
- Credential-stuffing-style activity
- Sequential ID probing
- Regular-interval automation

## Architecture

```text
Internet -> NGINX (Port 80/443) -> SentinelGuard (Port 8000) -> Backend API (Port 8001)
```

## Key Features

- Behavioral risk scoring
- Request fingerprint tracking
- Pattern detection
- Per-endpoint thresholds
- Automatic cooldown/unblocking
- Monitoring endpoints

## Tech Stack

- Python 3.11+
- FastAPI / Uvicorn
- PostgreSQL 15+
- Redis 7+
- Celery
- SQLAlchemy 2.0
- Docker / Docker Compose
- NGINX

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/sanjay-arlo/SentinelGuard---AI-Powered-API-Abuse-Detection-Middleware.git
   cd SentinelGuard---AI-Powered-API-Abuse-Detection-Middleware
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copy the environment template and set local values:
   ```bash
   cp .env.example .env
   ```
4. Start the local dependencies with Docker Compose.
5. Run database migrations:
   ```bash
   alembic upgrade head
   ```
6. Start the application using the repository's documented run command.

## Configuration

Never commit real secrets. Use environment variables for database passwords, API keys and signing secrets.

## API Documentation

The application exposes health, monitoring and administrative endpoints documented in the FastAPI OpenAPI interface when the local server is running.

## Testing and Code Quality

```bash
pytest
black app/
ruff check app/
mypy app/
```

## Deployment Notes

Docker/Kubernetes deployment is included as an architectural option for experimentation. A real production deployment would additionally require security review, load testing, secret management, observability validation, failure-mode testing and operational runbooks.

## License

MIT License - see LICENSE.
