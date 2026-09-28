# Architecture Decision Records (ADRs)

## Overview

This document tracks significant architectural and technical decisions made in this Docker repository.

---

## ADR-001: Multi-Stage Docker Builds

**Status**: Adopted

**Context**: Container images were large, startup times were slow, and unnecessary tools cluttered production images.

**Decision**: Use multi-stage Docker builds for all projects.

**Rationale**:
- Reduces production image size by 50-70%
- Separates build dependencies from runtime
- Improves security (fewer attack surface)
- Faster startup times

**Implementation**:
- All Dockerfiles now use builder stage for compilation
- Runtime stage copies only artifacts and runtime dependencies
- Layer caching optimized for faster rebuilds

**Example**:
```dockerfile
FROM maven:3.9-eclipse-temurin-17 AS builder
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package

FROM eclipse-temurin:17-jre-alpine
COPY --from=builder /app/target/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

---

## ADR-002: Non-Root User Execution

**Status**: Adopted

**Context**: Running containers as root increases security risk of privilege escalation attacks.

**Decision**: All containers run as non-root users with minimal privileges.

**Rationale**:
- Limits blast radius of container compromise
- Reduces risk of host system access
- Industry standard (CIS Benchmarks recommend)
- Minimal performance overhead

**Implementation**:
- Create unprivileged user in Dockerfile
- Use `USER` directive before `ENTRYPOINT`
- Remove `sudo` access (use separate admin containers if needed)

**Verification**:
```bash
docker run --rm calculator:latest id  # Should show uid != 0
```

---

## ADR-003: Dependency Version Pinning

**Status**: Adopted

**Context**: Unpinned dependencies led to silent breaking changes and inconsistent builds.

**Decision**: Pin all dependencies to exact patch versions.

**Rationale**:
- Reproducible builds across environments
- Predictable security updates
- Easier rollback if issues arise
- Better compliance and auditability

**Examples**:
```
# Before (bad)
numpy
requests==2.32.*

# After (good)
numpy==2.1.0
requests==2.32.3
```

**Maintenance**:
- Monthly dependency updates via automated PRs
- Test updates before deployment
- Use Dependabot for automation

---

## ADR-004: Health Checks for All Services

**Status**: Adopted

**Context**: No way to verify if containers were actually healthy; orchestrators couldn't auto-restart failed services.

**Decision**: Implement health checks for all container services.

**Rationale**:
- Enables automatic container restart on failure
- Provides visibility into service health
- Allows orchestrators (K8s) to replace unhealthy pods
- Prevents deployment of unhealthy versions

**Implementation**:
```dockerfile
# For web services with HTTP endpoints
HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://localhost:8080/health || exit 1

# For process-based services (SSH, background jobs)
HEALTHCHECK --interval=30s --timeout=5s \
    CMD pgrep sshd || exit 1
```

Note: Calculator is a CLI app (CommandLineRunner) and doesn't run as a service.

---

## ADR-005: Environment-Based Configuration

**Status**: Adopted

**Context**: Hardcoded values required image rebuilds for different environments.

**Decision**: Use environment variables for all configurable settings.

**Rationale**:
- Build once, deploy anywhere
- Single image works for dev, staging, production
- Secrets don't get baked into images
- Follows 12-factor app methodology

**Pattern**:
```dockerfile
ENV SERVER_PORT=${SERVER_PORT:-8080}
ENV LOG_LEVEL=${LOG_LEVEL:-INFO}
```

```bash
docker run -e SERVER_PORT=9090 -e LOG_LEVEL=DEBUG calculator:latest
```

**Special Cases - Secrets**:
- **Don't use**: Regular environment variables for secrets
- **Use instead**: Docker secrets, external secret management systems

---

## ADR-006: Alpine Base Images

**Status**: Adopted

**Context**: Ubuntu images were 100+ MB; startup and security updates were slow.

**Decision**: Use Alpine Linux as base image where possible.

**Rationale**:
- Smaller image size (5-20 MB base vs 70+ MB Ubuntu)
- Faster pulls and startup
- Smaller attack surface
- Common in modern containerization

**Trade-offs**:
- Limited package availability (rarely an issue)
- Different libc implementation (musl vs glibc)
- Most popular tools have Alpine versions

**Example**:
```
Before: ubuntu:24.04 (77 MB)
After:  alpine:3.19   (7 MB)
```

**When NOT to use Alpine**:
- Complex C dependencies that need glibc
- Python packages requiring binary wheels (use python:3.12-slim instead)

---

## ADR-007: CI/CD Pipeline with GitHub Actions

**Status**: Adopted

**Context**: No automated testing, security scanning, or deployment validation.

**Decision**: Implement comprehensive GitHub Actions workflow.

**Rationale**:
- Catches bugs before production
- Automated security scanning (Trivy, Dependency-Check)
- Prevents secrets being committed
- Enforces code quality standards
- Container image signing for supply chain security

**Pipeline Stages**:
1. Security scan (dependencies, secrets)
2. Test & build (unit tests, linting)
3. Build images (multi-platform)
4. Image scanning (vulnerabilities)
5. Integration tests
6. Deploy (on merge to main)

**Benefits**:
- 100% reproducible builds
- Audit trail for compliance
- Faster feedback loop
- Automated everything (no manual steps)

---

## ADR-008: Structured Logging

**Status**: Recommended

**Context**: Logs to stdout with no structure; difficult to parse, search, or aggregate.

**Decision**: Implement structured (JSON) logging.

**Rationale**:
- Machine-readable logs
- Easy to aggregate to centralized system
- Faster debugging and analysis
- Better for containers (works with log drivers)

**Example**:
```python
import logging
import json

