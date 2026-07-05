"""
Request/response contracts for the auth endpoints. Keeps API-facing shapes
separate from the ORM model — e.g. we never expose hashed_password.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserCreate(BaseModel):
  email: EmailStr
  password: str = Field(min_length=8, max_length=128)
  full_name: str | None = None
  
class UserLogin(BaseModel):
  email: EmailStr
  password: str
  
class UserRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: uuid.UUID
  email: EmailStr
  full_name: str | None = None
  is_active: bool
  created_at: datetime

class Token(BaseModel):
  access_token: str
  refresh_token: str
  token_type: str = "bearer"

class TokenPayload(BaseModel):
  sub: str | None = None
  type: str | None = None