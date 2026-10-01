from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, LoginRequest, Token
from ..security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    check_login_rate,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    email = data.email.strip().lower()

    existing = db.scalar(
        select(User).where(User.email == email)
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Bu email allaqachon ro'yxatdan o'tgan.",
        )

    user = User(
        email=email,
        password_hash=hash_password(data.password),
        is_admin=False,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Hisob muvaffaqiyatli yaratildi.",
        "user_id": user.id,
    }


@router.post("/login", response_model=Token)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    email = data.email.strip().lower()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if not user or not verify_password(
        data.password,
        user.password_hash,
    ):
        check_login_rate(email)

        raise HTTPException(
            status_code=401,
            detail="Email yoki parol noto'g'ri.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Hisob bloklangan.",
        )

    if user.is_admin:
        from ..security import verify_admin_panel_code

        if not data.admin_code:
            raise HTTPException(
                status_code=403,
                detail="Owner access code kerak.",
            )

        if not verify_admin_panel_code(data.admin_code):
            raise HTTPException(
                status_code=403,
                detail="Owner access code noto'g'ri.",
            )

    access_token = create_access_token(
        user_id=user.id,
        is_admin=user.is_admin,
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
    )


@router.get("/me")
def me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "is_active": current_user.is_active,
    }
