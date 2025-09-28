from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    receiver_id: int

class Message(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True

class Match(BaseModel):
    user_id: int
    username: str
    compatibility_score: float
    created_at: datetime

    class Config:
        orm_mode = True
