from types import SimpleNamespace
from uuid import uuid4

import pytest

import app.monitors.service as monitor_service


class FakeScalarResult:
    def __init__(self, values):
        self.values = values

    def all(self):
        return self.values

    def scalar_one_or_none(self):
        if isinstance(self.values, list):
            if len(self.values) == 1:
                return self.values[0]
            return None

        return self.values


class FakeExecuteResult:
    def __init__(self, values):
        self.values = values

    def scalars(self):
        return FakeScalarResult(self.values)

    def scalar_one_or_none(self):
        return FakeScalarResult(self.values).scalar_one_or_none()


class FakeDB:
    def __init__(self, execute_value=None):
        self.execute_value = execute_value
        self.added = []
        self.deleted = []
        self.committed = False
        self.refreshed = False

    def add(self, obj):
        self.added.append(obj)

    async def execute(self, statement):
        return FakeExecuteResult(self.execute_value)

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        self.refreshed = True

    async def delete(self, obj):
        self.deleted.append(obj)


def make_monitor():
    return SimpleNamespace(
        id=uuid4(),
        name="Original Monitor",
        url="https://example.com",
        interval_seconds=60,
        timeout_seconds=10,
        enabled=True,
    )


@pytest.mark.asyncio
async def test_create_monitor():
    monitor_id = uuid4()

    data = SimpleNamespace(
        name="Test Monitor",
        url="https://example.com/",
        interval_seconds=30,
        timeout_seconds=5,
        enabled=False,
    )

    db = FakeDB()

    result = await monitor_service.create_monitor(
        db=db,
        data=data,
    )

    assert len(db.added) == 1

    monitor = db.added[0]

    assert monitor.name == "Test Monitor"
    assert monitor.url == "https://example.com/"
    assert monitor.interval_seconds == 30
    assert monitor.timeout_seconds == 5
    assert monitor.enabled is False

    assert result is monitor
    assert db.committed is True
    assert db.refreshed is True


@pytest.mark.asyncio
async def test_get_monitors():
    monitor_1 = make_monitor()
    monitor_2 = make_monitor()

    db = FakeDB(
        execute_value=[
            monitor_1,
            monitor_2,
        ],
    )

    result = await monitor_service.get_monitors(db)

    assert result == [
        monitor_1,
        monitor_2,
    ]


@pytest.mark.asyncio
async def test_get_monitors_empty():
    db = FakeDB(
        execute_value=[],
    )

    result = await monitor_service.get_monitors(db)

    assert result == []


@pytest.mark.asyncio
async def test_get_monitor_found():
    monitor_id = uuid4()
    monitor = make_monitor()
    monitor.id = monitor_id

    db = FakeDB(
        execute_value=monitor,
    )

    result = await monitor_service.get_monitor(
        db=db,
        monitor_id=monitor_id,
    )

    assert result is monitor


@pytest.mark.asyncio
async def test_get_monitor_not_found():
    monitor_id = uuid4()

    db = FakeDB(
        execute_value=None,
    )

    result = await monitor_service.get_monitor(
        db=db,
        monitor_id=monitor_id,
    )

    assert result is None


@pytest.mark.asyncio
async def test_update_monitor_without_url():
    monitor = make_monitor()

    data = SimpleNamespace(
        model_dump=lambda exclude_unset=True: {
            "name": "Updated Monitor",
            "interval_seconds": 120,
            "enabled": False,
        }
    )

    db = FakeDB()

    result = await monitor_service.update_monitor(
        db=db,
        monitor=monitor,
        data=data,
    )

    assert result is monitor
    assert monitor.name == "Updated Monitor"
    assert monitor.interval_seconds == 120
    assert monitor.enabled is False

    assert monitor.url == "https://example.com"

    assert db.committed is True
    assert db.refreshed is True


@pytest.mark.asyncio
async def test_update_monitor_with_url():
    monitor = make_monitor()

    data = SimpleNamespace(
        model_dump=lambda exclude_unset=True: {
            "url": "https://httpbin.org/",
        }
    )

    db = FakeDB()

    result = await monitor_service.update_monitor(
        db=db,
        monitor=monitor,
        data=data,
    )

    assert result is monitor
    assert monitor.url == "https://httpbin.org/"

    assert db.committed is True
    assert db.refreshed is True


@pytest.mark.asyncio
async def test_update_monitor_empty_update():
    monitor = make_monitor()

    original_name = monitor.name
    original_url = monitor.url

    data = SimpleNamespace(
        model_dump=lambda exclude_unset=True: {}
    )

    db = FakeDB()

    result = await monitor_service.update_monitor(
        db=db,
        monitor=monitor,
        data=data,
    )

    assert result is monitor
    assert monitor.name == original_name
    assert monitor.url == original_url

    assert db.committed is True
    assert db.refreshed is True


@pytest.mark.asyncio
async def test_delete_monitor():
    monitor = make_monitor()

    db = FakeDB()

    result = await monitor_service.delete_monitor(
        db=db,
        monitor=monitor,
    )

    assert result is None
    assert db.deleted == [monitor]
    assert db.committed is True