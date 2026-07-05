"""
Shared FastAPI dependencies. `get_current_user` is what protects every
route that needs auth — just add `current_user: User = Depends(get_current_user)`
to any endpoint signature.
"""

import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
from app.database.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials  # <-- extract the actual JWT string here

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise UnauthorizedException("Invalid or expired token")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Invalid token payload")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(uuid.UUID(user_id))
    if user is None:
        raise UnauthorizedException("User no longer exists")
    if not user.is_active:
        raise UnauthorizedException("This account has been deactivated")

    return user