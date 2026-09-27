import asyncio

import aiohttp
import pytest

import app.monitors.checker as checker


class FakeResponse:
    def __init__(self, status):
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeSession:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def get(self, url):
        if self.error is not None:
            return FakeRequestContext(error=self.error)

        return FakeRequestContext(response=self.response)


class FakeRequestContext:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    async def __aenter__(self):
        if self.error is not None:
            raise self.error

        return self.response

    async def __aexit__(self, exc_type, exc, tb):
        return False


def fake_client_session_factory(
    *,
    response=None,
    error=None,
):
    def factory(*args, **kwargs):
        return FakeSession(
            response=response,
            error=error,
        )

    return factory


@pytest.mark.asyncio
async def test_check_url_success(monkeypatch):
    response = FakeResponse(status=200)

    monkeypatch.setattr(
        checker.aiohttp,
        "ClientSession",
        fake_client_session_factory(response=response),
    )

    result = await checker.check_url(
        "https://example.com",
        timeout_seconds=5,
    )

    assert result.status == "UP"
    assert result.status_code == 200
    assert result.response_time_ms is not None
    assert result.response_time_ms >= 0
    assert result.error is None


@pytest.mark.asyncio
async def test_check_url_http_error(monkeypatch):
    response = FakeResponse(status=500)

    monkeypatch.setattr(
        checker.aiohttp,
        "ClientSession",
        fake_client_session_factory(response=response),
    )

    result = await checker.check_url(
        "https://example.com",
        timeout_seconds=5,
    )

    assert result.status == "DOWN"
    assert result.status_code == 500
    assert result.response_time_ms is not None
    assert result.response_time_ms >= 0
    assert result.error == "HTTP error: 500"


@pytest.mark.asyncio
async def test_check_url_timeout(monkeypatch):
    monkeypatch.setattr(
        checker.aiohttp,
        "ClientSession",
        fake_client_session_factory(
            error=asyncio.TimeoutError(),
        ),
    )

    result = await checker.check_url(
        "https://example.com",
        timeout_seconds=1,
    )

    assert result.status == "DOWN"
    assert result.status_code is None
    assert result.response_time_ms is not None
    assert result.response_time_ms >= 0
    assert result.error == "Request timeout"


@pytest.mark.asyncio
async def test_check_url_client_error(monkeypatch):
    error = aiohttp.ClientConnectionError(
        "Connection failed"
    )

    monkeypatch.setattr(
        checker.aiohttp,
        "ClientSession",
        fake_client_session_factory(error=error),
    )

    result = await checker.check_url(
        "https://example.com",
        timeout_seconds=5,
    )

    assert result.status == "DOWN"
    assert result.status_code is None
    assert result.response_time_ms is not None
    assert result.response_time_ms >= 0
    assert result.error == "Connection failed"


@pytest.mark.asyncio
async def test_check_url_unexpected_error(monkeypatch):
    error = RuntimeError("Unexpected failure")

    monkeypatch.setattr(
        checker.aiohttp,
        "ClientSession",
        fake_client_session_factory(error=error),
    )

    result = await checker.check_url(
        "https://example.com",
        timeout_seconds=5,
    )

    assert result.status == "DOWN"
    assert result.status_code is None
    assert result.response_time_ms is not None
    assert result.response_time_ms >= 0
    assert result.error == "Unexpected failure"