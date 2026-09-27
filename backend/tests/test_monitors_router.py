from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import app.api.v1.monitors as monitors_router


@pytest.mark.asyncio
async def test_get_monitor_not_found_direct(monkeypatch):
    fake_db = object()

    monkeypatch.setattr(
        monitors_router.service,
        "get_monitor",
        AsyncMock(return_value=None),
    )

    with pytest.raises(monitors_router.HTTPException) as exc:
        await monitors_router.get_monitor(
            "00000000-0000-0000-0000-000000000001",
            fake_db,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Monitor not found"


@pytest.mark.asyncio
async def test_check_monitor_not_found_direct(monkeypatch):
    fake_db = object()

    monkeypatch.setattr(
        monitors_router.service,
        "get_monitor",
        AsyncMock(return_value=None),
    )

    with pytest.raises(monitors_router.HTTPException) as exc:
        await monitors_router.check_monitor(
            "00000000-0000-0000-0000-000000000001",
            fake_db,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Monitor not found"


@pytest.mark.asyncio
async def test_check_monitor_success_direct(monkeypatch):
    fake_db = SimpleNamespace(
        add=lambda obj: None,
        commit=AsyncMock(),
    )

    monitor = SimpleNamespace(
        id="00000000-0000-0000-0000-000000000001",
        url="https://example.com",
        timeout_seconds=10,
    )

    result = SimpleNamespace(
        status="UP",
        status_code=200,
        response_time_ms=123.45,
        error=None,
    )

    monkeypatch.setattr(
        monitors_router.service,
        "get_monitor",
        AsyncMock(return_value=monitor),
    )

    monkeypatch.setattr(
        monitors_router,
        "check_url",
        AsyncMock(return_value=result),
    )

    response = await monitors_router.check_monitor(
        monitor.id,
        fake_db,
    )

    assert str(response.monitor_id) == monitor.id
    assert response.status == "UP"
    assert response.status_code == 200
    assert response.response_time_ms == 123.45
    assert response.error is None

    fake_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_check_history_not_found_direct(monkeypatch):
    fake_db = object()

    monkeypatch.setattr(
        monitors_router.service,
        "get_monitor",
        AsyncMock(return_value=None),
    )

    with pytest.raises(monitors_router.HTTPException) as exc:
        await monitors_router.get_check_history(
            "00000000-0000-0000-0000-000000000001",
            fake_db,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Monitor not found"


@pytest.mark.asyncio
async def test_get_check_history_success_direct(monkeypatch):
    monitor_id = "00000000-0000-0000-0000-000000000001"

    monitor = SimpleNamespace(
        id=monitor_id,
    )

    check = SimpleNamespace(
        monitor_id=monitor_id,
        status="UP",
        status_code=200,
        response_time_ms=100.0,
        error=None,
    )

    scalars = SimpleNamespace(
        all=lambda: [check],
    )

    result = SimpleNamespace(
        scalars=lambda: scalars,
    )

    fake_db = SimpleNamespace(
        execute=AsyncMock(return_value=result),
    )

    monkeypatch.setattr(
        monitors_router.service,
        "get_monitor",
        AsyncMock(return_value=monitor),
    )

    response = await monitors_router.get_check_history(
        monitor_id,
        fake_db,
    )

    assert response == [check]

    fake_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_monitor_not_found_direct(monkeypatch):
    fake_db = object()
    data = SimpleNamespace()

    monkeypatch.setattr(
        monitors_router.service,
        "get_monitor",
        AsyncMock(return_value=None),
    )

    with pytest.raises(monitors_router.HTTPException) as exc:
        await monitors_router.update_monitor(
            "00000000-0000-0000-0000-000000000001",
            data,
            fake_db,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Monitor not found"


@pytest.mark.asyncio
async def test_update_monitor_success_direct(monkeypatch):
    fake_db = object()

    monitor = SimpleNamespace(
        id="monitor-1",
    )

    data = SimpleNamespace()

    updated_monitor = SimpleNamespace(
        id="monitor-1",
        name="Updated Monitor",
    )

    monkeypatch.setattr(
        monitors_router.service,
        "get_monitor",
        AsyncMock(return_value=monitor),
    )

    monkeypatch.setattr(
        monitors_router.service,
        "update_monitor",
        AsyncMock(return_value=updated_monitor),
    )

    response = await monitors_router.update_monitor(
        monitor.id,
        data,
        fake_db,
    )

    assert response == updated_monitor


@pytest.mark.asyncio
async def test_delete_monitor_not_found_direct(monkeypatch):
    fake_db = object()

    monkeypatch.setattr(
        monitors_router.service,
        "get_monitor",
        AsyncMock(return_value=None),
    )

    with pytest.raises(monitors_router.HTTPException) as exc:
        await monitors_router.delete_monitor(
            "00000000-0000-0000-0000-000000000001",
            fake_db,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Monitor not found"


@pytest.mark.asyncio
async def test_delete_monitor_success_direct(monkeypatch):
    fake_db = object()

    monitor = SimpleNamespace(
        id="monitor-1",
    )

    monkeypatch.setattr(
        monitors_router.service,
        "get_monitor",
        AsyncMock(return_value=monitor),
    )

    delete_mock = AsyncMock()

    monkeypatch.setattr(
        monitors_router.service,
        "delete_monitor",
        delete_mock,
    )

    result = await monitors_router.delete_monitor(
        monitor.id,
        fake_db,
    )

    assert result is None

    delete_mock.assert_awaited_once_with(
        fake_db,
        monitor,
    )
@pytest.mark.asyncio
async def test_get_monitor_success_direct(monkeypatch):
    fake_db = object()

    monitor = SimpleNamespace(
        id="00000000-0000-0000-0000-000000000001",
        name="Example Monitor",
        url="https://example.com",
    )

    monkeypatch.setattr(
        monitors_router.service,
        "get_monitor",
        AsyncMock(return_value=monitor),
    )

    response = await monitors_router.get_monitor(
        monitor.id,
        fake_db,
    )

    assert response == monitor