from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    bio: Optional[str] = None

class MatchResponse(BaseModel):
    match_id: int
    user: UserBase
    similarity_score: float
    unread_messages: int
    created_at: datetime

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    content: str
    sender: UserBase
    is_own_message: bool
    created_at: datetime
    is_read: bool

class ConversationResponse(BaseModel):
    messages: List[MessageResponse]
    match_info: dict

class MatchingStats(BaseModel):
    total_matches: int
    unread_messages: int
    top_similarity: Optional[float] = None
