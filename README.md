# audit-findings-import

# Import contrôlé de résultats d'audit

API et commande en ligne permettant d'importer des constats d'audit (fichiers CSV), de les consulter, et de les marquer comme corrigés. Les lignes invalides et les doublons sont détectés et expliqués sans bloquer l'import des lignes valides.

## Prérequis et installation

- Python 3.11+
- Un environnement virtuel (`venv`)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
 
```

### Variables d'environnement

Copier `.env.example` en `.env` et ajuster si besoin :

DATABASE_URL=sqlite:///./audit.db
JWT_SECRET=change-moi-en-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
SEED_AUDITEUR_PASSWORD=
SEED_RESPONSABLE_PASSWORD=


Si `SEED_AUDITEUR_PASSWORD` / `SEED_RESPONSABLE_PASSWORD` sont laissés vides, des mots de passe aléatoires sont générés et affichés une seule fois lors du seed.

La base de données par défaut est SQLite (fichier local `audit.db`), aucune installation supplémentaire requise.

## Lancer l'API

```powershell
uvicorn app.main:app --reload
```
Si API ne se lance pas immédiatement, installer la dépendance pip install python-multipart

L'API est alors disponible sur `http://127.0.0.1:8000`, avec la documentation interactive sur `http://127.0.0.1:8000/docs`.

## Créer les utilisateurs de test

```powershell
python -m app.seed
```

Crée un utilisateur `auditeur` et un utilisateur `responsable`. Les mots de passe générés sont affichés une seule fois dans le terminal — à conserver.

## Lancer la commande d'import

```powershell
python -m app.cli import fichier.csv
```


## Tableau des routes

| Méthode | Chemin | Rôle requis | Codes de retour |
|---|---|---|---|
| POST | /token | aucun | 200, 401 |
| POST | /imports | auditeur | 201, 400/422, 401, 403 |
| GET | /findings | auditeur, responsable | 200, 401, 422 |
| GET | /findings/{id} | auditeur, responsable | 200, 404, 401 |
| PATCH | /findings/{id}/resolve | responsable | 200, 401, 403, 404, 409 |

## Règles d'import (R1 à R6)

| # | Règle | Conséquence |
|---|---|---|
| R1 | Colonne obligatoire manquante dans les en-têtes | Fichier rejeté entièrement, rien n'est écrit en base |
| R2 | Colonnes en plus | Ignorées, l'import continue normalement |
| R3 | En-têtes corrects, certaines lignes invalides | Lignes valides conservées, invalides listées avec leur raison |
| R4 | La ref existe déjà en base | Ligne ignorée, constat existant non modifié, comptée comme doublon |
| R5 | La même ref apparaît plusieurs fois dans le fichier | Première ligne valide gardée, les suivantes sont des doublons |
| R6 | Marquer corrigé un constat déjà corrigé | Refus avec 409 Conflict |

### Format du bilan d'import

```json
{
  "total_lines": 6,
  "inserted": 1,
  "duplicates_existing": 1,
  "duplicates_in_file": 1,
  "rejected_count": 3,
  "rejected": [
    {"line": 4, "ref": "AUD-011", "errors": ["asset est vide"]}
  ]
}
```

## Lancer les tests

```powershell
pytest
```

## Choix de sécurité

- Mots de passe hachés (bcrypt), jamais stockés en clair.
- Authentification par JWT, transmis via `Authorization: Bearer <token>`.
- Contrôle d'accès par rôle (auditeur / responsable) sur chaque route sensible.
- Requêtes paramétrées via l'ORM (SQLAlchemy) : pas de concaténation de chaînes SQL, protection contre l'injection SQL.
- Pagination plafonnée (`per_page` max 100) pour éviter un déni de service.
- Mise à jour atomique conditionnelle sur `PATCH /resolve` (`WHERE status='ouvert'`) pour éviter les conditions de course.
- Messages d'erreur génériques côté client (`error` / `message`), sans trace de pile ni détail interne.
- Secrets (JWT, mots de passe) jamais commités : fichier `.env` ignoré par Git, `.env.example` fourni.
- Entrées CSV pouvant déclencher une injection de formule (`=`, `+`, `-`, `@`) stockées telles quelles mais neutralisées à l'export.

## Exemples curl

### 1. Connexion
```bash
curl -X POST http://localhost:8000/token \
  -d "username=auditeur&password=***"
```

### 2. Import (auditeur)
```bash
curl -X POST http://localhost:8000/imports \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@tests/fixtures/04_lignes_mixtes.csv"
```

### 3. Lister
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/findings?severity=forte&page=1"
```

### 4. Consulter
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/findings/12
```

### 5. Corriger (responsable)
```bash
curl -X PATCH -H "Authorization: Bearer $TOKEN_RESP" \
  http://localhost:8000/findings/12/resolve
```