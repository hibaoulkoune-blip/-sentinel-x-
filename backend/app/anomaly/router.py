from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.anomaly.models import Anomaly
from app.anomaly.schemas import AnomalyResponse
from app.database.session import get_db


router = APIRouter(
    prefix="/anomalies",
    tags=["Anomalies"],
)


@router.get(
    "",
    response_model=list[AnomalyResponse],
)
async def list_anomalies(
    monitor_id: UUID | None = Query(
        default=None,
        description="Filter anomalies by monitor ID.",
    ),
    severity: str | None = Query(
        default=None,
        description="Filter anomalies by severity.",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    db: AsyncSession = Depends(get_db),
) -> list[Anomaly]:
    """Return detected anomalies."""

    query = select(Anomaly).order_by(
        Anomaly.detected_at.desc()
    )

    if monitor_id is not None:
        query = query.where(
            Anomaly.monitor_id == monitor_id
        )

    if severity is not None:
        query = query.where(
            Anomaly.severity == severity.upper()
        )

    query = query.limit(limit)

    result = await db.execute(query)

    return list(result.scalars().all())