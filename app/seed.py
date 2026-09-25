"""Crée les comptes de test : python -m app.seed
Mots de passe lus dans l'environnement (jamais en dur dans le dépôt)."""
import os
import secrets

from app.db import SessionLocal, init_db
from app.models import User
from app.security import hash_password


def main():
    init_db()
    with SessionLocal() as db:
        for username, role in (("auditeur", "auditeur"), ("responsable", "responsable")):
            if db.query(User).filter_by(username=username).first():
                print(f"{username} existe déjà")
                continue
            pwd = os.environ.get(f"SEED_{role.upper()}_PASSWORD") or secrets.token_urlsafe(12)
            db.add(User(username=username, password_hash=hash_password(pwd), role=role))
            print(f"{username} ({role}) créé, mot de passe : {pwd}")
        db.commit()


if __name__ == "__main__":
    main()
