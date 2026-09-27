from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import app.anomaly.router as anomaly_router


MONITOR_ID = "00000000-0000-0000-0000-000000000001"


@pytest.mark.asyncio
async def test_list_anomalies_without_filters():
    anomaly = SimpleNamespace(
        id="00000000-0000-0000-0000-000000000002",
        monitor_id=MONITOR_ID,
        severity="HIGH",
    )

    scalars = SimpleNamespace(
        all=lambda: [anomaly],
    )

    result = SimpleNamespace(
        scalars=lambda: scalars,
    )

    fake_db = SimpleNamespace(
        execute=AsyncMock(return_value=result),
    )

    response = await anomaly_router.list_anomalies(
        monitor_id=None,
        severity=None,
        limit=50,
        db=fake_db,
    )

    assert response == [anomaly]
    fake_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_anomalies_with_monitor_filter():
    anomaly = SimpleNamespace(
        id="00000000-0000-0000-0000-000000000002",
        monitor_id=MONITOR_ID,
        severity="HIGH",
    )

    scalars = SimpleNamespace(
        all=lambda: [anomaly],
    )

    result = SimpleNamespace(
        scalars=lambda: scalars,
    )

    fake_db = SimpleNamespace(
        execute=AsyncMock(return_value=result),
    )

    response = await anomaly_router.list_anomalies(
        monitor_id=MONITOR_ID,
        severity=None,
        limit=50,
        db=fake_db,
    )

    assert response == [anomaly]
    fake_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_anomalies_with_severity_filter():
    anomaly = SimpleNamespace(
        id="00000000-0000-0000-0000-000000000002",
        monitor_id=MONITOR_ID,
        severity="HIGH",
    )

    scalars = SimpleNamespace(
        all=lambda: [anomaly],
    )

    result = SimpleNamespace(
        scalars=lambda: scalars,
    )

    fake_db = SimpleNamespace(
        execute=AsyncMock(return_value=result),
    )

    response = await anomaly_router.list_anomalies(
        monitor_id=None,
        severity="high",
        limit=10,
        db=fake_db,
    )

    assert response == [anomaly]
    fake_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_anomalies_with_all_filters():
    anomaly = SimpleNamespace(
        id="00000000-0000-0000-0000-000000000002",
        monitor_id=MONITOR_ID,
        severity="HIGH",
    )

    scalars = SimpleNamespace(
        all=lambda: [anomaly],
    )

    result = SimpleNamespace(
        scalars=lambda: scalars,
    )

    fake_db = SimpleNamespace(
        execute=AsyncMock(return_value=result),
    )

    response = await anomaly_router.list_anomalies(
        monitor_id=MONITOR_ID,
        severity="high",
        limit=5,
        db=fake_db,
    )

    assert response == [anomaly]
    fake_db.execute.assert_awaited_once()
