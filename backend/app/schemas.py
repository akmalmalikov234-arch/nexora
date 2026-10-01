from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    admin_code: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_admin: bool
    is_active: bool
    created_at: datetime


class AppResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    package_name: str
    version: str
    description: str
    category: str
    file_name: str
    sha256: str
    size_bytes: int
    status: str
    download_count: int
    uploader_id: int
    created_at: datetime


class AppOut(AppResponse):
    pass


class AppStatusUpdate(BaseModel):
    status: Literal["approved", "rejected", "blocked"]


class StatusUpdate(AppStatusUpdate):
    pass
