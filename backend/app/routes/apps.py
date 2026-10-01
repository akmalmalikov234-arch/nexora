import hashlib
import io
import os
import re
import uuid
import zipfile
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import App, User
from ..schemas import AppResponse
from ..security import get_current_user


router = APIRouter()


UPLOAD_DIR = Path(
    os.getenv("UPLOAD_DIR", "uploads")
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


MAX_UPLOAD_MB = int(
    os.getenv("MAX_UPLOAD_MB", "50")
)

MAX_UPLOAD_BYTES = (
    MAX_UPLOAD_MB * 1024 * 1024
)

MAX_UNCOMPRESSED_BYTES = 500 * 1024 * 1024
MAX_ZIP_ENTRIES = 20000


PACKAGE_PATTERN = re.compile(
    r"^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)+$"
)


def validate_apk_file(path: Path):
    try:
        with path.open("rb") as file:
            signature = file.read(4)

        if signature != b"PK\x03\x04":
            raise ValueError(
                "Fayl haqiqiy APK ZIP tuzilmasiga o'xshamaydi."
            )

        with zipfile.ZipFile(path, "r") as archive:

            bad_file = archive.testzip()

            if bad_file:
                raise ValueError(
                    "APK ichidagi ZIP ma'lumotlari buzilgan."
                )

            names = archive.namelist()

            if "AndroidManifest.xml" not in names:
                raise ValueError(
                    "AndroidManifest.xml topilmadi."
                )

            if len(names) > MAX_ZIP_ENTRIES:
                raise ValueError(
                    "APK ichidagi fayllar soni juda katta."
                )

            total_uncompressed = 0

            for info in archive.infolist():

                if info.filename.startswith("/"):
                    raise ValueError(
                        "APK ichida xavfli path topildi."
                    )

                parts = Path(info.filename).parts

                if ".." in parts:
                    raise ValueError(
                        "APK ichida xavfli path topildi."
                    )

                if info.file_size > MAX_UNCOMPRESSED_BYTES:
                    raise ValueError(
                        "APK ichidagi fayl juda katta."
                    )

                total_uncompressed += info.file_size

                if total_uncompressed > MAX_UNCOMPRESSED_BYTES:
                    raise ValueError(
                        "APK ichidagi umumiy ochiladigan hajm juda katta."
                    )

                if info.compress_size > 0:
                    ratio = (
                        info.file_size /
                        info.compress_size
                    )

                    if ratio > 200:
                        raise ValueError(
                            "Shubhali ZIP compression ratio."
                        )

    except zipfile.BadZipFile:
        raise ValueError(
            "APK ZIP tuzilmasi buzilgan."
        )


async def save_uploaded_apk(
    upload: UploadFile
):
    filename = upload.filename or ""

    if not filename.lower().endswith(".apk"):
        raise HTTPException(
            status_code=400,
            detail="Faqat APK fayl qabul qilinadi."
        )

    safe_name = (
        f"{uuid.uuid4().hex}.apk"
    )

    destination = UPLOAD_DIR / safe_name

    sha256 = hashlib.sha256()
    total_size = 0

    try:
        with destination.open("wb") as output:

            while True:
                chunk = await upload.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            f"APK hajmi {MAX_UPLOAD_MB} MB dan "
                            "oshmasligi kerak."
                        )
                    )

                sha256.update(chunk)
                output.write(chunk)

        validate_apk_file(destination)

    except HTTPException:
        destination.unlink(
            missing_ok=True
        )
        raise

    except Exception as error:
        destination.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=400,
            detail=f"APK tekshiruvdan o'tmadi: {error}"
        )

    return (
        destination,
        safe_name,
        total_size,
        sha256.hexdigest()
    )


@router.get(
    "",
    response_model=list[AppResponse]
)
def list_apps(
    q: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db)
):
    query = select(App).where(
        App.status == "approved"
    )

    if q:
        search = f"%{q.strip()}%"

        query = query.where(
            (App.name.ilike(search)) |
            (App.description.ilike(search)) |
            (App.package_name.ilike(search))
        )

    if category:
        query = query.where(
            App.category == category
        )

    query = query.order_by(
        App.created_at.desc()
    )

    return db.scalars(query).all()


@router.get(
    "/{app_id}",
    response_model=AppResponse
)
def get_app(
    app_id: int,
    db: Session = Depends(get_db)
):
    app = db.get(App, app_id)

    if app is None or app.status != "approved":
        raise HTTPException(
            status_code=404,
            detail="Ilova topilmadi."
        )

    return app


@router.post(
    "/upload",
    response_model=AppResponse
)
async def upload_app(
    name: str = Form(...),
    package_name: str = Form(...),
    version: str = Form(...),
    description: str = Form(""),
    category: str = Form("Boshqa"),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    name = name.strip()
    package_name = package_name.strip()
    version = version.strip()
    description = description.strip()
    category = category.strip() or "Boshqa"

    if len(name) < 2 or len(name) > 150:
        raise HTTPException(
            status_code=400,
            detail="Ilova nomi 2-150 belgi bo'lishi kerak."
        )

    if not PACKAGE_PATTERN.match(
        package_name
    ):
        raise HTTPException(
            status_code=400,
            detail="Package name noto'g'ri."
        )

    if len(version) > 50:
        raise HTTPException(
            status_code=400,
            detail="Version juda uzun."
        )

    (
        path,
        stored_name,
        size,
        sha256
    ) = await save_uploaded_apk(file)

    duplicate = db.scalar(
        select(App).where(
            App.sha256 == sha256
        )
    )

    if duplicate:
        path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=409,
            detail="Bu APK oldin yuklangan."
        )

    app = App(
        name=name,
        package_name=package_name,
        version=version,
        description=description,
        category=category,
        file_name=file.filename,
        file_path=str(path),
        sha256=sha256,
        size_bytes=size,
        download_count=0,
        status="pending",
        uploader_id=user.id,
    )

    db.add(app)
    db.commit()
    db.refresh(app)

    return app


@router.get(
    "/{app_id}/download"
)
def download_app(
    app_id: int,
    db: Session = Depends(get_db)
):
    app = db.get(App, app_id)

    if app is None:
        raise HTTPException(
            status_code=404,
            detail="Ilova topilmadi."
        )

    if app.status != "approved":
        raise HTTPException(
            status_code=403,
            detail="Bu ilova hozir yuklab olinmaydi."
        )

    path = Path(app.file_path)

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="APK fayli serverda topilmadi."
        )

    app.download_count += 1
    db.commit()

    return FileResponse(
        path=path,
        media_type=(
            "application/vnd.android.package-archive"
        ),
        filename=app.file_name,
    )
