from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.incidents.models import Incident
from app.incidents.schemas import IncidentCreate, IncidentUpdate


async def create_incident(
    db: AsyncSession,
    data: IncidentCreate,
) -> Incident:
    incident = Incident(
        monitor_id=data.monitor_id,
        title=data.title,
        description=data.description,
        severity=data.severity,
        status="OPEN",
    )

    db.add(incident)
    await db.commit()
    await db.refresh(incident)

    return incident


async def create_incident_from_failure(
    db: AsyncSession,
    monitor_id: UUID,
    monitor_name: str,
    error: str | None = None,
) -> Incident | None:
    """Create an incident only if no OPEN incident exists."""

    result = await db.execute(
        select(Incident)
        .where(
            Incident.monitor_id == monitor_id,
            Incident.status == "OPEN",
        )
        .order_by(Incident.opened_at.desc())
    )

    existing_incident = result.scalars().first()

    if existing_incident is not None:
        return None

    incident = Incident(
        monitor_id=monitor_id,
        title=f"Service unavailable: {monitor_name}",
        description=error or "Monitoring check failed.",
        status="OPEN",
        severity="HIGH",
    )

    db.add(incident)
    await db.commit()
    await db.refresh(incident)

    return incident


async def resolve_open_incident(
    db: AsyncSession,
    monitor_id: UUID,
) -> Incident | None:
    """Resolve the active incident when the service recovers."""

    result = await db.execute(
        select(Incident)
        .where(
            Incident.monitor_id == monitor_id,
            Incident.status == "OPEN",
        )
        .order_by(Incident.opened_at.desc())
    )

    incident = result.scalars().first()

    if incident is None:
        return None

    incident.status = "RESOLVED"
    incident.resolved_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(incident)

    return incident


async def get_incident(
    db: AsyncSession,
    incident_id: UUID,
) -> Incident | None:
    return await db.get(Incident, incident_id)


async def list_incidents(
    db: AsyncSession,
) -> list[Incident]:
    result = await db.execute(
        select(Incident).order_by(
            Incident.opened_at.desc()
        )
    )

    return list(result.scalars().all())


async def update_incident(
    db: AsyncSession,
    incident: Incident,
    data: IncidentUpdate,
) -> Incident:
    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(incident, field, value)

    if incident.status == "RESOLVED" and incident.resolved_at is None:
        incident.resolved_at = datetime.now(timezone.utc)

    elif incident.status != "RESOLVED":
        incident.resolved_at = None

    await db.commit()
    await db.refresh(incident)

    return incident


async def delete_incident(
    db: AsyncSession,
    incident: Incident,
) -> None:
    await db.delete(incident)
    await db.commit()