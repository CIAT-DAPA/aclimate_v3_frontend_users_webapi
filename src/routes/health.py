import os
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from aclimate_v3_orm_frontend.database import engine

router = APIRouter(tags=["Health"])

HEALTH_TOKEN = os.getenv("HEALTH_TOKEN", None)


def _validate_token(request: Request) -> bool:
    """Validate X-Health-Token header when HEALTH_TOKEN is configured."""
    if not HEALTH_TOKEN:
        return True
    token = request.headers.get("X-Health-Token")
    return token == HEALTH_TOKEN


@router.get("/health", include_in_schema=False)
async def health_check(request: Request):
    """
    Liveness check for container orchestration (Docker HEALTHCHECK).
    Returns immediately without external dependencies.
    Protected by optional HEALTH_TOKEN environment variable.
    """
    if not _validate_token(request):
        return JSONResponse(content=None, status_code=404)

    return {"status": "ok"}


@router.get("/ready", include_in_schema=False)
async def readiness_check(request: Request):
    """
    Readiness check for Kubernetes readiness probe.
    Verifies database connectivity and other critical dependencies.
    Returns 200 if all services are healthy, 503 otherwise.
    """
    if not _validate_token(request):
        return JSONResponse(content=None, status_code=404)

    checks = {
        "database": "disconnected"
    }

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception:
        pass

    all_healthy = all(v == "connected" for v in checks.values())
    status_code = 200 if all_healthy else 503

    return JSONResponse(content=checks, status_code=status_code)