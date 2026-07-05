"""
Request/response contracts for the chat endpoints.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.chat import MessageRole


class SendMessageRequest(BaseModel):
    # If omitted, a new session is created automatically.
    session_id: uuid.UUID | None = None
    content: str = Field(min_length=1, max_length=8000)


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: MessageRole
    content: str
    citations: list | None
    created_at: datetime


class ChatSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime


class ChatSessionWithMessages(ChatSessionRead):
    messages: list[MessageRead]


class SendMessageResponse(BaseModel):
    session_id: uuid.UUID
    user_message: MessageRead
    assistant_message: MessageRead