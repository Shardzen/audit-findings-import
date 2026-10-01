import csv
import io
from datetime import date, datetime

from fastapi import APIRouter, Depends, File, Query ,UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Finding
from app.security import require_role

router = APIRouter(prefix="/imports", tags=["imports"])

COLONNES_OBLIGATOIRES = ["ref", "asset", "title", "severity", "detected_on"]
SEVERITES_VALIDES = ["faible", "moyenne", "forte"]


def valider_ligne(row: dict) -> list[str]:
    erreurs = []
    if not row.get("ref"):
        erreurs.append("ref manquante")
    if not row.get("asset"):
        erreurs.append("asset est vide")
    if not row.get("title"):
        erreurs.append("title manquant")
    if row.get("severity") not in SEVERITES_VALIDES:
        erreurs.append("severity doit valoir faible, moyenne ou forte")
    try:
        datetime.strptime(row.get("detected_on", ""), "%Y-%m-%d")
    except (ValueError, TypeError):
        erreurs.append("detected_on doit être une date YYYY-MM-DD valide")
    return erreurs


@router.post("")
async def import_csv(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, alias="dry-run", description="Simule l'import sans écrire en BDD"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("auditeur")),
):
    content = await file.read()
    decoded = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))

    missing_columns = [c for c in COLONNES_OBLIGATOIRES if c not in (reader.fieldnames or [])]
    if missing_columns:
        from app.errors import AppError
        raise AppError(
            422, "validation_error",
            f"Colonnes obligatoires manquantes : {', '.join(missing_columns)}",
        )

    total_lines = 0
    inserted = 0
    duplicates_existing = 0
    duplicates_in_file = 0
    rejected = []
    refs_in_file = set()

    for i, row in enumerate(reader, start=2): 
        total_lines += 1
        ref = row.get("ref")

        erreurs = valider_ligne(row)
        if erreurs:
            rejected.append({"line": i, "ref": ref or "", "errors": erreurs})
            continue

        if ref in refs_in_file:
            duplicates_in_file += 1
            continue

        already_exists = db.query(Finding).filter(Finding.ref == ref).first()
        if already_exists:
            duplicates_existing += 1
            refs_in_file.add(ref)
            continue

        finding = Finding(
            ref=ref,
            asset=row["asset"],
            title=row["title"],
            severity=row["severity"],
            detected_on=datetime.strptime(row["detected_on"], "%Y-%m-%d").date(),
            status="ouvert",
        )
        db.add(finding)
        refs_in_file.add(ref)
        inserted += 1

    if dry_run:
        db.rollback()
    else:
        db.commit()

    return {
        "total_lines": total_lines,
        "inserted": inserted,
        "duplicates_existing": duplicates_existing,
        "duplicates_in_file": duplicates_in_file,
        "rejected_count": len(rejected),
        "rejected": rejected,
    }