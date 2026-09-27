import asyncio
import time
from uuid import UUID

from sqlalchemy import select

from app.anomaly.service import detect_response_time_anomaly
from app.checks.models import Check
from app.database.session import AsyncSessionLocal
from app.incidents.service import (
    create_incident_from_failure,
    resolve_open_incident,
)
from app.monitors.checker import check_url
from app.monitors.models import Monitor


async def run_monitor_check(monitor: Monitor) -> None:
    """Run one check, save the result, detect anomalies, and manage incidents."""

    print(f"[SCHEDULER] Checking monitor: {monitor.name}")

    result = await check_url(
        url=monitor.url,
        timeout_seconds=monitor.timeout_seconds,
    )

    print(
        f"[SCHEDULER] Result: "
        f"{monitor.name} -> "
        f"{result.status} "
        f"{result.status_code} "
        f"{result.response_time_ms} ms"
    )

    async with AsyncSessionLocal() as db:
        check = Check(
            monitor_id=monitor.id,
            status=result.status,
            status_code=result.status_code,
            response_time_ms=result.response_time_ms,
            error=result.error,
        )

        db.add(check)
        await db.commit()
        await db.refresh(check)

        anomaly = await detect_response_time_anomaly(
            db=db,
            monitor_id=monitor.id,
            check=check,
        )

        if anomaly is not None:
            print(
                f"[ANOMALY] Detected: "
                f"{monitor.name} "
                f"-> {anomaly.metric} "
                f"z={anomaly.z_score:.2f} "
                f"severity={anomaly.severity}"
            )

        if result.status == "DOWN":
            incident = await create_incident_from_failure(
                db=db,
                monitor_id=monitor.id,
                monitor_name=monitor.name,
                error=result.error,
            )

            if incident is not None:
                print(
                    f"[INCIDENT] OPEN: "
                    f"{monitor.name} "
                    f"-> {incident.id}"
                )
            else:
                print(
                    f"[INCIDENT] Existing OPEN incident: "
                    f"{monitor.name}"
                )

        elif result.status == "UP":
            incident = await resolve_open_incident(
                db=db,
                monitor_id=monitor.id,
            )

            if incident is not None:
                print(
                    f"[RECOVERY] RESOLVED: "
                    f"{monitor.name} "
                    f"-> {incident.id}"
                )

    print(f"[SCHEDULER] Check saved: {monitor.name}")


async def monitor_worker(monitor_id: UUID) -> None:
    """Continuously check one monitor according to its interval."""

    print(f"[WORKER] Started: {monitor_id}")

    while True:
        try:
            async with AsyncSessionLocal() as db:
                monitor = await db.get(Monitor, monitor_id)

            if monitor is None:
                print(f"[WORKER] Monitor deleted: {monitor_id}")
                return

            if not monitor.enabled:
                print(f"[WORKER] Monitor disabled: {monitor.name}")
                return

            start_time = time.monotonic()

            await run_monitor_check(monitor)

            elapsed = time.monotonic() - start_time

            wait_time = max(
                monitor.interval_seconds - elapsed,
                0,
            )

            print(
                f"[WORKER] {monitor.name} "
                f"next check in {wait_time:.2f}s"
            )

            await asyncio.sleep(wait_time)

        except asyncio.CancelledError:
            print(f"[WORKER] Cancelled: {monitor_id}")
            raise

        except Exception as exc:
            print(
                f"[WORKER] Error for {monitor_id}: {exc}"
            )

            await asyncio.sleep(5)


async def run_monitoring_loop() -> None:
    """Continuously manage workers for enabled monitors."""

    workers: dict[UUID, asyncio.Task] = {}

    print("[SCHEDULER] Monitoring loop started")

    while True:
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Monitor).where(
                        Monitor.enabled.is_(True)
                    )
                )

                monitors = list(result.scalars().all())

            active_ids = {monitor.id for monitor in monitors}

            print(
                f"[SCHEDULER] Enabled monitors: "
                f"{len(monitors)}"
            )

            for monitor in monitors:
                if monitor.id not in workers:
                    print(
                        f"[SCHEDULER] Creating worker: "
                        f"{monitor.name} "
                        f"({monitor.id})"
                    )

                    workers[monitor.id] = asyncio.create_task(
                        monitor_worker(monitor.id)
                    )

            for monitor_id in list(workers):
                if monitor_id not in active_ids:
                    print(
                        f"[SCHEDULER] Removing worker: "
                        f"{monitor_id}"
                    )

                    workers[monitor_id].cancel()

                    try:
                        await workers[monitor_id]
                    except asyncio.CancelledError:
                        pass

                    del workers[monitor_id]

            await asyncio.sleep(5)

        except asyncio.CancelledError:
            print("[SCHEDULER] Monitoring loop cancelled")

            for task in workers.values():
                task.cancel()

            await asyncio.gather(
                *workers.values(),
                return_exceptions=True,
            )

            raise

        except Exception as exc:
            print(
                f"[SCHEDULER] Manager error: {exc}"
            )

            await asyncio.sleep(5)
