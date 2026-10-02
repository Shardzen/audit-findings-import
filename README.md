# audit-findings-import

## Démarrage

```bash
python -m venv .venv
.venv/Scripts/activate  # .venv\Scripts\Activate.ps1 sous PowerShell
pip install -r requirements.txt
```

Variables d'environnement (`.env` ou export) :

- `JWT_SECRET` (obligatoire, ≥32 caractères)
- `DATABASE_URL` (défaut : `sqlite:///./app.db`)
- `JWT_EXPIRE_MINUTES` (défaut : 30)
- `SEED_AUDITEUR_PASSWORD` / `SEED_RESPONSABLE_PASSWORD` (optionnel, sinon générés aléatoirement)

Créer les comptes de test puis lancer l'API :

```bash
python -m app.seed
uvicorn app.main:app --reload
```

## Import en ligne de commande

```bash
python -m app.cli chemin/vers/fichier.csv
```

Affiche le même bilan JSON que `POST /imports` et retourne un code de sortie non nul si le fichier est rejeté.

## Tests

```bash
pytest
```