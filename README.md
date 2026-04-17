# SentinelGuard - AI-Powered API Abuse Detection Middleware

A production-grade FastAPI middleware that sits between NGINX and backend services, performing intelligent rate limiting and behavioral abuse detection using sliding window algorithms, risk scoring, and pattern analysis.

## Overview

SentinelGuard solves the limitations of traditional rate limiters by analyzing **behavior**, not just volume. It protects against sophisticated attacks including:
- Slow-drip bots (staying under rate limits)
- Credential stuffing (distributed IPs)
- Sequential ID probing
- Regular-interval automation

## Architecture

```
Internet -> NGINX (Port 80/443) -> SentinelGuard (Port 8000) -> Backend API (Port 8001)
```

## Key Features

- **Behavioral Scoring**: Risk analysis beyond simple request counting
- **Fingerprint Tracking**: IP + User-Agent + headers for accurate identification
- **Pattern Detection**: Regular intervals, sequential access, failed authentication bursts
- **Adaptive Thresholds**: Per-endpoint rate limiting configurations
- **Auto-Recovery**: Cooldown periods with automatic unblocking
- **Real-time Monitoring**: Live threat feeds and statistics

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0
- **Cache**: Redis 7.0+ for sliding windows and real-time data
- **Background Jobs**: Celery for async logging and cleanup
- **Infrastructure**: Docker, Docker Compose, NGINX

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone https://github.com/your-username/sentinelguard.git
   cd "SentinelGuard - AI-Powered API Abuse Detection Middleware"
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker**:
   ```bash
   docker-compose up -d
   ```

4. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Access the service**:
   - API: http://localhost:8000
   - Admin API: http://localhost:8000/api/v1/admin
   - Monitoring: http://localhost:8000/api/v1/monitor
   - Health: http://localhost:8000/health

## Configuration

Key environment variables:

```env
# Rate limiting defaults
DEFAULT_RATE_LIMIT=100
DEFAULT_WINDOW_SECONDS=60
DEFAULT_SCORE_THRESHOLD=50

# Database
DB_HOST=postgres
DB_NAME=sentinelguard
DB_USER=sentinel
DB_PASSWORD=your-password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Security
SECRET_KEY=your-secret-key
ADMIN_API_KEY=your-admin-api-key
```

## API Documentation

### Admin Endpoints
- `POST /api/v1/admin/blacklist` - Add IP to blacklist
- `DELETE /api/v1/admin/blacklist/{ip}` - Remove IP from blacklist
- `POST /api/v1/admin/whitelist` - Add IP to whitelist
- `GET /api/v1/admin/configs` - Get endpoint configurations

### Monitoring Endpoints
- `GET /api/v1/monitor/threats` - Live threat feed
- `GET /api/v1/monitor/stats` - Usage statistics
- `GET /api/v1/monitor/ip/{ip}` - IP-specific analysis

### Health Endpoints
- `GET /health` - Basic health check
- `GET /health/ready` - Readiness probe
- `GET /health/metrics` - Prometheus metrics

## Development

### Running Tests
```bash
pytest
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/e2e/           # End-to-end tests only
```

### Code Quality
```bash
black app/                  # Format code
ruff check app/             # Lint code
mypy app/                   # Type checking
```

### Database Migrations
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
alembic downgrade -1
```

## Monitoring

SentinelGuard provides comprehensive monitoring capabilities:

- **Real-time threat detection** with risk scoring
- **Request pattern analysis** for bot detection
- **IP reputation tracking** with blacklist/whitelist
- **Performance metrics** and response times
- **Prometheus metrics** for integration with monitoring systems

## Security Features

- **Sliding window rate limiting** prevents burst attacks
- **Behavioral analysis** detects sophisticated bots
- **Fingerprinting** tracks users across IP changes
- **Automatic blocking** with configurable cooldowns
- **Admin authentication** with API key protection

## Deployment

### Production Deployment
1. Set up PostgreSQL and Redis clusters
2. Configure environment variables
3. Deploy with Docker Compose or Kubernetes
4. Set up NGINX reverse proxy
5. Configure monitoring and alerting

### Docker Compose Production
```bash
cd docker
docker-compose up -d
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation in `/docs`
- Review the API reference at `/api/v1/docs`
