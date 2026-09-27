"""
Tests for the foundation endpoints: `/` and `/health`.

These are the first tests in the project. They are deliberately simple —
their purpose is to prove the testing pipeline itself works end-to-end
(app boots, client can reach it, assertions run, coverage collects) before
any real domain logic exists to test.
"""

import pytest


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200

    body = response.json()
    assert body["service"] == "Sentinel-X"
    assert body["status"] == "running"
    assert "docs" in body


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["app_name"] == "Sentinel-X"
    assert body["environment"] in {"development", "testing", "production"}
