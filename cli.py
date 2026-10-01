import argparse
import csv
import io
import json
import sys
from pathlib import Path

from app.db import SessionLocal
from app.models import Finding

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
        from datetime import datetime
        datetime.strptime(row.get("detected_on", ""), "%Y-%m-%d")
    except (ValueError, TypeError):
        erreurs.append("detected_on doit être une date YYYY-MM-DD valide")
    return erreurs


def executer_import(chemin_fichier: Path, dry_run: bool = False):
    if not chemin_fichier.exists():
        print(json.dumps({"erreur": f"Fichier introuvable: {chemin_fichier}"}))
        sys.exit(1)

    with open(chemin_fichier, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        missing_columns = [c for c in COLONNES_OBLIGATOIRES if c not in (reader.fieldnames or [])]
        if missing_columns:
            print(json.dumps({"erreur": f"Colonnes obligatoires manquantes : {', '.join(missing_columns)}"}))
            sys.exit(1)

        db = SessionLocal()
        total_lines = 0
        inserted = 0
        duplicates_existing = 0
        duplicates_in_file = 0
        rejected = []
        refs_in_file = set()

        try:
            for i, row in enumerate(reader, start=2):  # L'en-tête est la ligne 1
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

            # Si dry-run, on annule l'écriture en base
            if dry_run:
                db.rollback()
            else:
                db.commit()

            bilan = {
                "total_lines": total_lines,
                "inserted": inserted,
                "duplicates_existing": duplicates_existing,
                "duplicates_in_file": duplicates_in_file,
                "rejected_count": len(rejected),
                "rejected": rejected,
            }
            print(json.dumps(bilan, indent=2, ensure_ascii=False))

        except Exception as e:
            db.rollback()
            print(json.dumps({"erreur": str(e)}))
            sys.exit(1)
        finally:
            db.close()


def main():
    parser = argparse.ArgumentParser(description="CLI Import CSV")
    parser.add_argument("command", choices=["import"], help="Commande d'import")
    parser.add_argument("fichier", type=str, help="Chemin du fichier CSV")
    parser.add_argument("--dry-run", action="store_true", help="Simule l'import sans écrire en BDD")

    args = parser.parse_args()

    if args.command == "import":
        executer_import(Path(args.fichier), dry_run=args.dry_run)


if __name__ == "__main__":
    main()