"""
Repository pattern for Document. Every query is scoped by user_id where
relevant — a user must never be able to read/delete another user's
documents by guessing an ID. That check lives here, not in the service,
so it's impossible to accidentally bypass.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: uuid.UUID,
        original_filename: str,
        stored_filename: str,
        file_path: str,
        content_type: str,
        file_size_bytes: int,
    ) -> Document:
        document = Document(
            user_id=user_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            content_type=content_type,
            file_size_bytes=file_size_bytes,
            status=DocumentStatus.UPLOADED,
        )
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def get_by_id(self, document_id: uuid.UUID, user_id: uuid.UUID) -> Document | None:
        result = await self.db.execute(
            select(Document).where(Document.id == document_id, Document.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self, user_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> tuple[list[Document], int]:
        count_result = await self.db.execute(
            select(func.count()).select_from(Document).where(Document.user_id == user_id)
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all()), total

    async def delete(self, document: Document) -> None:
        await self.db.delete(document)
        await self.db.commit()