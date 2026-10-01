import os
import csv
from pathlib import Path
from datetime import datetime

FIXTURES_DIR = Path(__file__).parent 

def valider_ligne(ligne):
    erreurs = []

    if not ligne.get("ref"):
        erreurs.append("ref manquante")
    if not ligne.get("asset"):
        erreurs.append("asset est vide")
    if not ligne.get("title"):
        erreurs.append("title manquant")
    if ligne.get("severity") not in ["faible", "moyenne", "forte"]:
        erreurs.append("severity doit valoir faible, moyenne ou forte")

    try:
        datetime.strptime(ligne.get("detected_on", ""), "%Y-%m-%d")
    except (ValueError, TypeError):
        erreurs.append("detected_on doit être une date YYYY-MM-DD valide")

    return erreurs

def lire_fixture(nom_fichier):
    chemin_fichier = FIXTURES_DIR / nom_fichier
    with open(chemin_fichier, "r", encoding="utf-8-sig") as fichier:
        reader = csv.DictReader(fichier)
        return list(reader)


def lire_fixture(nom_fichier):
    chemin_fichier = FIXTURES_DIR / nom_fichier
    with open(chemin_fichier, "r", encoding="utf-8-sig") as fichier:
        reader = csv.DictReader(fichier)
        return list(reader)


def test_01_valide():
    lignes = lire_fixture("01_valide.csv")
    assert len(lignes) > 0
    for ligne in lignes:
        assert len(valider_ligne(ligne)) == 0


def test_02_colonne_manquante():
    lignes = lire_fixture("02_colonne_manquante.csv")
    assert any(len(valider_ligne(l)) > 0 for l in lignes)


def test_03_colonnes_en_plus():
    lignes = lire_fixture("03_colonnes_en_plus.csv")
    assert len(lignes) > 0
    for ligne in lignes:
        assert len(valider_ligne(ligne)) == 0


def test_04_lignes_mixtes():
    lignes = lire_fixture("04_lignes_mixtes.csv")
    erreurs_par_ligne = [valider_ligne(l) for l in lignes]
    assert any(len(err) == 0 for err in erreurs_par_ligne)
    assert any(len(err) > 0 for err in erreurs_par_ligne)


def test_05_doublons_internes():
    lignes = lire_fixture("05_doublons_internes.csv")
    refs = [l.get("ref") for l in lignes]
    assert len(refs) != len(set(refs))


def test_06_premier_invalide():
    lignes = lire_fixture("06_premier_invalide.csv")
    assert len(valider_ligne(lignes[0])) > 0


def test_07_reimport():
    lignes = lire_fixture("07_reimport.csv")
    assert len(lignes) > 0


def test_08_bom():
    lignes = lire_fixture("08_bom.csv")
    assert "ref" in lignes[0]


def test_09_vide():
    lignes = lire_fixture("09_vide.csv")
    assert len(lignes) == 0


def test_10_ordre_colonnes():
    lignes = lire_fixture("10_ordre_colonnes.csv")
    assert len(lignes) > 0
    for ligne in lignes:
        assert len(valider_ligne(ligne)) == 0


def test_11_espaces():
    lignes = lire_fixture("11_espaces.csv")
    assert len(lignes) > 0


def test_12_injection():
    lignes = lire_fixture("12_injection.csv")
    assert len(lignes) > 0