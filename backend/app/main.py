import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .database import Base, SessionLocal, engine
from .models import User
from .security import hash_password

from .routes.auth import router as auth_router
from .routes.apps import router as apps_router
from .routes.admin import router as admin_router


def validate_security_settings():
    jwt_secret = os.getenv("JWT_SECRET", "")
    admin_password = os.getenv("ADMIN_PASSWORD", "")
    admin_code = os.getenv("ADMIN_PANEL_CODE", "")

    if len(jwt_secret) < 32:
        raise RuntimeError(
            "JWT_SECRET kamida 32 ta belgidan iborat bo'lishi kerak."
        )

    if len(admin_password) < 12:
        raise RuntimeError(
            "ADMIN_PASSWORD kamida 12 ta belgidan iborat bo'lishi kerak."
        )

    if len(admin_code) < 24:
        raise RuntimeError(
            "ADMIN_PANEL_CODE kamida 24 ta belgidan iborat bo'lishi kerak."
        )


validate_security_settings()

Base.metadata.create_all(bind=engine)


def create_owner():
    email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "")

    if not email or not password:
        raise RuntimeError(
            "ADMIN_EMAIL va ADMIN_PASSWORD sozlanmagan."
        )

    db = SessionLocal()

    try:
        user = db.scalar(
            select(User).where(User.email == email)
        )

        if user is None:
            user = User(
                email=email,
                password_hash=hash_password(password),
                is_admin=True,
                is_active=True,
            )
            db.add(user)
            db.commit()

        elif not user.is_admin:
            user.is_admin = True
            db.commit()

    finally:
        db.close()


create_owner()


app = FastAPI(
    title="Nexora API",
    description="Nexora independent Android application marketplace",
    version="1.0.0",
)


cors_origins = [
    item.strip()
    for item in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000"
    ).split(",")
    if item.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication"],
)

app.include_router(
    apps_router,
    prefix="/api/apps",
    tags=["Applications"],
)

app.include_router(
    admin_router,
    prefix="/api/admin",
    tags=["Admin"],
)


@app.get("/")
def root():
    return {
        "name": "Nexora",
        "status": "online",
        "version": "1.0.0",
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "nexora-backend",
    }
