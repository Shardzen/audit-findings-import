import os
import csv
#from api import FastAPI
from datetime import datetime

with open('01_valide.csv', "r", encoding="utf-8-sig") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

with open('02_colonne_manquante.csv', "r", encoding="utf-8-sig") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

with open('03_colonnes_en_plus.csv', "r", encoding="utf-8-sig") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)


with open('04_lignes_mixtes.csv', "r", encoding="utf-8-sig") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

with open('05_doublons_internes.csv', "r", encoding="utf-8-sig") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

with open('06_premier_invalide.csv', "r", encoding="utf-8-sig") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

with open('07_reimport.csv', "r", encoding="utf-8-sig") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

with open('08_bom.csv', "r", encoding="utf-8-sig") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

with open('09_vide.csv', "r", encoding="utf-8-sig") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

with open('10_ordre_colonnes.csv', "r", encoding="utf-8-sig") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

with open('11_espaces.csv', "r", encoding="utf-8-sig") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

with open('12_injection.csv', "r", encoding="utf-8-sig") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

def valider_ligne(ligne):
   
    erreurs = []

    if not ligne['ref']:
        erreurs.append("ref manquante")
    if not ligne['asset']:
        erreurs.append("asset est vide")
    if not ligne['title']:
        erreurs.append ("title manquant")
    if ligne['severity'] not in ['faible', 'moyenne', 'forte']:
        erreurs.append("severity doit valoir faible, moyenne ou forte")
    try:
        datetime.strptime(ligne['detected_on'], "%Y-%m-%d")
    except (ValueError, TypeError):
        erreurs.append("detected_on doit être une date YYYY-MM-DD valide")

    return erreurs



