"""
Import every model here. Alembic's env.py imports this module so
autogenerate can detect all tables via Base.metadata.
"""

from app.models.document import Document
from app.models.user import User

__all__ = ["User", "Document"]