import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

import app.scheduler.service as scheduler_service


class FakeDB:
    def __init__(self, monitor=None, execute_result=None, get_error=None):
        self.monitor = monitor
        self.execute_result = execute_result
        self.get_error = get_error
        self.added = []
        self.committed = False
        self.refreshed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, model, monitor_id):
        if self.get_error is not None:
            raise self.get_error
        return self.monitor

    async def execute(self, statement):
        if isinstance(self.execute_result, Exception):
            raise self.execute_result
        return self.execute_result

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        self.refreshed = True


class FakeSessionFactory:
    def __init__(self, db):
        self.db = db

    def __call__(self):
        return self.db


def make_monitor(
    *,
    enabled=True,
    interval_seconds=60,
    name="Test Monitor",
):
    return SimpleNamespace(
        id=uuid4(),
        name=name,
        url="https://example.com",
        interval_seconds=interval_seconds,
        timeout_seconds=10,
        enabled=enabled,
    )


def make_result(
    *,
    status="UP",
    status_code=200,
    response_time_ms=100.0,
    error=None,
):
    return SimpleNamespace(
        status=status,
        status_code=status_code,
        response_time_ms=response_time_ms,
        error=error,
    )


@pytest.mark.asyncio
async def test_run_monitor_check_up_without_recovery(
    monkeypatch,
):
    monitor = make_monitor()
    result = make_result()

    db = FakeDB()
    monkeypatch.setattr(
        scheduler_service,
        "AsyncSessionLocal",
        FakeSessionFactory(db),
    )

    monkeypatch.setattr(
        scheduler_service,
        "check_url",
        lambda **kwargs: _async_return(result),
    )

    monkeypatch.setattr(
        scheduler_service,
        "detect_response_time_anomaly",
        lambda **kwargs: _async_return(None),
    )

    resolve_mock = lambda **kwargs: _async_return(None)

    monkeypatch.setattr(
        scheduler_service,
        "resolve_open_incident",
        resolve_mock,
    )

    await scheduler_service.run_monitor_check(monitor)

    assert len(db.added) == 1
    assert db.added[0].monitor_id == monitor.id
    assert db.added[0].status == "UP"
    assert db.committed is True
    assert db.refreshed is True


@pytest.mark.asyncio
async def test_run_monitor_check_up_with_anomaly_and_recovery(
    monkeypatch,
):
    monitor = make_monitor()
    result = make_result()

    anomaly = SimpleNamespace(
        metric="response_time_ms",
        z_score=3.25,
        severity="HIGH",
    )

    incident = SimpleNamespace(
        id=uuid4(),
    )

    db = FakeDB()

    monkeypatch.setattr(
        scheduler_service,
        "AsyncSessionLocal",
        FakeSessionFactory(db),
    )

    monkeypatch.setattr(
        scheduler_service,
        "check_url",
        lambda **kwargs: _async_return(result),
    )

    monkeypatch.setattr(
        scheduler_service,
        "detect_response_time_anomaly",
        lambda **kwargs: _async_return(anomaly),
    )

    monkeypatch.setattr(
        scheduler_service,
        "resolve_open_incident",
        lambda **kwargs: _async_return(incident),
    )

    await scheduler_service.run_monitor_check(monitor)

    assert len(db.added) == 1
    assert db.added[0].status == "UP"


@pytest.mark.asyncio
async def test_run_monitor_check_down_new_incident(
    monkeypatch,
):
    monitor = make_monitor()
    result = make_result(
        status="DOWN",
        status_code=None,
        response_time_ms=None,
        error="Connection failed",
    )

    incident = SimpleNamespace(
        id=uuid4(),
    )

    db = FakeDB()

    monkeypatch.setattr(
        scheduler_service,
        "AsyncSessionLocal",
        FakeSessionFactory(db),
    )

    monkeypatch.setattr(
        scheduler_service,
        "check_url",
        lambda **kwargs: _async_return(result),
    )

    monkeypatch.setattr(
        scheduler_service,
        "detect_response_time_anomaly",
        lambda **kwargs: _async_return(None),
    )

    monkeypatch.setattr(
        scheduler_service,
        "create_incident_from_failure",
        lambda **kwargs: _async_return(incident),
    )

    await scheduler_service.run_monitor_check(monitor)

    assert len(db.added) == 1
    assert db.added[0].status == "DOWN"
    assert db.added[0].error == "Connection failed"


@pytest.mark.asyncio
async def test_run_monitor_check_down_existing_incident(
    monkeypatch,
):
    monitor = make_monitor()
    result = make_result(
        status="DOWN",
        status_code=500,
        response_time_ms=250.0,
        error="Server error",
    )

    db = FakeDB()

    monkeypatch.setattr(
        scheduler_service,
        "AsyncSessionLocal",
        FakeSessionFactory(db),
    )

    monkeypatch.setattr(
        scheduler_service,
        "check_url",
        lambda **kwargs: _async_return(result),
    )

    monkeypatch.setattr(
        scheduler_service,
        "detect_response_time_anomaly",
        lambda **kwargs: _async_return(None),
    )

    monkeypatch.setattr(
        scheduler_service,
        "create_incident_from_failure",
        lambda **kwargs: _async_return(None),
    )

    await scheduler_service.run_monitor_check(monitor)

    assert len(db.added) == 1
    assert db.added[0].status == "DOWN"


@pytest.mark.asyncio
async def test_monitor_worker_deleted_monitor(
    monkeypatch,
):
    monitor_id = uuid4()

    db = FakeDB(monitor=None)

    monkeypatch.setattr(
        scheduler_service,
        "AsyncSessionLocal",
        FakeSessionFactory(db),
    )

    await scheduler_service.monitor_worker(monitor_id)


