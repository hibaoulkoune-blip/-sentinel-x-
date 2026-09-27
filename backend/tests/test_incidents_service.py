from types import SimpleNamespace
from uuid import uuid4

import pytest

import app.incidents.service as incident_service


class FakeScalarResult:
    def __init__(self, value):
        self.value = value

    def first(self):
        return self.value

    def all(self):
        if isinstance(self.value, list):
            return self.value
        return [self.value]


class FakeExecuteResult:
    def __init__(self, value):
        self.value = value

    def scalars(self):
        return FakeScalarResult(self.value)


class FakeDB:
    def __init__(self, execute_value=None, get_value=None):
        self.execute_value = execute_value
        self.get_value = get_value

        self.added = []
        self.deleted = []
        self.committed = False
        self.refreshed = False

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        self.refreshed = True

    async def execute(self, statement):
        return FakeExecuteResult(self.execute_value)

    async def get(self, model, object_id):
        return self.get_value

    async def delete(self, obj):
        self.deleted.append(obj)


def make_incident(
    *,
    status="OPEN",
    resolved_at=None,
):
    return SimpleNamespace(
        id=uuid4(),
        monitor_id=uuid4(),
        title="Test Incident",
        description="Test description",
        severity="HIGH",
        status=status,
        resolved_at=resolved_at,
    )


@pytest.mark.asyncio
async def test_create_incident():
    monitor_id = uuid4()

    data = SimpleNamespace(
        monitor_id=monitor_id,
        title="Server Down",
        description="Server unavailable",
        severity="HIGH",
    )

    db = FakeDB()

    incident = await incident_service.create_incident(
        db=db,
        data=data,
    )

    assert len(db.added) == 1

    created = db.added[0]

    assert created.monitor_id == monitor_id
    assert created.title == "Server Down"
    assert created.description == "Server unavailable"
    assert created.severity == "HIGH"
    assert created.status == "OPEN"

    assert incident is created
    assert db.committed is True
    assert db.refreshed is True


@pytest.mark.asyncio
async def test_create_incident_from_failure_existing_incident():
    monitor_id = uuid4()

    existing_incident = make_incident()

    db = FakeDB(
        execute_value=existing_incident,
    )

    result = await incident_service.create_incident_from_failure(
        db=db,
        monitor_id=monitor_id,
        monitor_name="Test Monitor",
        error="Connection failed",
    )

    assert result is None
    assert db.added == []
    assert db.committed is False


@pytest.mark.asyncio
async def test_create_incident_from_failure_new_incident_with_error():
    monitor_id = uuid4()

    db = FakeDB(
        execute_value=None,
    )

    result = await incident_service.create_incident_from_failure(
        db=db,
        monitor_id=monitor_id,
        monitor_name="Production API",
        error="Connection timeout",
    )

    assert result is db.added[0]

    incident = db.added[0]

    assert incident.monitor_id == monitor_id
    assert incident.title == "Service unavailable: Production API"
    assert incident.description == "Connection timeout"
    assert incident.status == "OPEN"
    assert incident.severity == "HIGH"

    assert db.committed is True
    assert db.refreshed is True


@pytest.mark.asyncio
async def test_create_incident_from_failure_default_error():
    monitor_id = uuid4()

    db = FakeDB(
        execute_value=None,
    )

    result = await incident_service.create_incident_from_failure(
        db=db,
        monitor_id=monitor_id,
        monitor_name="Payment API",
        error=None,
    )

    assert result is db.added[0]

    incident = db.added[0]

    assert incident.description == "Monitoring check failed."
    assert incident.status == "OPEN"


@pytest.mark.asyncio
async def test_resolve_open_incident_not_found():
    monitor_id = uuid4()

    db = FakeDB(
        execute_value=None,
    )

    result = await incident_service.resolve_open_incident(
        db=db,
        monitor_id=monitor_id,
    )

    assert result is None
    assert db.committed is False
    assert db.refreshed is False


@pytest.mark.asyncio
async def test_resolve_open_incident_success():
    monitor_id = uuid4()

    incident = make_incident()

    db = FakeDB(
        execute_value=incident,
    )

    result = await incident_service.resolve_open_incident(
        db=db,
        monitor_id=monitor_id,
    )

    assert result is incident
    assert incident.status == "RESOLVED"
    assert incident.resolved_at is not None

    assert db.committed is True
    assert db.refreshed is True


@pytest.mark.asyncio
async def test_get_incident():
    incident_id = uuid4()

    incident = make_incident()

    db = FakeDB(
        get_value=incident,
    )

    result = await incident_service.get_incident(
        db=db,
        incident_id=incident_id,
    )

    assert result is incident


@pytest.mark.asyncio
async def test_list_incidents():
    incident_1 = make_incident()
    incident_2 = make_incident(
        status="RESOLVED",
    )

    db = FakeDB(
        execute_value=[
            incident_1,
            incident_2,
        ],
    )

    result = await incident_service.list_incidents(
        db=db,
    )

    assert result == [
        incident_1,
        incident_2,
    ]


@pytest.mark.asyncio
async def test_update_incident_resolved():
    incident = make_incident(
        status="OPEN",
        resolved_at=None,
    )

    data = SimpleNamespace(
        model_dump=lambda exclude_unset=True: {
            "status": "RESOLVED",
            "title": "Resolved Incident",
        }
    )

    db = FakeDB()

    result = await incident_service.update_incident(
        db=db,
        incident=incident,
        data=data,
    )

    assert result is incident
    assert incident.status == "RESOLVED"
    assert incident.title == "Resolved Incident"
    assert incident.resolved_at is not None

    assert db.committed is True
    assert db.refreshed is True


@pytest.mark.asyncio
async def test_update_incident_non_resolved_clears_resolved_at():
    incident = make_incident(
        status="RESOLVED",
    )

    data = SimpleNamespace(
        model_dump=lambda exclude_unset=True: {
            "status": "OPEN",
        }
    )

    db = FakeDB()

    result = await incident_service.update_incident(
        db=db,
        incident=incident,
        data=data,
    )

    assert result is incident
    assert incident.status == "OPEN"
    assert incident.resolved_at is None

    assert db.committed is True
    assert db.refreshed is True


@pytest.mark.asyncio
async def test_update_incident_resolved_already_has_timestamp():
    existing_timestamp = object()

    incident = make_incident(
        status="RESOLVED",
        resolved_at=existing_timestamp,
    )

    data = SimpleNamespace(
        model_dump=lambda exclude_unset=True: {}
    )

    db = FakeDB()

    result = await incident_service.update_incident(
        db=db,
        incident=incident,
        data=data,
    )

    assert result is incident
    assert incident.status == "RESOLVED"
    assert incident.resolved_at is existing_timestamp

    assert db.committed is True
    assert db.refreshed is True


@pytest.mark.asyncio
async def test_delete_incident():
    incident = make_incident()

    db = FakeDB()

    result = await incident_service.delete_incident(
        db=db,
        incident=incident,
    )

    assert result is None
    assert db.deleted == [incident]
    assert db.committed is True