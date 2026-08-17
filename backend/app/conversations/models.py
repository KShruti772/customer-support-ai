from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


def _now():
    return datetime.utcnow()


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str  # 'user' or 'assistant' or agent name
    text: str
    timestamp: datetime = Field(default_factory=_now)
    metadata: Optional[Dict[str, Any]] = None


class Conversation(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    messages: List[Message] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


class ConversationCreate(BaseModel):
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AddMessageRequest(BaseModel):
    sender: str
    text: str
    metadata: Optional[Dict[str, Any]] = None


class ConversationOut(Conversation):
    pass
