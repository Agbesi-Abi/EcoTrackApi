Production Docker image notes

1) Build the image locally (example):

```powershell
docker build -t ecotrack-api:prod .
```

2) Run with environment variables (example):

```powershell
docker run -d -p 8000:8000 --name ecotrack-api \
  -e DATABASE_URL="postgresql://user:password@host:5432/db" \
  -e ENVIRONMENT=production \
  --restart unless-stopped \
  ecotrack-api:prod
```

Notes and recommendations:
- Ensure `DATABASE_URL` points to a managed Postgres instance. Do not embed secrets in images.
- Use an orchestration runtime (Docker Compose, Kubernetes, Render, etc.) for production.
- Configure monitoring (Sentry), a centralized log collector, and regular backups for the database.
- Consider running migrations out-of-band in CI/CD instead of in the container entrypoint if you need strict control over migrations.

Health & readiness:
- The container exposes `/health` and the Docker HEALTHCHECK pings it.
- For readiness in orchestrators, prefer a TCP or HTTP readiness probe against `/health`.
