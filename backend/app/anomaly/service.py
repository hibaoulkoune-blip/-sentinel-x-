from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.anomaly.detector import (
    calculate_z_score,
    get_severity,
    is_anomaly,
)
from app.anomaly.models import Anomaly
from app.checks.models import Check


async def detect_response_time_anomaly(
    db: AsyncSession,
    monitor_id: UUID,
    check: Check,
    history_size: int = 20,
) -> Anomaly | None:
    """
    Detect a response-time anomaly using the previous checks
    of the same monitor.
    """

    if check.response_time_ms is None:
        return None

    result = await db.execute(
        select(Check)
        .where(
            Check.monitor_id == monitor_id,
            Check.response_time_ms.is_not(None),
            Check.id != check.id,
        )
        .order_by(Check.checked_at.desc())
        .limit(history_size)
    )

    history = list(result.scalars().all())

    values = [
        item.response_time_ms
        for item in reversed(history)
        if item.response_time_ms is not None
    ]

    if len(values) < 10:
        return None

    average, standard_deviation, z_score = calculate_z_score(
        values=values,
        current_value=check.response_time_ms,
    )

    if not is_anomaly(z_score):
        return None

    anomaly = Anomaly(
        monitor_id=monitor_id,
        check_id=check.id,
        metric="response_time_ms",
        value=check.response_time_ms,
        mean=average,
        standard_deviation=standard_deviation,
        z_score=z_score,
        severity=get_severity(z_score),
    )

    db.add(anomaly)
    await db.commit()
    await db.refresh(anomaly)

    return anomaly
