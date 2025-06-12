import sqlalchemy
from sqlalchemy import Table, Column, BigInteger, String, MetaData, DateTime, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from datetime import datetime

from . import config

engine = create_async_engine(config.DATABASE_URL)
metadata = MetaData()

# Define an async session maker
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)

channels = Table(
    "channels",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", String, nullable=False),
)

messages = Table(
    "messages",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("channel_id", BigInteger, sqlalchemy.ForeignKey("channels.id"), nullable=False),
    Column("body", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("ingested_at", DateTime(timezone=True), server_default=func.now()),
)

async def setup_database():
    """Creates tables in the database if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

async def save_message(
    channel_id: int,
    channel_name: str,
    message_id: int,
    body: str,
    created_at: datetime,
):
    """
    Saves a single message to the database and notifies listeners.

    This function performs an "upsert" for the channel to ensure the channel
    is in the database before adding the message. It then inserts the message,
    ignoring conflicts if the message ID already exists. Finally, it sends a
    PostgreSQL NOTIFY signal on the 'new_message' channel with the message ID
    as the payload.

    Args:
        channel_id: The Telegram ID of the channel.
        channel_name: The display name of the channel.
        message_id: The Telegram ID of the message.
        body: The text content of the message.
        created_at: The timestamp when the message was created in Telegram.
    """
    async with AsyncSession() as session:
        async with session.begin():
            # Upsert channel
            stmt = sqlalchemy.dialects.postgresql.insert(channels).values(
                id=channel_id, name=channel_name
            ).on_conflict_do_nothing()
            await session.execute(stmt)

            # Insert message
            stmt = sqlalchemy.dialects.postgresql.insert(messages).values(
                id=message_id,
                channel_id=channel_id,
                body=body,
                created_at=created_at,
            ).on_conflict_do_nothing()
            await session.execute(stmt)

            # Notify the API service that a new message has arrived
            await session.execute(sqlalchemy.text(f"NOTIFY new_message, '{message_id}'")) 