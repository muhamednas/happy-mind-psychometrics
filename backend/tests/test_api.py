import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_chat_endpoint(async_client: AsyncClient):
    response = await async_client.post("/api/v1/chat/message", json={"message": "hello"})
    assert response.status_code == 200
    assert "reply" in response.json()

@pytest.mark.asyncio
async def test_corporates_crud(async_client: AsyncClient):
    # 1. Create a corporate client
    payload = {
        "name": "Test Acme Corp",
        "slug": "test-acme",
        "logo_url": "https://example.com/logo.png",
        "primary_color": "#ff5500",
        "quota": 50
    }
    response = await async_client.post("/api/v1/admin/corporates", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Acme Corp"
    assert data["slug"] == "test-acme"
    assert data["logo_url"] == "https://example.com/logo.png"
    assert data["primary_color"] == "#ff5500"
    assert data["quota"] == 50
    corp_id = data["id"]

    # 2. Get list of corporates
    list_response = await async_client.get("/api/v1/admin/corporates")
    assert list_response.status_code == 200
    assert any(c["id"] == corp_id for c in list_response.json())

    # 3. Get single corporate config
    config_response = await async_client.get(f"/api/v1/admin/corporates/{corp_id}/config")
    assert config_response.status_code == 200
    config_data = config_response.json()
    assert config_data["name"] == "Test Acme Corp"
    assert config_data["config"]["primary"] == "#ff5500"

    # 4. Update the corporate client
    update_payload = {
        "name": "Updated Acme Corp",
        "quota": 100
    }
    update_response = await async_client.put(f"/api/v1/admin/corporates/{corp_id}", json=update_payload)
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["name"] == "Updated Acme Corp"
    assert updated_data["quota"] == 100

    # 5. Delete the corporate client
    delete_response = await async_client.delete(f"/api/v1/admin/corporates/{corp_id}")
    assert delete_response.status_code == 200
    
    # 6. Verify deletion
    verify_response = await async_client.get(f"/api/v1/admin/corporates/{corp_id}")
    assert verify_response.status_code == 404

@pytest.mark.asyncio
async def test_assessments_crud(async_client: AsyncClient):
    # 1. Create a master assessment template
    payload = {
        "title": "Abstract Reasoning Pro",
        "description": "Standard abstract logic module",
        "type": "cognitive",
        "time_limit_minutes": 45,
        "questions": [
            {
                "id": "q-abstract-1",
                "text": "Identify the missing pattern block",
                "type": "mcq",
                "options": ["A", "B", "C"],
                "correct_answer": "B"
            }
        ]
    }
    response = await async_client.post("/api/v1/admin/assessments", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Abstract Reasoning Pro"
    assert data["type"] == "cognitive"
    assert data["time_limit_minutes"] == 45
    assert len(data["questions"]) == 1
    assessment_id = data["id"]

    # 2. Get list of assessments
    list_response = await async_client.get("/api/v1/admin/assessments")
    assert list_response.status_code == 200
    assert any(a["id"] == assessment_id for a in list_response.json())

    # 3. Update the assessment template
    update_payload = {
        "title": "Abstract Reasoning Extreme",
        "time_limit_minutes": 60
    }
    update_response = await async_client.put(f"/api/v1/admin/assessments/{assessment_id}", json=update_payload)
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["title"] == "Abstract Reasoning Extreme"
    assert updated_data["time_limit_minutes"] == 60

    # 4. Delete the assessment template
    delete_response = await async_client.delete(f"/api/v1/admin/assessments/{assessment_id}")
    assert delete_response.status_code == 200

    # 5. Verify deletion
    verify_response = await async_client.get(f"/api/v1/admin/assessments/{assessment_id}")
    assert verify_response.status_code == 404
