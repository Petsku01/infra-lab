# Docker Projects Repository

A collection of containerized applications demonstrating Docker best practices, security hardening, and CI/CD integration.

## Projects Overview

| Project | Type | Purpose | Status |
|---------|------|---------|--------|
| **Calculator_java_docker** | Java 17 | Complex number calculator with CLI interface | Production-ready |
| **async-web-crawler** | Python 3.12 | Async web crawler with content analysis | Production-ready |
| **integration-tests** | Python 3.10 | Test environment for CI/CD integration | Production-ready |
| **devops-container** | Ubuntu 24.04 | Dev container with SSH, code-server, tools | Production-ready |

## Quick Start

### Prerequisites
- Docker & Docker Compose (latest)
- Git
- ~2GB disk space

### Clone & Setup
```bash
git clone <repository-url>
cd Docker
cp .env.example .env
# Edit .env with your configuration
```

### Run Individual Projects

**Complex Calculator**:
```bash
cd Calculator_java_docker
docker build -t complex-calculator:latest .
docker run -it --rm complex-calculator:latest
```

**Async Web Crawler**:
```bash
cd async-web-crawler
docker build -t async-web-crawler:latest .
docker run --rm async-web-crawler:latest --urls "https://example.com"
```

**Integration Tests**:
```bash
cd integration-tests
docker build -t integration-tests:latest .
docker run --rm -v $(pwd):/app integration-tests:latest python3 /app/test_process.py
```

**DevOps Container**:
Each container has detailed README documentation:
- **[async-web-crawler/README.md](./async-web-crawler/README.md)** - Web crawler usage and configuration
- **[Calculator_java_docker/README.md](./Calculator_java_docker/README.md)** - Complex calculator guide
- **[integration-tests/README.md](./integration-tests/README.md)** - Test environment setup
- **[devops-container/README.md](./devops-container/README.md)** - DevOps container guide
- **[QUICKSTART.md](./QUICKSTART.md)** - Quick start guide for all projects
- **[ADR.md](./ADR.md)** - Architecture Decision Records
ssh devuser@localhost -p 2222
```

## Documentation

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Complete deployment guide with examples
- **[ADR.md](./ADR.md)** - Architecture Decision Records explaining design choices
- **[SECURITY_CHECKLIST.md](./SECURITY_CHECKLIST.md)** - Security verification checklist
- **[CI/CD Pipeline](./.github/workflows/ci-cd.yml)** - GitHub Actions automation

## Security Improvements

Implemented:
- Non-root user execution in all containers
- Pinned dependency versions for reproducibility
- Health checks for automatic recovery
- Multi-stage builds for smaller images
- Environment-based configuration
- Comprehensive CI/CD with security scanning
- .gitignore to prevent secret leaks
- Docker image vulnerability scanning

## Testing
docker run --rm -v $(pwd):/app maven:3.9.9-eclipse-temurin-17 mvn -f /app/pom.xml clean test
```

### Code Quality
```bash
# Python linting (async-web-crawler)
cd async-web-crawler
docker run --rm -v $(pwd):/app python:3.12-slim bash -c "pip install flake8 pylint && flake8 /app/*.py && pylint /app/*.py"
```bash
# Python linting
flake8 Crawler_docker_ml/*.py
pylint Crawler_docker_ml/*.py
```

## CI/CD Pipeline

Automatic on every push:
- Security scanning (Trivy, Dependency-Check)
- Unit tests
- Code linting
- Docker image builds
- Container vulnerability scanning
- Secret detection

View: [GitHub Actions](./.github/workflows/ci-cd.yml)

## Environment Configuration

Create `.env` file from template:
```bash
cp .env.example .env
```

Key variables:
```properties
SERVER_PORT=8080
START_URLS=https://example.com
LOG_LEVEL=INFO
ML_MODEL_PATH=/app/models/model.pth
```

**Security**: Never commit `.env` to git!

## Architecture

### Multi-Stage Docker Builds
- **Builder stage**: Compiles code, installs build tools
- **Runtime stage**: Only artifacts and runtime dependencies
- **Result**: 50-70% smaller images, faster startup

### Services
- **complex-calculator**: Java 17 CLI for complex number arithmetic operations
- **async-web-crawler**: Python 3.12 async web scraper with URL validation and CSV export
- **integration-tests**: Python 3.10 test environment for CI/CD pipelines
- **devops-container**: Ubuntu 24.04 dev environment with SSH, code-server, and tools

## Customization

### Adding Environment Variables

1. Update `.env.example`:
```properties
MY_NEW_VAR=default_value
```

2. Update Dockerfile:
```dockerfile
ENV MY_NEW_VAR=${MY_NEW_VAR:-default_value}
```

3. Update application code to use `$MY_NEW_VAR`

### Adding Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
```

## Monitoring

### Check Container Health
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### View Logs
```bash
docker logs -f <container-name>
```

### Performance Metrics
```bash
docker stats
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port already in use | Change `8080` in `.env` to different port |
| Permission denied | Run `chmod +x scripts/*.sh` |
| Out of memory | Increase `mem_limit` in docker-compose.yml |
| Container won't start | Check logs: `docker logs <name>` |

See [DEPLOYMENT.md](./DEPLOYMENT.md#troubleshooting) for more.

## Improvements from Review

Security:
- Removed `sudo ALL=(ALL)` (excessive privileges)
- Pinned all Python package versions
- Fixed misleading health checks
- Added environment validation

Quality:
- Added 20+ unit tests for Calculator
- Added configuration support
- Comprehensive CI/CD pipeline
- Security scanning (Trivy, Dependency-Check)

Observability:
- Structured logging with proper levels
- Concurrency limits and timeouts
- Resource limits (memory, CPU)

## Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

**Note**: All PRs trigger CI/CD pipeline (tests, security scans, etc)

## Testing Locally

Before pushing, test locally:

```bash
# Run CI/CD checks
docker build -t complex-calculator:test Calculator_java_docker/

# Run security scan
trivy image complex-calculator:test

# Check for secrets
git diff --cached | grep -i "password\|token\|secret"

# Lint Python
cd async-web-crawler
docker run --rm -v $(pwd):/app python:3.12-slim bash -c "pip install flake8 && flake8 /app/*.py"
```

## Security Reporting

Found a security issue? **Don't open a public issue**.

Contact: pk

Please include:
- Description of vulnerability
- Steps to reproduce
- Suggested fix (if known)

## License

[Specify your license here]

## Acknowledgments

- [Docker Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [OWASP Container Security](https://cheatsheetseries.owasp.org/cheatsheets/Container_Security_Cheat_Sheet.html)

## Support

- **Issues**: Open GitHub issue for bugs
- **Documentation**: See individual README files in each container directory
- **Quick Start**: See [QUICKSTART.md](./QUICKSTART.md)
- **Architecture**: See [ADR.md](./ADR.md)

---

**Last Updated**: 2026-01-17  
**Author**: pk  
**Status**: Active Development
