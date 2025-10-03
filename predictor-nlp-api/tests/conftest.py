import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from app.main import app as fastapi_app

@pytest.fixture(scope="session")
def app() -> FastAPI:
    return fastapi_app

@pytest.fixture
async def client(app: FastAPI):
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
