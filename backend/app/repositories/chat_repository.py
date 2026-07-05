"""
Repository pattern for chat data. Every session query is scoped by
user_id, same reasoning as documents — prevents cross-user access even
if a session_id is guessed or leaked.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession as DBSession
from sqlalchemy.orm import selectinload

from app.models.chat import ChatSession, Message, MessageRole


class ChatRepository:
    def __init__(self, db: DBSession):
        self.db = db

    async def create_session(self, user_id: uuid.UUID, title: str = "New Chat") -> ChatSession:
        session = ChatSession(user_id=user_id, title=title)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> ChatSession | None:
        result = await self.db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id, ChatSession.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_session_with_messages(
        self, session_id: uuid.UUID, user_id: uuid.UUID
    ) -> ChatSession | None:
        result = await self.db.execute(
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_sessions(self, user_id: uuid.UUID) -> list[ChatSession]:
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
        )
        return list(result.scalars().all())

    async def delete_session(self, session: ChatSession) -> None:
        await self.db.delete(session)
        await self.db.commit()

    async def add_message(
        self,
        session_id: uuid.UUID,
        role: MessageRole,
        content: str,
        citations: list | None = None,
    ) -> Message:
        message = Message(session_id=session_id, role=role, content=content, citations=citations)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def touch_session(self, session: ChatSession) -> None:
        """Bumps updated_at so session lists sort by most recently active."""
        await self.db.execute(
            ChatSession.__table__.update()
            .where(ChatSession.id == session.id)
            .values(updated_at=func.now())
        )
        await self.db.commit()