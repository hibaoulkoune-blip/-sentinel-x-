# Sentinel-X

### Intelligent Infrastructure Monitoring & Incident Management Platform

> Status: **Phase 0 — Architecture & Foundation.** This is not the finished
> product; it is the first implemented milestone of a larger, incrementally
> built platform. See `docs/architecture.md` (added as phases progress) for
> the full system design.

## What is Sentinel-X?

Sentinel-X monitors HTTP/API/TCP endpoints, detects failures and
degradation, generates alerts, manages incidents end-to-end, and surfaces
all of it through a dashboard — with an AI assistant to help triage
incidents. Full vision and phase roadmap live in the project's master
planning document.

## Current capabilities (Phase 0)

- FastAPI application skeleton
- Centralized, typed configuration (`app/core/config.py`)
- Structured logging foundation
- `GET /` and `GET /api/v1/health`
- Test foundation (`pytest` + `httpx` async client against the app)

Everything else in the final vision (monitoring engine, metrics, anomaly
detection, alerting, incidents, auth/RBAC, React dashboard, AI assistant,
Docker, CI/CD) is **planned, not yet implemented** — it will land in later
phases. Nothing in this repo simulates functionality that isn't real yet.

## Tech stack (backend, so far)

- Python 3.12+
- FastAPI
- Pydantic / pydantic-settings
- SQLAlchemy 2.x + Alembic (installed, not yet wired to a live DB)
- pytest / pytest-asyncio / httpx

## Getting started

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp ../.env.example ../.env       # then edit values as needed

uvicorn app.main:app --reload
```

Visit:
- http://127.0.0.1:8000/ 
- http://127.0.0.1:8000/api/v1/health
- http://127.0.0.1:8000/docs (interactive API docs)

## Running tests

```bash
cd backend
pytest -v
```

## Roadmap

See the full 20-phase plan (monitoring engine → scheduler → metrics →
anomaly detection → alerting → incidents → auth/RBAC → dashboard →
security hardening → Docker/CI-CD → self-observability → AI assistant →
scalability → production hardening) in the project planning doc.
