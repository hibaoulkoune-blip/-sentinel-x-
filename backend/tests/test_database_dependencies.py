from unittest.mock import AsyncMock, MagicMock

import pytest

import app.database.dependencies as dependencies


@pytest.mark.asyncio
async def test_get_db_success():
    session = MagicMock()
    session.rollback = AsyncMock()

    class FakeSessionContext:
        async def __aenter__(self):
            return session

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch_target = dependencies.AsyncSessionLocal

    original = monkeypatch_target

    dependencies.AsyncSessionLocal = lambda: FakeSessionContext()

    try:
        generator = dependencies.get_db()

        result = await anext(generator)

        assert result is session

        await generator.aclose()

        session.rollback.assert_not_awaited()

    finally:
        dependencies.AsyncSessionLocal = original


@pytest.mark.asyncio
async def test_get_db_rolls_back_on_exception(monkeypatch):
    session = MagicMock()
    session.rollback = AsyncMock()

    class FakeSessionContext:
        async def __aenter__(self):
            return session

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(
        dependencies,
        "AsyncSessionLocal",
        lambda: FakeSessionContext(),
    )

    generator = dependencies.get_db()

    result = await anext(generator)

    assert result is session

    with pytest.raises(RuntimeError, match="Database error"):
        await generator.athrow(
            RuntimeError("Database error")
        )

    session.rollback.assert_awaited_once()