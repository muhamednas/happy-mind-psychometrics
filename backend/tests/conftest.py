import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.database import engine, Base
import app.models as models_module
from app.main import app as fastapi_app

@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
