from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.monitors import router as monitors_router
from app.api.v1.incidents import router as incidents_router
from app.anomaly.router import router as anomaly_router


api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(monitors_router)
api_router.include_router(incidents_router)
api_router.include_router(anomaly_router)