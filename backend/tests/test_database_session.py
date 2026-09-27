from unittest.mock import AsyncMock, MagicMock

import pytest

import app.database.session as session_module


@pytest.mark.asyncio
async def test_get_db():
    session = MagicMock()

    class FakeSessionContext:
        async def __aenter__(self):
            return session

        async def __aexit__(self, exc_type, exc, tb):
            return False

    original = session_module.AsyncSessionLocal
    session_module.AsyncSessionLocal = lambda: FakeSessionContext()

    try:
        generator = session_module.get_db()

        result = await anext(generator)

        assert result is session

        await generator.aclose()

    finally:
        session_module.AsyncSessionLocal = original


@pytest.mark.asyncio
async def test_close_database(monkeypatch):
    dispose_mock = AsyncMock()

    fake_engine = MagicMock()
    fake_engine.dispose = dispose_mock

    monkeypatch.setattr(
        session_module,
        "engine",
        fake_engine,
    )

    await session_module.close_database()

    dispose_mock.assert_awaited_once()