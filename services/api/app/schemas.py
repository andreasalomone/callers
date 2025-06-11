from pydantic import BaseModel
from datetime import datetime

class Channel(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class Message(BaseModel):
    id: int
    body: str
    created_at: datetime
    channel: Channel

    class Config:
        from_attributes = True 