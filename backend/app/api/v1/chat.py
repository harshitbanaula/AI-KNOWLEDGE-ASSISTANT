"""
POST   /chat            - send a message (creates a session if none given)
GET    /chat/history     - list all sessions for the current user
GET    /chat/{session_id} - full session with message history
DELETE /chat/{session_id} - delete a session and its messages
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatSessionRead,
    ChatSessionWithMessages,
    SendMessageRequest,
    SendMessageResponse,
)
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("", response_model=SendMessageResponse)
async def send_message(
    data: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SendMessageResponse:
    service = ChatService(db)
    session_id, user_message, assistant_message = await service.send_message(
        current_user.id, data.session_id, data.content
    )
    return SendMessageResponse(
        session_id=session_id, user_message=user_message, assistant_message=assistant_message
    )


@router.get("/history", response_model=list[ChatSessionRead])
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ChatSessionRead]:
    service = ChatService(db)
    return await service.list_sessions(current_user.id)


@router.get("/{session_id}", response_model=ChatSessionWithMessages)
async def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatSessionWithMessages:
    service = ChatService(db)
    return await service.get_session(session_id, current_user.id)


@router.delete("/{session_id}", status_code=204)
async def delete_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = ChatService(db)
    await service.delete_session(session_id, current_user.id)