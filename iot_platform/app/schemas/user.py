from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=120)
    email: EmailStr | None = None
    is_active: bool | None = None
    role: UserRole | None = None
