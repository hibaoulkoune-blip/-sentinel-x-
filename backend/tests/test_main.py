import asyncio

import pytest

import app.main as main


@pytest.mark.asyncio
async def test_lifespan():
    async def fake_monitoring_loop():
        await asyncio.sleep(3600)

    monkeypatch = pytest.MonkeyPatch()

    try:
        monkeypatch.setattr(
            main,
            "run_monitoring_loop",
            fake_monitoring_loop,
        )

        async with main.lifespan(main.app):
            pass

    finally:
        monkeypatch.undo()