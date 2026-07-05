"""
POST   /documents/upload
GET    /documents
GET    /documents/{id}
DELETE /documents/{id}
"""

import uuid

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.document import DocumentListResponse, DocumentRead
from app.services.document_service import DocumentService

router = APIRouter()


@router.post("/upload", response_model=DocumentRead, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentRead:
    service = DocumentService(db)
    document = await service.upload(current_user.id, file)
    return document


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentListResponse:
    service = DocumentService(db)
    documents, total = await service.list_documents(current_user.id, limit, offset)
    return DocumentListResponse(total=total, documents=documents)


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentRead:
    service = DocumentService(db)
    return await service.get(document_id, current_user.id)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = DocumentService(db)
    await service.delete(document_id, current_user.id)