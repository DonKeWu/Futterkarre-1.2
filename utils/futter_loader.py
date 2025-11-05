from typing import List, Dict, Any
from pathlib import Path
import csv
import logging
from models.pferd import Pferd
from models.futter import Heu, Heulage
from utils.validation import validate_pferd, validate_heu, validate_heulage
from utils.csv_validator import csv_validator

logger = logging.getLogger(__name__)

DATA_DIR = (Path(__file__).parent.parent / "data").resolve()

def lade_pferde_als_dataclasses(dateiname: str) -> List[Pferd]:
    """Lädt Pferde mit robuster CSV-Validierung"""
    pfad = DATA_DIR / dateiname
    
    # CSV-Validierung
    validation_result = csv_validator.validate_csv_file(pfad, 'pferde')
    
    if not validation_result['success']:
        logger.error(f"CSV-Validierung fehlgeschlagen für {dateiname}: {validation_result['error']}")
        logger.warning("Verwende Fallback-Pferd")
        fallback_data = csv_validator.get_fallback_data('pferde')
        return [Pferd(**data) for data in fallback_data]
    
    # Warnungen loggen
    for warning in validation_result['warnings']:
        logger.warning(warning)
    
    # Fehler loggen (aber trotzdem gültige Zeilen verwenden)
    for error in validation_result['errors']:
        logger.error(error)
    
    pferde_liste = []
    # Fallback, wenn validation_result noch altes Format hat
    data_key = 'data' if 'data' in validation_result else 'valid_rows'
    for row_data in validation_result[data_key]:
        # Nur aktive Pferde mit Namen laden
        if row_data.get('Aktiv', 'true').lower() == 'true' and row_data.get('Name'):
            pferd = Pferd(
                name=row_data['Name'],
                gewicht=float(row_data['Gewicht']),
                alter=int(row_data['Alter']),
                box=int(row_data.get('Box', row_data.get('Folge', 1))),
                aktiv=True,
                notizen=row_data.get('Notizen', '')
            )
            pferde_liste.append(pferd)
        else:
            logger.info(f"Leere Box übersprungen: Box {row_data.get('Box', '?')}")
    
    # Nach Box-Nummer sortieren
    pferde_liste.sort(key=lambda p: p.box)
    logger.info(f"{len(pferde_liste)} Pferde erfolgreich geladen mit CSV-Validierung")
    return pferde_liste

def lade_heu_als_dataclasses(dateiname: str) -> List[Heu]:
    """Lädt Heu mit robuster CSV-Validierung"""
    pfad = DATA_DIR / dateiname
    
    # CSV-Validierung
    validation_result = csv_validator.validate_csv_file(pfad, 'heu')
    
    if not validation_result['success']:
        logger.error(f"CSV-Validierung fehlgeschlagen für {dateiname}: {validation_result['error']}")
        logger.warning("Verwende Fallback-Heu")
        fallback_data = csv_validator.get_fallback_data('heu')
        return [Heu(name=pfad.stem, **data) for data in fallback_data]
    
    # Warnungen und Fehler loggen
    for warning in validation_result['warnings']:
        logger.warning(warning)
    for error in validation_result['errors']:
        logger.error(error)
    
    heu_liste = []
    # Fallback, wenn validation_result noch altes Format hat
    data_key = 'data' if 'data' in validation_result else 'valid_rows'
    for row_data in validation_result[data_key]:
        heu = Heu(
            name=pfad.stem,  # Dateiname als Heu-Name
            trockenmasse=float(row_data['Trockensubstanz']),
            rohprotein=float(row_data['Rohprotein']),
            rohfaser=float(row_data['Rohfaser']),
            gesamtzucker=float(row_data['Gesamtzucker']),
            fruktan=float(row_data['Fruktan']),
            me_pferd=float(row_data['ME-Pferd']),
            pcv_xp=float(row_data.get('pcv_XP', 0)),
            herkunft=row_data.get('Herkunft', 'Eigen'),
            jahrgang=int(row_data.get('Jahrgang', 2025)),
            staubarm=None  # Optional
        )
        heu_liste.append(heu)
    
    logger.info(f"{len(heu_liste)} Heu-Einträge erfolgreich geladen mit CSV-Validierung")
    return heu_liste

