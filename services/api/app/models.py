from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Channel(Base):
    __tablename__ = "channels"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, nullable=False)

    messages = relationship("Message", back_populates="channel")

class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, index=True)
    channel_id = Column(BigInteger, ForeignKey("channels.id"), nullable=False, index=True)
    body = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    ingested_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    channel = relationship("Channel", back_populates="messages")

    __table_args__ = (
        Index("idx_messages_created_at_desc", created_at.desc()),
    ) 