logging.basicConfig(
    format='%(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)
# Output: {"timestamp": "...", "level": "INFO", "message": "..."}
```

---

## ADR-009: Resource Limits

**Status**: Recommended

**Context**: Containers could consume unlimited resources, starving host or other containers.

**Decision**: Set memory and CPU limits for all containers.

**Rationale**:
- Prevents denial-of-service via resource exhaustion
- Ensures fair resource allocation
- Enables better orchestration decisions
- Provides visibility into resource usage

**Example**:
```yaml
services:
  calculator:
    mem_limit: 512m
    cpus: 1.0
```

**Setting Guidelines**:
- Memory: `requests: 256m`, `limits: 512m`
- CPU: `requests: 0.25`, `limits: 1.0`
- Monitor actual usage, then adjust

---

## ADR-010: Read-Only Filesystem

**Status**: Recommended

**Context**: Containers could be modified at runtime (code injection attacks).

**Decision**: Use read-only filesystem where possible; mount temporary directories.

**Rationale**:
- Prevents runtime modifications
- Forces all changes through proper deployment channels
- Fails fast on unexpected writes
- Industry best practice (CIS, NIST)

**Implementation**:
```yaml
security_opt:
  - no-new-privileges:true
read_only: true
tmpfs:
  - /tmp
  - /var/cache
```

**When to use**:
- Production deployments
- High-security applications
- After thorough testing (don't use in dev initially)

---

## Future Considerations

### ADR-011: Kubernetes Migration (Planned)
- Move from Docker Compose to Kubernetes for better orchestration
- Enable auto-scaling, rolling updates, service mesh

### ADR-012: Database Migration (Proposed)
- Externalize database from container
- Implement proper backup/recovery strategy
- Enable data persistence across deployments

### ADR-013: API Gateway (Proposed)
- Add API gateway for routing and rate limiting
- Implement authentication/authorization
- Provide API versioning strategy

---

## Decision Timeline

| Decision | Date | Status |
|----------|------|--------|
| ADR-001: Multi-Stage Builds | 2026-01 |  Adopted |
| ADR-002: Non-Root Users | 2026-01 |  Adopted |
| ADR-003: Version Pinning | 2026-01 |  Adopted |
| ADR-004: Health Checks | 2026-01 |  Adopted |
| ADR-005: Environment Config | 2026-01 |  Adopted |
| ADR-006: Alpine Images | 2026-01 |  Adopted |
| ADR-007: CI/CD Pipeline | 2026-01 |  Adopted |
| ADR-008: Structured Logging | 2026-01 |  Recommended |
| ADR-009: Resource Limits | 2026-01 |  Recommended |
| ADR-010: Read-Only FS | 2026-01 |  Recommended |

---

## Related Documents

- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment procedures
- [.github/workflows/ci-cd.yml](./.github/workflows/ci-cd.yml) - CI/CD implementation
- [Security Guidelines](#) - Security best practices

---
*Author: pk*

