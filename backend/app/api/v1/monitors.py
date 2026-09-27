from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.checks.models import Check
from app.checks.schemas import CheckResponse
from app.database.dependencies import get_db
from app.monitors import service
from app.monitors.checker import check_url
from app.monitors.schemas import (
    MonitorCheckResponse,
    MonitorCreate,
    MonitorResponse,
    MonitorUpdate,
)


router = APIRouter(
    prefix="/monitors",
    tags=["monitors"],
)


@router.post(
    "",
    response_model=MonitorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_monitor(
    data: MonitorCreate,
    db: AsyncSession = Depends(get_db),
) -> MonitorResponse:
    return await service.create_monitor(db, data)


@router.get(
    "",
    response_model=list[MonitorResponse],
)
async def list_monitors(
    db: AsyncSession = Depends(get_db),
) -> list[MonitorResponse]:
    return await service.get_monitors(db)


@router.get(
    "/{monitor_id}",
    response_model=MonitorResponse,
)
async def get_monitor(
    monitor_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> MonitorResponse:
    monitor = await service.get_monitor(db, monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        )

    return monitor


@router.post(
    "/{monitor_id}/check",
    response_model=MonitorCheckResponse,
)
async def check_monitor(
    monitor_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> MonitorCheckResponse:
    monitor = await service.get_monitor(db, monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        )

    result = await check_url(
        url=monitor.url,
        timeout_seconds=monitor.timeout_seconds,
    )

    # Save the check result in the database
    check = Check(
        monitor_id=monitor.id,
        status=result.status,
        status_code=result.status_code,
        response_time_ms=result.response_time_ms,
        error=result.error,
    )

    db.add(check)
    await db.commit()

    return MonitorCheckResponse(
        monitor_id=monitor.id,
        status=result.status,
        status_code=result.status_code,
        response_time_ms=result.response_time_ms,
        error=result.error,
    )


@router.get(
    "/{monitor_id}/checks",
    response_model=list[CheckResponse],
)
async def get_check_history(
    monitor_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[CheckResponse]:
    monitor = await service.get_monitor(db, monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        )

    result = await db.execute(
        select(Check)
        .where(Check.monitor_id == monitor_id)
        .order_by(Check.checked_at.desc())
    )

    return list(result.scalars().all())


@router.patch(
    "/{monitor_id}",
    response_model=MonitorResponse,
)
async def update_monitor(
    monitor_id: UUID,
    data: MonitorUpdate,
    db: AsyncSession = Depends(get_db),
) -> MonitorResponse:
    monitor = await service.get_monitor(db, monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        )

    return await service.update_monitor(db, monitor, data)


@router.delete(
    "/{monitor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_monitor(
    monitor_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    monitor = await service.get_monitor(db, monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        )

    await service.delete_monitor(db, monitor)