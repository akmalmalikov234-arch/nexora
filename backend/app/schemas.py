from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=1,
        max_length=128
    )
    admin_code: str | None = Field(
        default=None,
        max_length=256
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    email: EmailStr
    is_admin: bool
    is_active: bool
    created_at: datetime


class AppResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    name: str
    package_name: str
    version: str
    description: str
    category: str
    file_name: str
    sha256: str
    size_bytes: int
    download_count: int
    status: str
    uploader_id: int
    created_at: datetime


class AppStatusUpdate(BaseModel):
    status: Literal[
        "approved",
        "rejected",
        "blocked"
    ]
