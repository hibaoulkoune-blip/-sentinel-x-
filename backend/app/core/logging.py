"""
Logging foundation.

WHY THIS FILE EXISTS
---------------------
An observability platform that can't observe itself properly is a bad look
(and a bad tool). We set up structured, leveled logging from Phase 0 so that
every later subsystem (monitoring engine, alert engine, scheduler, etc.)
just calls `get_logger(__name__)` instead of reinventing logging config.

This is intentionally simple right now (stdlib logging, readable format).
It can be swapped for structured JSON logging later (Phase 16 —
self-observability) without touching any call site, because every module
only ever imports `get_logger`.
"""

import logging
import sys

from app.core.config import get_settings


def configure_logging() -> None:
    """Configure the root logger once, at application startup."""
    settings = get_settings()

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger. Use `get_logger(__name__)` at call sites."""
    return logging.getLogger(name)
