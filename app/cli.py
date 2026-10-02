"""Commande en ligne : python cli.py import fichier.csv [--dry-run]"""
import argparse
import json
import sys

from app.db import SessionLocal, init_db
from app.services.import_service import ImportRejected, process_csv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="import-findings")
    parser.add_argument("args", nargs="+", metavar="[import] chemin.csv")
    parser.add_argument("--dry-run", action="store_true", help="Valider et afficher le bilan sans rien écrire")
    ns = parser.parse_args(argv)

    args = ns.args[1:] if ns.args[0] == "import" else ns.args
    if len(args) != 1:
        parser.error("un seul fichier CSV attendu")

    init_db()
    try:
        with open(args[0], "rb") as f:
            content = f.read()
    except OSError as exc:
        print(json.dumps({"error": "file_unreadable", "message": exc.strerror}, ensure_ascii=False))
        return 1

    with SessionLocal() as db:
        try:
            report = process_csv(content, db, dry_run=ns.dry_run)
        except ImportRejected as exc:
            print(json.dumps({"error": exc.error, "message": exc.message, **exc.extra}, ensure_ascii=False))
            return 1

    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
