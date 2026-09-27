from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.anomaly.service import detect_response_time_anomaly


def make_check(response_time_ms, check_id="check-id"):
    return SimpleNamespace(
        id=check_id,
        response_time_ms=response_time_ms,
    )


class FakeScalars:
    def __init__(self, items):
        self.items = items

    def all(self):
        return self.items


class FakeResult:
    def __init__(self, items):
        self.items = items

    def scalars(self):
        return FakeScalars(self.items)


def make_db():
    db = MagicMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.mark.asyncio
async def test_no_response_time_returns_none():
    db = make_db()
    check = make_check(None)

    result = await detect_response_time_anomaly(
        db=db,
        monitor_id="monitor-id",
        check=check,
    )

    assert result is None
    db.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_insufficient_history_returns_none():
    db = make_db()

    history = [
        make_check(100, "1"),
        make_check(102, "2"),
        make_check(98, "3"),
        make_check(101, "4"),
    ]

    db.execute.return_value = FakeResult(history)

    check = make_check(150, "current")

    result = await detect_response_time_anomaly(
        db=db,
        monitor_id="monitor-id",
        check=check,
    )

    assert result is None
    db.add.assert_not_called()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_non_anomaly_returns_none():
    db = make_db()

    history = [
        make_check(100, "1"),
        make_check(102, "2"),
        make_check(98, "3"),
        make_check(101, "4"),
        make_check(99, "5"),
    ]

    db.execute.return_value = FakeResult(history)

    check = make_check(101, "current")

    result = await detect_response_time_anomaly(
        db=db,
        monitor_id="monitor-id",
        check=check,
    )

    assert result is None
    db.add.assert_not_called()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_anomaly_is_created():
    db = make_db()

    history = [
        make_check(100, "1"),
        make_check(102, "2"),
        make_check(98, "3"),
        make_check(101, "4"),
        make_check(99, "5"),
        make_check(100, "6"),
        make_check(102, "7"),
        make_check(97, "8"),
        make_check(101, "9"),
        make_check(100, "10"),
    ]

    db.execute.return_value = FakeResult(history)

    check = make_check(150, "current")

    result = await detect_response_time_anomaly(
        db=db,
        monitor_id="monitor-id",
        check=check,
    )

    assert result is not None
    assert result.metric == "response_time_ms"
    assert result.value == 150
    assert result.monitor_id == "monitor-id"
    assert result.check_id == "current"
    assert result.severity == "CRITICAL"

    db.add.assert_called_once_with(result)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(result)