import uuid

import pytest


async def create_test_monitor(client):
    unique_id = uuid.uuid4().hex[:8]

    payload = {
        "name": f"INCIDENT Test Monitor {unique_id}",
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

    return response.json()["id"]


@pytest.mark.asyncio
async def test_list_incidents(client):
    response = await client.get(
        "/api/v1/incidents"
    )

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body, list)


@pytest.mark.asyncio
async def test_create_incident(client):
    monitor_id = await create_test_monitor(client)

    payload = {
        "monitor_id": monitor_id,
        "title": "Test incident",
        "description": "Test incident created by QA",
        "severity": "HIGH",
    }

    response = await client.post(
        "/api/v1/incidents",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert "id" in body
    assert body["monitor_id"] == monitor_id
    assert body["title"] == "Test incident"
    assert body["description"] == "Test incident created by QA"
    assert body["severity"] == "HIGH"
    assert body["status"] == "OPEN"
    assert body["resolved_at"] is None
    assert body["opened_at"] is not None


@pytest.mark.asyncio
async def test_get_incident(client):
    monitor_id = await create_test_monitor(client)

    create_response = await client.post(
        "/api/v1/incidents",
        json={
            "monitor_id": monitor_id,
            "title": "GET Incident",
            "description": "Testing GET",
            "severity": "MEDIUM",
        },
    )

    assert create_response.status_code == 201

    incident_id = create_response.json()["id"]

    response = await client.get(
        f"/api/v1/incidents/{incident_id}"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == incident_id
    assert body["monitor_id"] == monitor_id
    assert body["title"] == "GET Incident"


@pytest.mark.asyncio
async def test_get_incident_not_found(client):
    fake_id = str(uuid.uuid4())

    response = await client.get(
        f"/api/v1/incidents/{fake_id}"
    )

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == "Incident not found"


@pytest.mark.asyncio
async def test_update_incident(client):
    monitor_id = await create_test_monitor(client)

    create_response = await client.post(
        "/api/v1/incidents",
        json={
            "monitor_id": monitor_id,
            "title": "Original Incident",
            "description": "Original description",
            "severity": "MEDIUM",
        },
    )

    assert create_response.status_code == 201

    incident_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={
            "title": "Updated Incident",
            "severity": "HIGH",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == incident_id
    assert body["title"] == "Updated Incident"
    assert body["severity"] == "HIGH"


@pytest.mark.asyncio
async def test_resolve_incident(client):
    monitor_id = await create_test_monitor(client)

    create_response = await client.post(
        "/api/v1/incidents",
        json={
            "monitor_id": monitor_id,
            "title": "Incident to Resolve",
            "description": "Testing recovery",
            "severity": "HIGH",
        },
    )

    assert create_response.status_code == 201

    incident_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={
            "status": "RESOLVED",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "RESOLVED"
    assert body["resolved_at"] is not None


@pytest.mark.asyncio
async def test_reopen_incident(client):
    monitor_id = await create_test_monitor(client)

    create_response = await client.post(
        "/api/v1/incidents",
        json={
            "monitor_id": monitor_id,
            "title": "Incident Reopen Test",
            "severity": "HIGH",
        },
    )

    assert create_response.status_code == 201

    incident_id = create_response.json()["id"]

    resolve_response = await client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={
            "status": "RESOLVED",
        },
    )

    assert resolve_response.status_code == 200
    assert resolve_response.json()["resolved_at"] is not None

    reopen_response = await client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={
            "status": "OPEN",
        },
    )

    assert reopen_response.status_code == 200

    body = reopen_response.json()

    assert body["status"] == "OPEN"
    assert body["resolved_at"] is None


@pytest.mark.asyncio
async def test_delete_incident(client):
    monitor_id = await create_test_monitor(client)

    create_response = await client.post(
        "/api/v1/incidents",
        json={
            "monitor_id": monitor_id,
            "title": "Incident to Delete",
            "severity": "LOW",
        },
    )

    assert create_response.status_code == 201

    incident_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/v1/incidents/{incident_id}"
    )

    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/api/v1/incidents/{incident_id}"
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_incident_not_found(client):
    fake_id = str(uuid.uuid4())

    response = await client.delete(
        f"/api/v1/incidents/{fake_id}"
    )

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == "Incident not found"


@pytest.mark.asyncio
async def test_update_incident_not_found(client):
    fake_id = str(uuid.uuid4())

    response = await client.patch(
        f"/api/v1/incidents/{fake_id}",
        json={
            "title": "Updated",
        },
    )

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == "Incident not found"


@pytest.mark.asyncio
async def test_create_incident_empty_title(client):
    monitor_id = await create_test_monitor(client)

    response = await client.post(
        "/api/v1/incidents",
        json={
            "monitor_id": monitor_id,
            "title": "",
            "severity": "MEDIUM",
        },
    )

    assert response.status_code == 422