import uuid

import pytest


@pytest.mark.asyncio
async def test_list_monitors(client):
    response = await client.get("/api/v1/monitors")

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body, list)


@pytest.mark.asyncio
async def test_create_monitor(client):
    unique_id = uuid.uuid4().hex[:8]

    payload = {
        "name": f"QA Test Monitor {unique_id}",
        "url": "https://example.com",
        "interval_seconds": 60,
        "timeout_seconds": 10,
        "enabled": True,
    }

    response = await client.post(
        "/api/v1/monitors",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert "id" in body
    assert body["name"] == payload["name"]
    assert body["url"].rstrip("/") == "https://example.com"
    assert body["interval_seconds"] == 60
    assert body["timeout_seconds"] == 10
    assert body["enabled"] is True


@pytest.mark.asyncio
async def test_get_monitor(client):
    unique_id = uuid.uuid4().hex[:8]

    create_payload = {
        "name": f"GET Test Monitor {unique_id}",
        "url": "https://example.com",
        "interval_seconds": 60,
        "timeout_seconds": 10,
        "enabled": True,
    }

    create_response = await client.post(
        "/api/v1/monitors",
        json=create_payload,
    )

    assert create_response.status_code == 201

    monitor_id = create_response.json()["id"]

    response = await client.get(
        f"/api/v1/monitors/{monitor_id}"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == monitor_id
    assert body["name"] == create_payload["name"]


@pytest.mark.asyncio
async def test_get_monitor_not_found(client):
    fake_id = str(uuid.uuid4())

    response = await client.get(
        f"/api/v1/monitors/{fake_id}"
    )

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == "Monitor not found"


@pytest.mark.asyncio
async def test_update_monitor(client):
    unique_id = uuid.uuid4().hex[:8]

    create_payload = {
        "name": f"UPDATE Test Monitor {unique_id}",
        "url": "https://example.com",
        "interval_seconds": 60,
        "timeout_seconds": 10,
        "enabled": True,
    }

    create_response = await client.post(
        "/api/v1/monitors",
        json=create_payload,
    )

    assert create_response.status_code == 201

    monitor_id = create_response.json()["id"]

    update_payload = {
        "name": f"UPDATED Monitor {unique_id}",
        "interval_seconds": 120,
    }

    response = await client.patch(
        f"/api/v1/monitors/{monitor_id}",
        json=update_payload,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == monitor_id
    assert body["name"] == update_payload["name"]
    assert body["interval_seconds"] == 120


@pytest.mark.asyncio
async def test_delete_monitor(client):
    unique_id = uuid.uuid4().hex[:8]
    create_payload = {
        "name": f"DELETE Test Monitor {unique_id}",
        "url": "https://example.com",
        "interval_seconds": 60,
        "timeout_seconds": 10,
        "enabled": True,
    }

    create_response = await client.post(
        "/api/v1/monitors",
        json=create_payload,
    )

    assert create_response.status_code == 201

    monitor_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/v1/monitors/{monitor_id}"
    )

    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/api/v1/monitors/{monitor_id}"
    )

    assert get_response.status_code == 404
@pytest.mark.asyncio
async def test_check_monitor(client):
    unique_id = uuid.uuid4().hex[:8]

    create_payload = {
        "name": f"CHECK Test Monitor {unique_id}",
        "url": "https://example.com",
        "interval_seconds": 60,
        "timeout_seconds": 10,
        "enabled": True,
    }

    create_response = await client.post(
        "/api/v1/monitors",
        json=create_payload,
    )

    assert create_response.status_code == 201

    monitor_id = create_response.json()["id"]

    response = await client.post(
        f"/api/v1/monitors/{monitor_id}/check"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["monitor_id"] == monitor_id
    assert body["status"] == "UP"
    assert body["status_code"] == 200
    assert body["response_time_ms"] is not None
    assert body["error"] is None
@pytest.mark.asyncio
async def test_get_check_history(client):
    unique_id = uuid.uuid4().hex[:8]

    create_payload = {
        "name": f"HISTORY Test Monitor {unique_id}",
        "url": "https://example.com",
        "interval_seconds": 60,
        "timeout_seconds": 10,
        "enabled": True,
    }

    create_response = await client.post(
        "/api/v1/monitors",
        json=create_payload,
    )

    assert create_response.status_code == 201

    monitor_id = create_response.json()["id"]

    check_response = await client.post(
        f"/api/v1/monitors/{monitor_id}/check"
    )

    assert check_response.status_code == 200

    history_response = await client.get(
        f"/api/v1/monitors/{monitor_id}/checks"
    )

    assert history_response.status_code == 200

    body = history_response.json()

    assert isinstance(body, list)
    assert len(body) >= 1

    check = body[0]

    assert check["monitor_id"] == monitor_id
    assert check["status"] == "UP"
    assert check["status_code"] == 200
    assert check["response_time_ms"] is not None
@pytest.mark.asyncio
async def test_create_monitor_invalid_interval(client):
    payload = {
        "name": "Invalid Interval Monitor",
        "url": "https://example.com",
        "interval_seconds": 2,
        "timeout_seconds": 10,
        "enabled": True,
    }

    response = await client.post(
        "/api/v1/monitors",
        json=payload,
    )

    assert response.status_code == 422
@pytest.mark.asyncio
async def test_create_monitor_invalid_url(client):
    payload = {
        "name": "Invalid URL Monitor",
        "url": "not-a-valid-url",
        "interval_seconds": 60,
        "timeout_seconds": 10,
        "enabled": True,
    }

    response = await client.post(
        "/api/v1/monitors",
        json=payload,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_monitor_invalid_timeout(client):
    payload = {
        "name": "Invalid Timeout Monitor",
        "url": "https://example.com",
        "interval_seconds": 60,
        "timeout_seconds": 0,
        "enabled": True,
    }

    response = await client.post(
        "/api/v1/monitors",
        json=payload,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_monitor_empty_name(client):
    payload = {
        "name": "",
        "url": "https://example.com",
        "interval_seconds": 60,
        "timeout_seconds": 10,
        "enabled": True,
    }

    response = await client.post(
        "/api/v1/monitors",
        json=payload,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_check_monitor_not_found(client):
    fake_id = str(uuid.uuid4())

    response = await client.post(
        f"/api/v1/monitors/{fake_id}/check"
    )

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == "Monitor not found"


@pytest.mark.asyncio
async def test_check_history_monitor_not_found(client):
    fake_id = str(uuid.uuid4())

    response = await client.get(
        f"/api/v1/monitors/{fake_id}/checks"
    )

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == "Monitor not found"


@pytest.mark.asyncio
async def test_update_monitor_not_found(client):
    fake_id = str(uuid.uuid4())

    response = await client.patch(
        f"/api/v1/monitors/{fake_id}",
        json={
            "name": "Updated Monitor",
        },
    )

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == "Monitor not found"


@pytest.mark.asyncio
async def test_delete_monitor_not_found(client):
    fake_id = str(uuid.uuid4())

    response = await client.delete(
        f"/api/v1/monitors/{fake_id}"
    )

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == "Monitor not found"


@pytest.mark.asyncio
async def test_update_monitor_url(client):
    unique_id = uuid.uuid4().hex[:8]

    create_payload = {
        "name": f"URL UPDATE Monitor {unique_id}",
        "url": "https://example.com",
        "interval_seconds": 60,
        "timeout_seconds": 10,
        "enabled": True,
    }

    create_response = await client.post(
        "/api/v1/monitors",
        json=create_payload,
    )

    assert create_response.status_code == 201

    monitor_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/monitors/{monitor_id}",
        json={
            "url": "https://httpbin.org",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == monitor_id
    assert body["url"].rstrip("/") == "https://httpbin.org"


@pytest.mark.asyncio
async def test_disable_monitor(client):
    unique_id = uuid.uuid4().hex[:8]

    create_payload = {
        "name": f"DISABLE Monitor {unique_id}",
        "url": "https://example.com",
        "interval_seconds": 60,
        "timeout_seconds": 10,
        "enabled": True,
    }

    create_response = await client.post(
        "/api/v1/monitors",
        json=create_payload,
    )

    assert create_response.status_code == 201

    monitor_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/monitors/{monitor_id}",
        json={
            "enabled": False,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == monitor_id
    assert body["enabled"] is False


@pytest.mark.asyncio
async def test_update_monitor_timeout(client):
    unique_id = uuid.uuid4().hex[:8]

    create_payload = {
        "name": f"TIMEOUT UPDATE Monitor {unique_id}",
        "url": "https://example.com",
        "interval_seconds": 60,
        "timeout_seconds": 10,
        "enabled": True,
    }

    create_response = await client.post(
        "/api/v1/monitors",
        json=create_payload,
    )

    assert create_response.status_code == 201

    monitor_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/monitors/{monitor_id}",
        json={
            "timeout_seconds": 20,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == monitor_id
    assert body["timeout_seconds"] == 20
