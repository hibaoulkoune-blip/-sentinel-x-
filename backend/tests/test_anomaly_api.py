import uuid

import pytest


@pytest.mark.asyncio
async def test_list_anomalies(client):
    response = await client.get("/api/v1/anomalies")

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body, list)


@pytest.mark.asyncio
async def test_list_anomalies_with_limit(client):
    response = await client.get(
        "/api/v1/anomalies?limit=1"
    )

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body, list)
    assert len(body) <= 1


@pytest.mark.asyncio
async def test_list_anomalies_with_severity_filter(client):
    response = await client.get(
        "/api/v1/anomalies?severity=CRITICAL"
    )

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body, list)

    for anomaly in body:
        assert anomaly["severity"] == "CRITICAL"


@pytest.mark.asyncio
async def test_list_anomalies_with_monitor_filter(client):
    fake_monitor_id = str(uuid.uuid4())

    response = await client.get(
        f"/api/v1/anomalies?monitor_id={fake_monitor_id}"
    )

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body, list)

    for anomaly in body:
        assert anomaly["monitor_id"] == fake_monitor_id


@pytest.mark.asyncio
async def test_list_anomalies_invalid_limit(client):
    response = await client.get(
        "/api/v1/anomalies?limit=0"
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_anomalies_limit_above_maximum(client):
    response = await client.get(
        "/api/v1/anomalies?limit=101"
    )

    assert response.status_code == 422