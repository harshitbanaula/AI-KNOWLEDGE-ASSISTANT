"""
Business logic for chat. `send_message` currently returns a stub
assistant reply — this is intentional. The real RAG pipeline (retrieval
+ LLM generation) gets wired into this exact method in a later phase
without changing the API contract, so the frontend can be built against
this now and won't need to change later.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.chat import ChatSession, MessageRole
from app.repositories.chat_repository import ChatRepository


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chat_repo = ChatRepository(db)

    async def list_sessions(self, user_id: uuid.UUID) -> list[ChatSession]:
        return await self.chat_repo.list_sessions(user_id)

    async def get_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> ChatSession:
        session = await self.chat_repo.get_session_with_messages(session_id, user_id)
        if session is None:
            raise NotFoundException("Chat session not found")
        return session

    async def delete_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> None:
        session = await self.chat_repo.get_session(session_id, user_id)
        if session is None:
            raise NotFoundException("Chat session not found")
        await self.chat_repo.delete_session(session)

    async def send_message(self, user_id: uuid.UUID, session_id: uuid.UUID | None, content: str):
        if session_id is None:
            # Auto-title from the first ~50 chars of the first message
            title = content[:50] + ("..." if len(content) > 50 else "")
            session = await self.chat_repo.create_session(user_id, title=title)
        else:
            session = await self.chat_repo.get_session(session_id, user_id)
            if session is None:
                raise NotFoundException("Chat session not found")

        user_message = await self.chat_repo.add_message(session.id, MessageRole.USER, content)

        # --- STUB: replaced by real RAG + LLM router in a later phase ---
        assistant_reply = (
            "This is a placeholder response. The RAG pipeline (document "
            "retrieval + LLM generation) will be wired in here in the next phase."
        )
        assistant_message = await self.chat_repo.add_message(
            session.id, MessageRole.ASSISTANT, assistant_reply
        )

        await self.chat_repo.touch_session(session)

        return session.id, user_message, assistant_message