@pytest.mark.asyncio
async def test_monitor_worker_disabled_monitor(
    monkeypatch,
):
    monitor_id = uuid4()

    monitor = make_monitor(enabled=False)

    db = FakeDB(monitor=monitor)

    monkeypatch.setattr(
        scheduler_service,
        "AsyncSessionLocal",
        FakeSessionFactory(db),
    )

    await scheduler_service.monitor_worker(monitor_id)


@pytest.mark.asyncio
async def test_monitor_worker_success_then_cancelled(
    monkeypatch,
):
    monitor = make_monitor(
        enabled=True,
        interval_seconds=10,
    )

    db = FakeDB(monitor=monitor)

    monkeypatch.setattr(
        scheduler_service,
        "AsyncSessionLocal",
        FakeSessionFactory(db),
    )

    async def fake_run_monitor_check(received_monitor):
        assert received_monitor is monitor

    monkeypatch.setattr(
        scheduler_service,
        "run_monitor_check",
        fake_run_monitor_check,
    )

    async def cancel_on_sleep(seconds):
        raise asyncio.CancelledError

    monkeypatch.setattr(
        scheduler_service.asyncio,
        "sleep",
        cancel_on_sleep,
    )

    with pytest.raises(asyncio.CancelledError):
        await scheduler_service.monitor_worker(monitor.id)


@pytest.mark.asyncio
async def test_monitor_worker_error_then_cancelled(
    monkeypatch,
):
    monitor_id = uuid4()

    db = FakeDB(
        monitor=None,
        get_error=RuntimeError("database failure"),
    )

    monkeypatch.setattr(
        scheduler_service,
        "AsyncSessionLocal",
        FakeSessionFactory(db),
    )

    sleep_calls = 0

    async def controlled_sleep(seconds):
        nonlocal sleep_calls
        sleep_calls += 1

        if sleep_calls == 1:
            return

        raise asyncio.CancelledError

    monkeypatch.setattr(
        scheduler_service.asyncio,
        "sleep",
        controlled_sleep,
    )

    with pytest.raises(asyncio.CancelledError):
        await scheduler_service.monitor_worker(monitor_id)

    assert sleep_calls == 2


@pytest.mark.asyncio
async def test_monitoring_loop_creates_worker_then_cancelled(
    monkeypatch,
):
    monitor = make_monitor()

    scalars = SimpleNamespace(
        all=lambda: [monitor],
    )

    execute_result = SimpleNamespace(
        scalars=lambda: scalars,
    )

    db = FakeDB(
        execute_result=execute_result,
    )

    monkeypatch.setattr(
        scheduler_service,
        "AsyncSessionLocal",
        FakeSessionFactory(db),
    )

    async def fake_monitor_worker(monitor_id):
        await asyncio.Event().wait()

    monkeypatch.setattr(
        scheduler_service,
        "monitor_worker",
        fake_monitor_worker,
    )

    sleep_calls = 0

    async def controlled_sleep(seconds):
        nonlocal sleep_calls
        sleep_calls += 1
        raise asyncio.CancelledError

    monkeypatch.setattr(
        scheduler_service.asyncio,
        "sleep",
        controlled_sleep,
    )

    with pytest.raises(asyncio.CancelledError):
        await scheduler_service.run_monitoring_loop()

    assert sleep_calls == 1


@pytest.mark.asyncio
async def test_monitoring_loop_removes_worker(
    monkeypatch,
):
    monitor = make_monitor()

    responses = [
        SimpleNamespace(
            scalars=lambda: SimpleNamespace(
                all=lambda: [monitor],
            )
        ),
        SimpleNamespace(
            scalars=lambda: SimpleNamespace(
                all=lambda: [],
            )
        ),
    ]

    db = FakeDB()

    execute_calls = 0

    async def execute(statement):
        nonlocal execute_calls

        result = responses[execute_calls]
        execute_calls += 1

        return result

    db.execute = execute

    monkeypatch.setattr(
        scheduler_service,
        "AsyncSessionLocal",
        FakeSessionFactory(db),
    )

    async def fake_monitor_worker(monitor_id):
        await asyncio.Event().wait()

    monkeypatch.setattr(
        scheduler_service,
        "monitor_worker",
        fake_monitor_worker,
    )

    sleep_calls = 0

    async def controlled_sleep(seconds):
        nonlocal sleep_calls
        sleep_calls += 1

        if sleep_calls == 1:
            return

        raise asyncio.CancelledError

    monkeypatch.setattr(
        scheduler_service.asyncio,
        "sleep",
        controlled_sleep,
    )

    with pytest.raises(asyncio.CancelledError):
        await scheduler_service.run_monitoring_loop()

    assert execute_calls == 2
    assert sleep_calls == 2


@pytest.mark.asyncio
async def test_monitoring_loop_manager_error_then_cancelled(
    monkeypatch,
):
    db = FakeDB(
        execute_result=RuntimeError("database unavailable"),
    )

    monkeypatch.setattr(
        scheduler_service,
        "AsyncSessionLocal",
        FakeSessionFactory(db),
    )

    sleep_calls = 0

    async def controlled_sleep(seconds):
        nonlocal sleep_calls
        sleep_calls += 1

        raise asyncio.CancelledError

    monkeypatch.setattr(
        scheduler_service.asyncio,
        "sleep",
        controlled_sleep,
    )

    with pytest.raises(asyncio.CancelledError):
        await scheduler_service.run_monitoring_loop()

    assert sleep_calls == 1


async def _async_return(value):
    return value