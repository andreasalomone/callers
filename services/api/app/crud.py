from sqlalchemy.orm import Session, joinedload
from sqlalchemy.future import select

from . import models, schemas

async def get_messages(db: Session, skip: int = 0, limit: int = 50) -> list[models.Message]:
    """
    Retrieve a list of messages from the database, most recent first.
    """
    result = await db.execute(
        select(models.Message)
        .options(joinedload(models.Message.channel))
        .order_by(models.Message.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_message(db: Session, message_id: int) -> models.Message | None:
    """
    Retrieve a single message by its ID.
    """
    result = await db.execute(
        select(models.Message)
        .options(joinedload(models.Message.channel))
        .where(models.Message.id == message_id)
    )
    return result.scalars().first() 