import os
import csv
#from api import FastAPI

with open('01_valide.csv', "r", encoding="utf-8") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

with open('02_colonne_manquante.csv', "r", encoding="utf-8") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

with open('03_colonnes_en_plus.csv', "r", encoding="utf-8") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)


with open('04_lignes_mixtes.csv', "r", encoding="utf-8") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

with open('05_doublons_internes.csv', "r", encoding="utf-8") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

with open('06_premier_invalide.csv', "r", encoding="utf-8") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

with open('07_reimport.csv', "r", encoding="utf-8") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)