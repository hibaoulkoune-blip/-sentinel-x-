from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import app.api.v1.incidents as incidents_router


MONITOR_ID = "00000000-0000-0000-0000-000000000001"
INCIDENT_ID = "00000000-0000-0000-0000-000000000002"


@pytest.mark.asyncio
async def test_create_incident_direct(monkeypatch):
    fake_db = object()

    data = SimpleNamespace(
        monitor_id=MONITOR_ID,
        title="Server is down",
        description="Server unavailable",
        severity="HIGH",
    )

    incident = SimpleNamespace(
        id=INCIDENT_ID,
        monitor_id=MONITOR_ID,
        title="Server is down",
        description="Server unavailable",
        severity="HIGH",
        status="OPEN",
    )

    create_mock = AsyncMock(return_value=incident)

    monkeypatch.setattr(
        incidents_router.service,
        "create_incident",
        create_mock,
    )

    response = await incidents_router.create_incident(
        data,
        fake_db,
    )

    assert response == incident

    create_mock.assert_awaited_once_with(
        fake_db,
        data,
    )


@pytest.mark.asyncio
async def test_get_incidents_direct(monkeypatch):
    fake_db = object()

    incidents = [
        SimpleNamespace(id=INCIDENT_ID),
        SimpleNamespace(id="00000000-0000-0000-0000-000000000003"),
    ]

    list_mock = AsyncMock(return_value=incidents)

    monkeypatch.setattr(
        incidents_router.service,
        "list_incidents",
        list_mock,
    )

    response = await incidents_router.get_incidents(
        fake_db,
    )

    assert response == incidents

    list_mock.assert_awaited_once_with(fake_db)


@pytest.mark.asyncio
async def test_get_incident_not_found_direct(monkeypatch):
    fake_db = object()

    monkeypatch.setattr(
        incidents_router.service,
        "get_incident",
        AsyncMock(return_value=None),
    )

    with pytest.raises(incidents_router.HTTPException) as exc:
        await incidents_router.get_incident(
            INCIDENT_ID,
            fake_db,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Incident not found"


@pytest.mark.asyncio
async def test_get_incident_success_direct(monkeypatch):
    fake_db = object()

    incident = SimpleNamespace(
        id=INCIDENT_ID,
        title="Server is down",
    )

    get_mock = AsyncMock(return_value=incident)

    monkeypatch.setattr(
        incidents_router.service,
        "get_incident",
        get_mock,
    )

    response = await incidents_router.get_incident(
        INCIDENT_ID,
        fake_db,
    )

    assert response == incident

    get_mock.assert_awaited_once_with(
        fake_db,
        INCIDENT_ID,
    )


@pytest.mark.asyncio
async def test_update_incident_not_found_direct(monkeypatch):
    fake_db = object()

    data = SimpleNamespace(
        title="Updated incident",
    )

    monkeypatch.setattr(
        incidents_router.service,
        "get_incident",
        AsyncMock(return_value=None),
    )

    with pytest.raises(incidents_router.HTTPException) as exc:
        await incidents_router.update_incident(
            INCIDENT_ID,
            data,
            fake_db,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Incident not found"


@pytest.mark.asyncio
async def test_update_incident_success_direct(monkeypatch):
    fake_db = object()

    incident = SimpleNamespace(
        id=INCIDENT_ID,
        title="Old title",
    )

    data = SimpleNamespace(
        title="Updated title",
    )

    updated_incident = SimpleNamespace(
        id=INCIDENT_ID,
        title="Updated title",
    )

    monkeypatch.setattr(
        incidents_router.service,
        "get_incident",
        AsyncMock(return_value=incident),
    )

    update_mock = AsyncMock(
        return_value=updated_incident,
    )

    monkeypatch.setattr(
        incidents_router.service,
        "update_incident",
        update_mock,
    )

    response = await incidents_router.update_incident(
        INCIDENT_ID,
        data,
        fake_db,
    )

    assert response == updated_incident

    update_mock.assert_awaited_once_with(
        fake_db,
        incident,
        data,
    )


@pytest.mark.asyncio
async def test_delete_incident_not_found_direct(monkeypatch):
    fake_db = object()

    monkeypatch.setattr(
        incidents_router.service,
        "get_incident",
        AsyncMock(return_value=None),
    )

    with pytest.raises(incidents_router.HTTPException) as exc:
        await incidents_router.delete_incident(
            INCIDENT_ID,
            fake_db,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Incident not found"


@pytest.mark.asyncio
async def test_delete_incident_success_direct(monkeypatch):
    fake_db = object()

    incident = SimpleNamespace(
        id=INCIDENT_ID,
    )

    monkeypatch.setattr(
        incidents_router.service,
        "get_incident",
        AsyncMock(return_value=incident),
    )

    delete_mock = AsyncMock()

    monkeypatch.setattr(
        incidents_router.service,
        "delete_incident",
        delete_mock,
    )

    result = await incidents_router.delete_incident(
        INCIDENT_ID,
        fake_db,
    )

    assert result is None

    delete_mock.assert_awaited_once_with(
        fake_db,
        incident,
    )