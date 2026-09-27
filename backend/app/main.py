"""
Sentinel-X — FastAPI application entrypoint.

This file is responsible for:
- creating the FastAPI app
- configuring logging
- configuring CORS
- mounting the versioned API router
- starting and stopping the monitoring scheduler
- exposing the root endpoint
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.scheduler.service import run_monitoring_loop


settings = get_settings()

configure_logging()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Sentinel-X starting up in '%s' environment",
        settings.ENVIRONMENT,
    )

    scheduler_task = asyncio.create_task(
        run_monitoring_loop()
    )

    logger.info("Automatic monitoring scheduler started")

    try:
        yield
    finally:
        logger.info("Stopping automatic monitoring scheduler")

        scheduler_task.cancel()

        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass

        logger.info("Sentinel-X shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent Infrastructure Monitoring & Incident Management Platform",
    version="0.1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


@app.get("/", tags=["root"])
async def root() -> dict:
    return {
        "service": settings.APP_NAME,
        "status": "running",
        "docs": "/docs",
        "api": settings.API_V1_PREFIX,
    }