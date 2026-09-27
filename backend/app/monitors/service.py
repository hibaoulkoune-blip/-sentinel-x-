from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.monitors.models import Monitor
from app.monitors.schemas import MonitorCreate, MonitorUpdate


async def create_monitor(
    db: AsyncSession,
    data: MonitorCreate,
) -> Monitor:
    monitor = Monitor(
        name=data.name,
        url=str(data.url),
        interval_seconds=data.interval_seconds,
        timeout_seconds=data.timeout_seconds,
        enabled=data.enabled,
    )

    db.add(monitor)
    await db.commit()
    await db.refresh(monitor)

    return monitor


async def get_monitors(
    db: AsyncSession,
) -> list[Monitor]:
    result = await db.execute(
        select(Monitor).order_by(Monitor.created_at.desc())
    )

    return list(result.scalars().all())


async def get_monitor(
    db: AsyncSession,
    monitor_id: UUID,
) -> Monitor | None:
    result = await db.execute(
        select(Monitor).where(Monitor.id == monitor_id)
    )

    return result.scalar_one_or_none()


async def update_monitor(
    db: AsyncSession,
    monitor: Monitor,
    data: MonitorUpdate,
) -> Monitor:
    update_data = data.model_dump(exclude_unset=True)

    if "url" in update_data:
        update_data["url"] = str(update_data["url"])

    for field, value in update_data.items():
        setattr(monitor, field, value)

    await db.commit()
    await db.refresh(monitor)

    return monitor


async def delete_monitor(
    db: AsyncSession,
    monitor: Monitor,
) -> None:
    await db.delete(monitor)
    await db.commit()