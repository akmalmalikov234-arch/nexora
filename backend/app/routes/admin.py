from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import App, User
from ..schemas import (
    AppResponse,
    AppStatusUpdate,
    UserResponse,
)
from ..security import require_admin


router = APIRouter()


@router.get(
    "/apps",
    response_model=list[AppResponse]
)
def admin_apps(
    status: str = "pending",
    _: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    allowed = {
        "pending",
        "approved",
        "rejected",
        "blocked",
        "all",
    }

    if status not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Status noto'g'ri."
        )

    query = select(App)

    if status != "all":
        query = query.where(
            App.status == status
        )

    query = query.order_by(
        App.created_at.desc()
    )

    return db.scalars(query).all()


@router.post(
    "/apps/{app_id}/status",
    response_model=AppResponse
)
def change_app_status(
    app_id: int,
    data: AppStatusUpdate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    app = db.get(App, app_id)

    if app is None:
        raise HTTPException(
            status_code=404,
            detail="Ilova topilmadi."
        )

    app.status = data.status

    db.commit()
    db.refresh(app)

    return app


@router.get(
    "/users",
    response_model=list[UserResponse]
)
def users(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = select(User).order_by(
        User.created_at.desc()
    )

    return db.scalars(query).all()


@router.post(
    "/users/{user_id}/block",
    response_model=UserResponse
)
def block_user(
    user_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Foydalanuvchi topilmadi."
        )

    if user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Owner hisobini bu yerdan bloklab bo'lmaydi."
        )

    user.is_active = False

    db.commit()
    db.refresh(user)

    return user


@router.post(
    "/users/{user_id}/unblock",
    response_model=UserResponse
)
def unblock_user(
    user_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Foydalanuvchi topilmadi."
        )

    user.is_active = True

    db.commit()
    db.refresh(user)

    return user
