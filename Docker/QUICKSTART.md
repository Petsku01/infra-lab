# Quick Reference

## Getting Started

```bash
git clone <repository>
cd Docker
cp .env.example .env
docker-compose up
```

## Common Commands

```bash
# Build
docker build -t calculator:latest Calculator_java_docker/

# Test
mvn clean test

# Scan
trivy image calculator:latest

# Logs
docker logs -f <container-name>

# Stop
docker-compose down
```

## Key Files

- `.env.example` - Configuration template
- `DEPLOYMENT.md` - Deployment guide
- `ADR.md` - Architecture decisions
- `SECURITY_CHECKLIST.md` - Security verification

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port in use | Change port in `.env` |
| Build fails | Check Dockerfile, ensure base images exist |
| Container exits | Run `docker logs <name>` |
| Permission denied | Run `chmod +x scripts/*.sh` |

## Environment

```properties
SERVER_PORT=8080
START_URLS=https://example.com
RATE_LIMIT_SEC=5
LOG_LEVEL=INFO
```

## Health Check

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

---
*Author: pk*
