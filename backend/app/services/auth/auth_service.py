"""
Business logic for authentication. The API layer (app/api/v1/auth.py) calls
this — it never talks to the repository or DB session directly. This is
where rules live (e.g. "email must be unique", "password must match").
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ConflictException, UnauthorizedException
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token, UserCreate


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, data: UserCreate) -> User:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ConflictException("A user with this email already exists")

        hashed = hash_password(data.password)
        return await self.user_repo.create(
            email=data.email, hashed_password=hashed, full_name=data.full_name
        )

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Incorrect email or password")
        if not user.is_active:
            raise BadRequestException("This account has been deactivated")
        return user

    def issue_tokens(self, user: User) -> Token:
        subject = str(user.id)
        return Token(
            access_token=create_access_token(subject),
            refresh_token=create_refresh_token(subject),
        )