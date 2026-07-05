"""
Business logic for document management. Handles the full upload flow:
validate -> generate a safe on-disk name -> write to disk -> persist
the DB record. Also owns delete (DB row + the file on disk together,
so they never drift out of sync).
"""

import os
import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.exceptions import NotFoundException
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.utils.file_validation import validate_file


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.doc_repo = DocumentRepository(db)

    async def upload(self, user_id: uuid.UUID, file: UploadFile) -> Document:
        contents = await file.read()
        extension = validate_file(file.content_type, len(contents))

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        # Random on-disk filename — never trust the client's filename for
        # the actual path (path traversal risk); original name is kept
        # separately in the DB purely for display purposes.
        stored_filename = f"{uuid.uuid4().hex}{extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, stored_filename)

        with open(file_path, "wb") as f:
            f.write(contents)

        return await self.doc_repo.create(
            user_id=user_id,
            original_filename=file.filename or "unnamed",
            stored_filename=stored_filename,
            file_path=file_path,
            content_type=file.content_type,
            file_size_bytes=len(contents),
        )

    async def get(self, document_id: uuid.UUID, user_id: uuid.UUID) -> Document:
        document = await self.doc_repo.get_by_id(document_id, user_id)
        if document is None:
            raise NotFoundException("Document not found")
        return document

    async def list_documents(
        self, user_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> tuple[list[Document], int]:
        return await self.doc_repo.list_by_user(user_id, limit, offset)

    async def delete(self, document_id: uuid.UUID, user_id: uuid.UUID) -> None:
        document = await self.get(document_id, user_id)
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        await self.doc_repo.delete(document)