import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# We use the simple "postgresql://" URL from the .env file,
# but we explicitly tell SQLAlchemy to use the "asyncpg" driver.
engine = create_async_engine(f"postgresql+asyncpg://{DATABASE_URL.split('://')[1]}", echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session 