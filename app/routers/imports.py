import csv
import io
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Finding
from app.security import get_current_user, require_role
from datetime import datetime

router = APIRouter(prefix="/imports", tags=["imports"])

@router.post("")
async def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("auditeur")),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="Le fichier doit être au format CSV"
        )

    content = await file.read()
    decoded = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))

    imported_findings = []
    for row in reader:
        raw_date = row.get("detected_on")
        if raw_date:
            try:
                detected_on_val = datetime.strptime(
                    raw_date.strip(), "%Y-%m-%d"
                ).date()
            except ValueError:
                detected_on_val = datetime.utcnow().date()
        else:
            detected_on_val = datetime.utcnow().date()

        finding = Finding(
            ref=row.get("ref"),
            asset=row.get("asset"),
            title=row.get("title"),
            severity=row.get("severity"),
            detected_on=detected_on_val,
            status="ouvert",
        )
        db.add(finding)
        imported_findings.append(finding)

    db.commit()

    return {
        "message": f"{len(imported_findings)} constats importés avec succès"
    }