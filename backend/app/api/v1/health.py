"""
Health check endpoint.

WHY THIS FILE EXISTS
---------------------
`/health` is the very first real endpoint of any production service. It
proves the process is up and able to serve HTTP. It intentionally does NOT
check the database yet (that arrives with `/ready` in Phase 16, once there
is a database connection to check) — `/health` and `/ready` are different
concepts:

  /health -> "is this process alive?"      (liveness)
  /ready  -> "can this process serve traffic right now?" (readiness,
             e.g. DB reachable, migrations applied)

Conflating the two is a common mistake that causes orchestrators
(Kubernetes, Docker healthchecks, etc.) to restart healthy-but-not-yet-ready
processes. We keep them separate from the start.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        environment=settings.ENVIRONMENT,
    )
