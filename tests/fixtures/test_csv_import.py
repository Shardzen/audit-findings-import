import os
import csv
from api import FastAPI

with open('01_valide.csv', "r", encoding="utf-8") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)

with open('02_colonne_manquante.csv', "r", encoding="utf-8") as fichier:
    reader = csv.DictReader(fichier)
    for ligne in reader:
        print(ligne)
