from typing import List
from pathlib import Path
import csv
import logging
from models.pferd import Pferd
from models.futter import Heu, Heulage
from utils.validation import validate_pferd, validate_heu, validate_heulage

logger = logging.getLogger(__name__)

DATA_DIR = (Path(__file__).parent.parent / "data").resolve()

def lade_pferde_als_dataclasses(dateiname: str) -> List[Pferd]:
    pfad = DATA_DIR / dateiname
    pferde_liste = []
    with pfad.open(newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if validate_pferd(row):
                pferd = Pferd(
                    name=row['Name'],  # Großgeschrieben
                    gewicht=float(row['Gewicht']),  # Großgeschrieben
                    alter=int(row['Alter']),  # Großgeschrieben
                    notizen=row.get('Notizen', '')
                )
                pferde_liste.append(pferd)
            else:
                logger.warning(f"Ungültige Pferdedaten übersprungen: {row}")
    return pferde_liste

def lade_heu_als_dataclasses(dateiname: str) -> List[Heu]:
    pfad = DATA_DIR / dateiname
    heu_liste = []
    with pfad.open(newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if validate_heu(row):
                heu = Heu(
                    name=pfad.stem,
                    trockenmasse=float(row['Trockensubstanz']),
                    rohprotein=float(row['Rohprotein']),
                    rohfaser=float(row['Rohfaser']),
                    gesamtzucker=float(row['Gesamtzucker']),
                    fruktan=float(row['Fruktan']),
                    me_pferd=float(row['ME-Pferd']),
                    pcv_xp=float(row.get('pcv_XP', 0)),
                    herkunft=row.get('Herkunft'),
                    jahrgang=int(row.get('Jahrgang', 2025)),
                    staubarm=None  # Optional, falls vorhanden
                )
                heu_liste.append(heu)
            else:
                logger.warning(f"Ungültige Heudaten übersprungen: {row}")
    return heu_liste

def lade_heulage_als_dataclasses(dateiname: str) -> List[Heulage]:
    pfad = DATA_DIR / dateiname
    heulage_liste = []
    with pfad.open(newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if validate_heulage(row):
                heulage = Heulage(
                    name=pfad.stem,
                    trockenmasse=float(row['Trockensubstanz']),
                    rohprotein=float(row['Rohprotein']),
                    rohfaser=float(row['Rohfaser']),
                    gesamtzucker=float(row['Gesamtzucker']),
                    fruktan=float(row['Fruktan']),
                    me_pferd=float(row['ME-Pferd']),
                    pcv_xp=float(row.get('pcv_XP', 0)),
                    herkunft=row.get('Herkunft'),
                    jahrgang=int(row.get('Jahrgang', 2025)),
                    ph_wert=float(row.get('pH-Wert', 0)),
                    siliergrad=row.get('Siliergrad')
                )
                heulage_liste.append(heulage)
            else:
                logger.warning(f"Ungültige Heulagedaten übersprungen: {row}")
    return heulage_liste

