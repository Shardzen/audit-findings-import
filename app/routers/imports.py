from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.errors import AppError
from app.security import require_role
from app.services.import_service import ImportRejected, process_csv

router = APIRouter(tags=["imports"])

MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@router.post("/imports")
async def import_findings(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(require_role("auditeur")),
):
    if not (file.filename or "").lower().endswith(".csv"):
        raise AppError(415, "unsupported_media_type", "Le fichier doit être un CSV (.csv)")

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise AppError(413, "file_too_large", "Le fichier dépasse la taille maximale autorisée")

    try:
        return process_csv(content, db)
    except ImportRejected as exc:
        raise AppError(422, exc.error, exc.message, **exc.extra)
