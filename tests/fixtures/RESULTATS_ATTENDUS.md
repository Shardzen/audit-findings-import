## 01_valide.csv

État de départ : base vide

{
  "total_lines": 5,
  "inserted": 5,
  "duplicates_existing": 0,
  "duplicates_in_file": 0,
  "rejected_count": 0,
  "rejected": []
}

## 03_colonnes_en_plus.csv

État de départ : base vide

{
  "total_lines": 3,
  "inserted": 3,
  "duplicates_existing": 0,
  "duplicates_in_file": 0,
  "rejected_count": 0,
  "rejected": []
}

# 02_colonne_manquante.csv
{
  "error": "validation_error",
  "message": "La colonne severity est manquante dans l'en-tête"
}


# 04 
# 04_lignes_mixtes.csv

État de départ : base vide

{
  "total_lines": 12,
  "inserted": 1,
  "duplicates_existing": 0,
  "duplicates_in_file": 0,
  "rejected_count": 11,
  "rejected": [
    {"line": 3, "ref": "", "errors": ["ref manquante"]},
    {"line": 4, "ref": "AUD-103", "errors": ["asset est vide"]},
    {"line": 5, "ref": "AUD-104", "errors": ["title est vide"]},
    {"line": 6, "ref": "AUD-105", "errors": ["severity doit valoir faible, moyenne ou forte"]},
    {"line": 7, "ref": "AUD-106", "errors": ["detected_on doit être une date YYYY-MM-DD valide"]},
    {"line": 8, "ref": "AUD-107", "errors": ["detected_on doit être une date YYYY-MM-DD valide"]},
    {"line": 9, "ref": "AUD-108", "errors": ["detected_on doit être une date YYYY-MM-DD valide"]},
    {"line": 10, "ref": "AUD-109", "errors": ["detected_on doit être une date YYYY-MM-DD valide"]},
    {"line": 11, "ref": "AUD-110", "errors": ["ligne contient plus de colonnes que prévu"]},
    {"line": 12, "ref": "AUD-111", "errors": ["severity manquant", "detected_on manquant"]},
    {"line": 13, "ref": "", "errors": ["ref manquante", "asset est vide", "severity doit valoir faible, moyenne ou forte", "detected_on doit être une date YYYY-MM-DD valide"]}
  ]
}

# 05_doublons_internes.csv
{
  "total_lines": 3,
  "inserted": 1,
  "duplicates_existing": 0,
  "duplicates_in_file": 2,
  "rejected_count": 0,
  "rejected": []
}

# 06_premier_invalide
{ 
  "total_lines": 2, 
  "inserted": 1, 
  "duplicates_existing": 0, 
  "duplicates_in_file": 0, 
  "rejected_count": 1, 
  "rejected": [{
    "line": 2, 
    "ref": "AUD-300", 
    "errors": ["severity doit valoir faible, moyenne ou forte"] }] 
}


## 07_reimport
base préparée : 01_valide.csv déjà importé, un constat marqué corrigé

{
  "total_lines": 5,
  "inserted": 0,
  "duplicates_existing": 5,
  "duplicates_in_file": 0,
  "rejected_count": 0,
  "rejected": []
}

# il faut aussi vérifier, en consultant la base (ou via GET /findings/{id}), que AUD-001 a toujours status: "corrige", et pas status: "ouvert".

# 08
{
  "total_lines": 2,
  "inserted": 2,
  "duplicates_existing": 0,
  "duplicates_in_file": 0,
  "rejected_count": 0,
  "rejected": []
}

# 09
{
  "total_lines": 0,
  "inserted": 0,
  "duplicates_existing": 0,
  "duplicates_in_file": 0,
  "rejected_count": 0,
  "rejected": []
}

# 10
{
  "total_lines": 3,
  "inserted": 3,
  "duplicates_existing": 0,
  "duplicates_in_file": 0,
  "rejected_count": 0,
  "rejected": []
}

# 11
{
  "total_lines": 2,
  "inserted": 1,
  "duplicates_existing": 0,
  "duplicates_in_file": 0,
  "rejected_count": 1,
  "rejected": [
    {"line": 3, "ref": "AUD-501", "errors": ["title est vide (après suppression des espaces)"]}
  ]
}

# 12_injection.csv

État de départ : base vide

Remarque : REF-604 a severity="critique" (invalide) dans le fichier actuel — à corriger en "forte" si l'intention était de tester uniquement l'injection sur une ligne par ailleurs valide.

{
  "total_lines": 4,
  "inserted": 3,
  "duplicates_existing": 0,
  "duplicates_in_file": 0,
  "rejected_count": 1,
  "rejected": [
    {"line": 5, "ref": "REF-604", "errors": ["severity doit valoir faible, moyenne ou forte"]}
  ]
}