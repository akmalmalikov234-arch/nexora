from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    apps = relationship(
        "App",
        back_populates="uploader"
    )


class App(Base):
    __tablename__ = "apps"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    package_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    version: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(100),
        default="Boshqa",
        nullable=False,
        index=True
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True
    )

    size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    download_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
        index=True
    )

    uploader_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    uploader = relationship(
        "User",
        back_populates="apps"
    )
