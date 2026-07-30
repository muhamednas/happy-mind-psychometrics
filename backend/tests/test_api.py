import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_chat_endpoint(async_client: AsyncClient):
    response = await async_client.post("/api/v1/chat/message", json={"message": "hello"})
    assert response.status_code == 200
    assert "reply" in response.json()
