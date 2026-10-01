import os
import time
import hmac
from collections import defaultdict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import User


JWT_SECRET = os.getenv(
    "JWT_SECRET",
    ""
)

JWT_ALGORITHM = "HS256"

JWT_EXPIRE_MINUTES = int(
    os.getenv(
        "JWT_EXPIRE_MINUTES",
        "60"
    )
)

ADMIN_PANEL_CODE = os.getenv(
    "ADMIN_PANEL_CODE",
    ""
)


password_hasher = PasswordHash.recommended()

bearer_scheme = HTTPBearer(
    auto_error=False
)


failed_login_attempts = defaultdict(list)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(
    password: str,
    password_hash: str
) -> bool:
    return password_hasher.verify(
        password,
        password_hash
    )


def create_access_token(
    user_id: int,
    is_admin: bool
) -> str:

    import datetime

    expire = (
        datetime.datetime.now(
            datetime.timezone.utc
        )
        + datetime.timedelta(
            minutes=JWT_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "is_admin": bool(is_admin),
        "exp": expire
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def check_login_rate(email: str):
    now = time.time()

    recent = [
        timestamp
        for timestamp in failed_login_attempts[email]
        if now - timestamp < 600
    ]

    failed_login_attempts[email] = recent

    if len(recent) >= 8:
        raise HTTPException(
            status_code=429,
            detail=(
                "Juda ko'p noto'g'ri urinish. "
                "10 daqiqadan keyin qayta urinib ko'ring."
            )
        )


def register_failed_login(email: str):
    failed_login_attempts[email].append(
        time.time()
    )


def clear_failed_logins(email: str):
    failed_login_attempts.pop(
        email,
        None
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db)
) -> User:

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kirish talab qilinadi."
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Token noto'g'ri."
            )

        user_id = int(user_id)

    except (
        JWTError,
        ValueError,
        TypeError
    ):
        raise HTTPException(
            status_code=401,
            detail="Token noto'g'ri yoki muddati tugagan."
        )

    user = db.scalar(
        select(User).where(
            User.id == user_id
        )
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Foydalanuvchi topilmadi."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Hisob bloklangan."
        )

    return user


def require_admin(
    user: User = Depends(get_current_user)
) -> User:

    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Bu bo'lim faqat loyiha egasi uchun."
        )

    return user


def verify_admin_code(
    submitted_code: str | None
) -> bool:

    if not ADMIN_PANEL_CODE:
        return False

    if not submitted_code:
        return False

    return hmac.compare_digest(
        submitted_code,
        ADMIN_PANEL_CODE
    )
