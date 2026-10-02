"""Service d'import des constats d'audit, partagé par la route /imports et la CLI."""
import csv
import io
import re
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Finding

REQUIRED_COLUMNS = ["ref", "asset", "title", "severity", "detected_on"]
ALLOWED_SEVERITIES = {"faible", "moyenne", "forte"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ImportRejected(Exception):
    """Levée quand le fichier entier doit être rejeté, avant toute écriture."""

    def __init__(self, error: str, message: str, **extra):
        self.error, self.message, self.extra = error, message, extra
        super().__init__(message)


def _valid_date(value: str) -> bool:
    if not DATE_RE.match(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def _row_errors(row: dict[str, str]) -> list[str]:
    errors = []
    if not row["ref"]:
        errors.append("ref est requis")
    if not row["asset"]:
        errors.append("asset est requis")
    if not row["title"]:
        errors.append("title est requis")
    if row["severity"] not in ALLOWED_SEVERITIES:
        errors.append("severity doit être l'une de : faible, moyenne, forte")
    if not _valid_date(row["detected_on"]):
        errors.append("detected_on doit être une date valide au format AAAA-MM-JJ")
    return errors


def process_csv(content: bytes, db: Session, dry_run: bool = False) -> dict:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ImportRejected("invalid_encoding", "Le fichier doit être encodé en UTF-8")

    reader = csv.reader(io.StringIO(text))
    header = [h.strip() for h in next(reader, [])]

    missing = [c for c in REQUIRED_COLUMNS if c not in header]
    if missing:
        raise ImportRejected("missing_columns", "Colonnes obligatoires manquantes", missing_columns=missing)

    col_index = {name: i for i, name in enumerate(header)}
    n_cols = len(header)

    rejected: list[dict] = []
    valid_rows: list[tuple[int, dict]] = []

    for offset, raw_row in enumerate(reader):
        if not raw_row:
            continue
        line_no = offset + 2  # la ligne 1 est l'en-tête
        if len(raw_row) != n_cols:
            ref_guess = raw_row[col_index["ref"]].strip() if len(raw_row) > col_index["ref"] else None
            rejected.append({"line": line_no, "ref": ref_guess or None,
                              "errors": ["nombre de colonnes incorrect"]})
            continue

        row = {name: raw_row[idx].strip() for name, idx in col_index.items()}
        errors = _row_errors(row)
        if errors:
            rejected.append({"line": line_no, "ref": row["ref"] or None, "errors": errors})
        else:
            valid_rows.append((line_no, row))

    total_lines = len(valid_rows) + len(rejected)

    existing_refs: set[str] = set()
    file_refs = {row["ref"] for _, row in valid_rows}
    if file_refs:
        existing_refs = set(db.scalars(select(Finding.ref).where(Finding.ref.in_(file_refs))))

    seen_in_file: set[str] = set()
    duplicates_in_file = 0
    duplicates_existing = 0
    to_insert: list[dict] = []

    for _, row in valid_rows:
        ref = row["ref"]
        if ref in seen_in_file:
            duplicates_in_file += 1
            continue
        seen_in_file.add(ref)
        if ref in existing_refs:
            duplicates_existing += 1
            continue
        to_insert.append(row)

    if dry_run:
        to_write: list[dict] = []
        inserted = len(to_insert)
    else:
        to_write = to_insert
        inserted = 0
    for row in to_write:
        finding = Finding(
            ref=row["ref"],
            asset=row["asset"],
            title=row["title"],
            severity=row["severity"],
            detected_on=datetime.strptime(row["detected_on"], "%Y-%m-%d").date(),
        )
        try:
            with db.begin_nested():
                db.add(finding)
                db.flush()
        except IntegrityError:
            continue
        inserted += 1

    db.commit()

    rejected.sort(key=lambda r: r["line"])
    return {
        "total_lines": total_lines,
        "inserted": inserted,
        "duplicates_existing": duplicates_existing,
        "duplicates_in_file": duplicates_in_file,
        "rejected_count": len(rejected),
        "rejected": rejected,
    }
