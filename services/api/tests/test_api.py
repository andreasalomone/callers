import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import Depends

from app.main import app
from app.database import get_db
from app.models import Base, Message, Channel
from datetime import datetime

# Setup the Test Database
DATABASE_URL_TEST = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL_TEST, echo=True)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_read_messages(test_db):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Add a channel and a message to the test DB
        async with TestingSessionLocal() as session:
            channel = Channel(id=1, name="Test Channel")
            session.add(channel)
            await session.commit()
            
            message = Message(
                id=1,
                channel_id=1,
                body="Test message",
                created_at=datetime.utcnow(),
                ingested_at=datetime.utcnow(),
            )
            session.add(message)
            await session.commit()

        response = await ac.get("/api/feed")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["body"] == "Test message"
        assert data[0]["channel"]["name"] == "Test Channel" 