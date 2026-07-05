"""
Validates uploaded files before they touch disk or the DB.
Centralized here so document_service.py stays focused on orchestration,
not validation rules. Add new file types (HTML, JSON, XML) by extending
ALLOWED_CONTENT_TYPES only — nothing else needs to change.
"""

from app.config.settings import settings
from app.core.exceptions import BadRequestException

ALLOWED_CONTENT_TYPES: dict[str, str] = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "text/csv": ".csv",
}


def validate_file(content_type: str, file_size_bytes: int) -> str:
    """
    Returns the canonical file extension if valid, else raises BadRequestException.
    """
    if content_type not in ALLOWED_CONTENT_TYPES:
        allowed = ", ".join(sorted(set(ALLOWED_CONTENT_TYPES.values())))
        raise BadRequestException(
            f"Unsupported file type '{content_type}'. Allowed types: {allowed}"
        )

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise BadRequestException(
            f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB"
        )

    if file_size_bytes == 0:
        raise BadRequestException("File is empty")

    return ALLOWED_CONTENT_TYPES[content_type]