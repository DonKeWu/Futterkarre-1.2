import os
import csv
from models.futter import Heu, Heulage

def lade_heu_aus_csv(pfad: str) -> Heu:
    with open(pfad, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader)  # Nur die erste Zeile, da Analysewerte meist 1 Zeile
        return Heu(
            name=os.path.splitext(os.path.basename(pfad))[0],
            trockenmasse=float(row['Trockensubstanz']),
            rohprotein=float(row['Rohprotein']),
            rohfaser=float(row['Rohfaser']),
            gesamtzucker=float(row['Gesamtzucker']),
            fruktan=float(row['Fruktan']),
            me_pferd=float(row['ME-Pferd']),
            pcv_xp=float(row.get('pcv_XP', 0)),
            herkunft=None,
            jahrgang=int(row.get('Jahrgang', 2025))
        )

def lade_heulage_aus_csv(pfad: str) -> Heulage:
    with open(pfad, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader)
        return Heulage(
            name=os.path.splitext(os.path.basename(pfad))[0],
            trockenmasse=float(row['Trockensubstanz']),
            rohprotein=float(row['Rohprotein']),
            rohfaser=float(row['Rohfaser']),
            gesamtzucker=float(row['Gesamtzucker']),
            fruktan=float(row['Fruktan']),
            me_pferd=float(row['ME-Pferd']),
            pcv_xp=0,
            herkunft=None,
            jahrgang=int(row.get('Jahrgang', 2025)),
            ph_wert=float(row.get('pH-Wert', 0)),
            siliergrad=None
        )
