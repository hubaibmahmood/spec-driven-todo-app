# Docker Security Checklist - Backend Service

## ✅ Completed Security Measures

### Image Security

- [x] **Minimal base image**: Using `python:3.12-slim` (~150MB) instead of full image (~900MB)
- [x] **Multi-stage build**: Separates build tools from runtime image
- [x] **Layer optimization**: Dependencies installed before application code for better caching
- [x] **No hardcoded secrets**: All secrets passed via environment variables

### User Security

- [x] **Non-root user**: Application runs as `appuser` (UID 1000)
- [x] **Proper ownership**: All application files owned by `appuser:appuser`
- [x] **User switching**: `USER appuser` directive in Dockerfile

### Build Security

- [x] **Comprehensive .dockerignore**: Excludes sensitive files (.env, .git, credentials)
- [x] **Clean apt cache**: `rm -rf /var/lib/apt/lists/*` after package installation
- [x] **No cache for pip**: `pip install --no-cache-dir` reduces image size and attack surface

### Runtime Security

- [x] **Health checks**: Container health monitored via `/health` endpoint
- [x] **Resource limits**: Can be set via docker-compose or orchestrator
- [x] **Read-only filesystem**: Can be enabled with `read_only: true` in docker-compose
- [x] **No privileged mode**: Container runs without elevated privileges

### Network Security

- [x] **Isolated network**: Services communicate via `todo-network` bridge
- [x] **Port exposure**: Only necessary ports exposed (8000 for API)
- [x] **CORS configuration**: Controlled via `CORS_ORIGINS` environment variable

## 🔐 Production Hardening Recommendations

### 1. Use Secrets Management

❌ **Don't do this:**
```yaml
environment:
  DATABASE_URL: postgresql://user:password@host/db
```

✅ **Do this instead:**
```yaml
secrets:
  - db_password
environment:
  DATABASE_URL_FILE: /run/secrets/db_password
```

### 2. Enable Read-Only Filesystem

```yaml
services:
  backend:
    read_only: true
    tmpfs:
      - /tmp
```

### 3. Set Resource Limits

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 4. Drop Unnecessary Capabilities

```yaml
services:
  backend:
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
```

### 5. Use Vulnerability Scanning

```bash
# Scan image with Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image todo-backend:latest

# Scan with Docker Scout
docker scout cves todo-backend:latest
```

### 6. Enable Content Trust

```bash
# Enable Docker Content Trust
export DOCKER_CONTENT_TRUST=1

# Build and push signed images
docker build -t registry.example.com/todo-backend:latest .
docker push registry.example.com/todo-backend:latest
```

### 7. Network Isolation

```yaml
services:
  backend:
    networks:
      - frontend-network
      - backend-network

  postgres:
    networks:
      - backend-network  # Not exposed to frontend

networks:
  frontend-network:
  backend-network:
    internal: true  # No external access
```

## 📋 Pre-Deployment Checklist

Before deploying to production:

- [ ] Generate unique secrets for `SESSION_HASH_SECRET`, `SERVICE_AUTH_TOKEN`, `ENCRYPTION_KEY`
- [ ] Store secrets in secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)
- [ ] Update `CORS_ORIGINS` to match production frontend domain
- [ ] Use managed database service (Neon, RDS, Cloud SQL) instead of container PostgreSQL
- [ ] Use managed Redis service (Upstash, ElastiCache) instead of container Redis
- [ ] Enable HTTPS/TLS for all connections
- [ ] Configure log aggregation (CloudWatch, Datadog, etc.)
- [ ] Set up monitoring and alerting (Prometheus, Grafana)
- [ ] Implement rate limiting at reverse proxy level (Nginx, CloudFlare)
- [ ] Enable automated security updates for base image
- [ ] Configure backup strategy for database
- [ ] Test disaster recovery procedures

## 🔍 Security Audit Commands

```bash
# Check for running processes as root
docker-compose exec backend ps aux | grep root

# Verify file ownership
docker-compose exec backend ls -la /app

# Check exposed ports
docker-compose ps

# Inspect security options
docker inspect todo-backend-api | grep -A 10 SecurityOpt

# Check image layers for secrets
docker history todo-backend:latest --no-trunc

# Scan for vulnerabilities
docker scan todo-backend:latest
```

## 📚 Security Best Practices References

- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [Snyk Container Security Best Practices](https://snyk.io/learn/container-security/)
- [Docker Security Documentation](https://docs.docker.com/engine/security/)

## ⚠️ Known Limitations

1. **Development secrets**: Default docker-compose.yml uses placeholder secrets - NEVER use in production
2. **Volume mounts**: Source code mounted for hot reload - disable in production
3. **Database persistence**: Container volumes should be backed up regularly
4. **No TLS termination**: Use reverse proxy (Nginx, Traefik) for HTTPS

## 🛡️ Compliance Considerations

For regulated industries (HIPAA, PCI-DSS, SOC 2):

- Enable audit logging for all API requests
- Encrypt sensitive data at rest (already done via `ENCRYPTION_KEY`)
- Implement data retention policies
- Use immutable infrastructure (rebuild containers instead of patching)
- Regular security assessments and penetration testing
- Document security controls and procedures

## 🚨 Incident Response

If security incident detected:

1. **Isolate**: `docker-compose stop backend`
2. **Preserve**: `docker commit todo-backend-api forensic-backup`
3. **Investigate**: `docker logs todo-backend-api > incident-logs.txt`
4. **Remediate**: Rebuild from known-good image
5. **Rotate secrets**: Generate new `SESSION_HASH_SECRET`, `SERVICE_AUTH_TOKEN`, etc.
6. **Document**: Record incident details and remediation steps

## ✅ Verification

Run this script to verify security configuration:

```bash
#!/bin/bash
echo "🔍 Docker Security Verification"
echo "================================"

# Check non-root user
echo "✓ Checking non-root user..."
docker-compose exec -T backend whoami | grep -q appuser && echo "  ✅ Running as appuser" || echo "  ❌ Running as root!"

# Check health check
echo "✓ Checking health endpoint..."
curl -f http://localhost:8000/health > /dev/null 2>&1 && echo "  ✅ Health check passed" || echo "  ⚠️  Health check failed"

# Check exposed ports
echo "✓ Checking exposed ports..."
docker-compose ps backend | grep -q "0.0.0.0:8000" && echo "  ✅ Only port 8000 exposed" || echo "  ⚠️  Port configuration issue"

# Check database connection
echo "✓ Checking database connection..."
docker-compose exec -T postgres psql -U postgres -d todo_db -c "SELECT 1;" > /dev/null 2>&1 && echo "  ✅ Database connection OK" || echo "  ❌ Database connection failed"

echo ""
echo "✅ Security verification complete!"
```

Save as `verify-security.sh`, make executable with `chmod +x verify-security.sh`, and run.
