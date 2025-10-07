# EcoTrack API (EcoTrack Ghana)

Backend API for EcoTrack Ghana — an environmental tracking application built with FastAPI and SQLAlchemy.

This repository contains the FastAPI backend, database models, Alembic migrations and utility scripts used during development and deployment.

## Quick overview
- Framework: FastAPI
- ASGI server (dev): Uvicorn
- Production server (recommended): Gunicorn + Uvicorn workers
- ORM: SQLAlchemy 2.x
- Migrations: Alembic
- Database: PostgreSQL (recommended); SQLite is used as a local fallback

## Getting started (local development)

Prerequisites:
- Python 3.11+
- pip
- (Optional) PostgreSQL for local testing

1) Create and activate a virtual environment (PowerShell example):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

2) Copy the example env file and fill in values (do NOT commit secrets):

```powershell
copy .env.example .env
# edit .env and set DATABASE_URL, JWT_SECRET_KEY, etc.
```

3) Run migrations (Alembic) and start the app in dev mode:

```powershell
# Run migrations
alembic upgrade head

# Start development server (reload enabled when DEBUG)
python -m uvicorn main:app --reload --port 8000
```

4) Visit the health endpoint:

```
GET http://localhost:8000/health
```

## Production (containerized)

We provide a production-oriented Docker setup. The image uses `requirements.production.txt` and an entrypoint that runs Alembic (optional) then starts Gunicorn with Uvicorn workers.

Build and run (PowerShell example):

```powershell
docker build -t ecotrack-api:prod .

docker run -d -p 8000:8000 --name ecotrack-api `
  -e DATABASE_URL="postgresql://user:password@host:5432/dbname" `
  -e JWT_SECRET_KEY="super-secret-value" `
  -e ENVIRONMENT=production `
  --restart unless-stopped `
  ecotrack-api:prod
```

Notes:
- Prefer injecting secrets via your platform (Kubernetes Secrets, Docker Secrets, Render/Heroku config vars), not baked into images.
- You can disable automatic migrations in the container entrypoint if you prefer running migrations from CI/CD.

## Environment variables
Create `.env` from `.env.example`. Important variables:

- DATABASE_URL: PostgreSQL connection string (postgresql://user:pass@host:port/dbname)
- JWT_SECRET_KEY: secret used to sign JWT access tokens
- JWT_ACCESS_TOKEN_EXPIRE_MINUTES: token expiry in minutes
- ENVIRONMENT: `development`|`production`
- ENABLE_DOCS: `true` to enable OpenAPI docs in non-development environments
- ENABLE_ADMIN: `true` to enable admin routes in non-development environments
- ALLOWED_ORIGINS: comma-separated list for CORS
- GUNICORN_WORKERS: number of Gunicorn workers (production)

Never commit secrets to the repository. Use `.env.example` for templates only.

## Database migrations

This project uses Alembic. Typical workflow:

```powershell
# Create a new revision (autogenerate)
alembic revision --autogenerate -m "Add something"

# Apply migrations
alembic upgrade head
```

If you run migrations in containers, the provided `docker-entrypoint.sh` runs `alembic upgrade head` when a `DATABASE_URL` is present. For production, consider running migrations as a separate CI/CD step.

## Tests

Tests are executed with `pytest`. To run tests:

```powershell
pip install -r requirements.txt
pytest -q
```

If tests ever need secrets, use environment variables or a dedicated test configuration and avoid hard-coding credentials.

## Security & secrets

- Do not commit `.env` or files containing secrets. `.gitignore` already excludes common `.env` patterns.
- If secrets were accidentally committed, rotate them immediately and consider purging history with `git-filter-repo` or the BFG repo-cleaner (force push required).
- Keep `ENABLE_DOCS=false` in production and set explicit `ALLOWED_ORIGINS`.

## CI / CD checklist (recommended)

- Run linters and type checks (ruff / mypy) on pull requests
- Run unit and integration tests (pytest)
- Build the production Docker image in CI
- Apply migrations in a controlled deployment step (CI job) or use a migration job in orchestrator
- Deploy container image to your platform (Render, Kubernetes, ECS, etc.)

## Removing sensitive or unused files

- Use `.dockerignore` to exclude tests, local DB files and `.env` from Docker build context.
- To remove a file from future commits: `git rm <file> && git commit -m "chore: remove <file>"`
- To purge files from git history (destructive): use `git-filter-repo` or BFG — coordinate with your team and create a backup branch first.

## Contributing

Pull requests are welcome. Please:

- Open an issue for big changes before implementing
- Add/modify tests for new features
- Keep secrets out of the repo — use `.env.example` for templates

## License

Specify your license here (e.g. MIT). If you want, I can add a `LICENSE` file.

---

If you want, I can:
- add a short `CONTRIBUTING.md` with PR checklist
- open a GitHub Actions workflow to run tests and build the production image
- redact any secrets I found and commit the redaction

Tell me which of these you'd like next.
