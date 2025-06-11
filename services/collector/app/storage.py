import sqlalchemy
from sqlalchemy import Table, Column, BigInteger, String, MetaData, DateTime, func

from . import config

engine = sqlalchemy.create_engine(config.DATABASE_URL)
metadata = MetaData()

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

def setup_database():
    """Creates tables in the database."""
    metadata.create_all(engine)

def save_message(channel_id: int, channel_name: str, message_id: int, body: str, created_at: DateTime):
    """Saves a single message to the database and notifies."""
    with engine.connect() as conn:
        # Upsert channel
        stmt = sqlalchemy.dialects.postgresql.insert(channels).values(
            id=channel_id, name=channel_name
        ).on_conflict_do_nothing()
        conn.execute(stmt)

        # Insert message
        stmt = sqlalchemy.dialects.postgresql.insert(messages).values(
            id=message_id,
            channel_id=channel_id,
            body=body,
            created_at=created_at,
        ).on_conflict_do_nothing()
        conn.execute(stmt)

        # Notify the API service that a new message has arrived
        conn.execute(sqlalchemy.text(f"NOTIFY new_message, '{message_id}'"))
        conn.commit() 