def lade_heulage_als_dataclasses(dateiname: str) -> List[Heulage]:
    """Lädt Heulage mit robuster CSV-Validierung"""
    pfad = DATA_DIR / dateiname
    
    # CSV-Validierung
    validation_result = csv_validator.validate_csv_file(pfad, 'heulage')
    
    if not validation_result['success']:
        logger.error(f"CSV-Validierung fehlgeschlagen für {dateiname}: {validation_result['error']}")
        logger.warning("Verwende Fallback-Heulage")
        fallback_data = csv_validator.get_fallback_data('heulage')
        return [Heulage(name=pfad.stem, **data) for data in fallback_data]
    
    # Warnungen und Fehler loggen
    for warning in validation_result['warnings']:
        logger.warning(warning)
    for error in validation_result['errors']:
        logger.error(error)
    
    heulage_liste = []
    # Fallback, wenn validation_result noch altes Format hat
    data_key = 'data' if 'data' in validation_result else 'valid_rows'
    for row_data in validation_result[data_key]:
        heulage = Heulage(
            name=pfad.stem,  # Dateiname als Heulage-Name
            trockenmasse=float(row_data['Trockensubstanz']),
            rohprotein=float(row_data['Rohprotein']),
            rohfaser=float(row_data['Rohfaser']),
            gesamtzucker=float(row_data['Gesamtzucker']),
            fruktan=float(row_data['Fruktan']),
            me_pferd=float(row_data['ME-Pferd']),
            pcv_xp=float(row_data.get('pcv_XP', 0)),
            herkunft=row_data.get('Herkunft', 'Eigen'),
            jahrgang=int(row_data.get('Jahrgang', 2025)),
            ph_wert=float(row_data.get('pH-Wert', 4.5)),
            siliergrad=row_data.get('Siliergrad', 'gut')
        )
        heulage_liste.append(heulage)
    
    logger.info(f"{len(heulage_liste)} Heulage-Einträge erfolgreich geladen mit CSV-Validierung")
    return heulage_liste

def get_available_files() -> List[str]:
    """
    Holt verfügbare CSV-Dateien aus dem data-Ordner
    
    Returns:
        Liste der verfügbaren Dateinamen
    """
    try:
        csv_files = []
        if DATA_DIR.exists():
            for file_path in DATA_DIR.glob("*.csv"):
                csv_files.append(file_path.name)
        
        csv_files.sort()
        logger.debug(f"Gefundene CSV-Dateien: {csv_files}")
        return csv_files
        
    except Exception as e:
        logger.error(f"Fehler beim Laden der verfügbaren Dateien: {e}")
        return []

def load_futter_data(dateiname: str) -> Dict[str, Any]:
    """
    Lädt Futter-Daten aus CSV-Datei in generisches Format
    
    Args:
        dateiname: Name der CSV-Datei
        
    Returns:
        Dictionary mit Futter-Daten
    """
    try:
        pfad = DATA_DIR / dateiname
        
        if not pfad.exists():
            logger.error(f"Datei nicht gefunden: {pfad}")
            return {}
        
        # CSV lesen
        data = {}
        with open(pfad, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader):
                # Eindeutigen Schlüssel generieren
                if 'Name' in row and row['Name']:
                    key = row['Name']
                elif 'Herkunft' in row:
                    key = f"{row.get('Herkunft', 'Unbekannt')}_{i}"
                else:
                    key = f"Eintrag_{i}"
                
                # Leere Strings durch 0 ersetzen für numerische Felder
                clean_row = {}
                for field, value in row.items():
                    if value == '':
                        # Versuche zu bestimmen ob numerisch
                        if any(num_field in field.lower() for num_field in ['gewicht', 'protein', 'faser', 'zucker', 'me', 'pcv', 'alter', 'box']):
                            clean_row[field] = 0
                        else:
                            clean_row[field] = ''
                    else:
                        clean_row[field] = value
                
                data[key] = clean_row
        
        logger.info(f"Futter-Daten geladen: {dateiname} ({len(data)} Einträge)")
        return data
        
    except Exception as e:
        logger.error(f"Fehler beim Laden der Futter-Daten {dateiname}: {e}")
        return {}

