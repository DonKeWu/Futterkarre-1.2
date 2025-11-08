# utils/csv_validator.py
"""
Robuster CSV-Validator mit Schema-Definition und Fallback-Mechanismen
"""
import logging
import csv
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ColumnSchema:
    """Schema-Definition für eine CSV-Spalte"""
    name: str                    # Spalten-Name
    required: bool = True        # Pflichtfeld?
    data_type: type = str       # Erwarteter Datentyp
    min_value: Optional[float] = None  # Minimum (für Zahlen)
    max_value: Optional[float] = None  # Maximum (für Zahlen)
    allowed_values: Optional[List[str]] = None  # Erlaubte Werte
    default: Any = None         # Standard-Wert bei Fehlern
    aliases: Optional[List[str]] = None  # Alternative Spaltennamen

@dataclass
class ValidationResult:
    """Ergebnis einer CSV-Validierung"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    fixed_data: Optional[Dict] = None
    row_number: Optional[int] = None

class CSVValidator:
    """Robuster CSV-Validator mit Schema-Validierung"""
    
    def __init__(self):
        self.schemas = self._init_schemas()
    
    def _init_schemas(self) -> Dict[str, List[ColumnSchema]]:
        """Definiert Schemas für alle CSV-Typen"""
        return {
            'pferde': [
                ColumnSchema('Name', required=True, data_type=str),
                ColumnSchema('Gewicht', required=True, data_type=float, min_value=100, max_value=1000, default=500),
                ColumnSchema('Alter', required=True, data_type=int, min_value=1, max_value=40, default=10),
                ColumnSchema('Box', required=False, data_type=int, min_value=1, max_value=100, aliases=['Folge']),
                ColumnSchema('Aktiv', required=False, data_type=str, allowed_values=['true', 'false', 'True', 'False'], default='true')
            ],
            'heu': [
                ColumnSchema('Trockensubstanz', required=True, data_type=float, min_value=70, max_value=100, default=85),
                ColumnSchema('Rohprotein', required=True, data_type=float, min_value=3, max_value=25, default=8),
                ColumnSchema('Rohfaser', required=True, data_type=float, min_value=15, max_value=45, default=30),
                ColumnSchema('Gesamtzucker', required=True, data_type=float, min_value=2, max_value=20, default=8),
                ColumnSchema('Fruktan', required=True, data_type=float, min_value=0, max_value=15, default=2),
                ColumnSchema('ME-Pferd', required=True, data_type=float, min_value=5, max_value=15, default=8, aliases=['ME_Pferd']),
                ColumnSchema('pcv_XP', required=False, data_type=float, min_value=0, max_value=100, default=0),
                ColumnSchema('Herkunft', required=False, data_type=str, default='Eigen'),
                ColumnSchema('Jahrgang', required=False, data_type=int, min_value=2020, max_value=2030, default=2025)
            ],
            'heulage': [
                ColumnSchema('Trockensubstanz', required=True, data_type=float, min_value=25, max_value=70, default=45),
                ColumnSchema('Rohprotein', required=True, data_type=float, min_value=8, max_value=25, default=12),
                ColumnSchema('Rohfaser', required=True, data_type=float, min_value=20, max_value=40, default=25),
                ColumnSchema('Gesamtzucker', required=True, data_type=float, min_value=3, max_value=15, default=6),
                ColumnSchema('Fruktan', required=True, data_type=float, min_value=0, max_value=8, default=1),
                ColumnSchema('ME-Pferd', required=True, data_type=float, min_value=8, max_value=15, default=10, aliases=['ME_Pferd']),
                ColumnSchema('pH-Wert', required=False, data_type=float, min_value=3.5, max_value=6.5, default=4.5, aliases=['pH_Wert', 'ph_wert']),
                ColumnSchema('Siliergrad', required=False, data_type=str, allowed_values=['gut', 'mittel', 'schlecht'], default='gut')
            ],
            'pellets': [
                ColumnSchema('Trockensubstanz', required=True, data_type=float, min_value=85, max_value=95, default=90),
                ColumnSchema('Rohprotein', required=True, data_type=float, min_value=10, max_value=30, default=15),
                ColumnSchema('Rohfaser', required=True, data_type=float, min_value=8, max_value=25, default=12),
                ColumnSchema('Gesamtzucker', required=True, data_type=float, min_value=2, max_value=10, default=5),
                ColumnSchema('Fruktan', required=True, data_type=float, min_value=0, max_value=5, default=1),
                ColumnSchema('ME-Pferd', required=True, data_type=float, min_value=10, max_value=18, default=12)
            ]
        }
    
    def detect_csv_type(self, filepath: Union[str, Path]) -> Optional[str]:
        """Erkennt automatisch den CSV-Typ basierend auf Dateiname"""
        filename = Path(filepath).name.lower()
        
        if 'pferd' in filename:
            return 'pferde'
        elif 'heu' in filename and 'heulage' not in filename:
            return 'heu'
        elif 'heulage' in filename:
            return 'heulage'
        elif 'pellet' in filename:
            return 'pellets'
        else:
            logger.warning(f"Unbekannter CSV-Typ für Datei: {filename}")
            return None
    
    def find_column_mapping(self, headers: List[str], schema: List[ColumnSchema]) -> Dict[str, str]:
        """Erstellt Mapping zwischen CSV-Headern und Schema-Spalten"""
        mapping = {}
        
        for column in schema:
            # Exakte Übereinstimmung
            if column.name in headers:
                mapping[column.name] = column.name
                continue
            
            # Alias-Übereinstimmung
            if column.aliases:
                for alias in column.aliases:
                    if alias in headers:
                        mapping[column.name] = alias
                        break
        
        return mapping
    
    def validate_row(self, row: Dict[str, str], schema: List[ColumnSchema], 
                    column_mapping: Dict[str, str], row_number: int = 0) -> ValidationResult:
        """Validiert eine einzelne CSV-Zeile"""
        errors = []
        warnings = []
        fixed_data = {}
        
        for column in schema:
            csv_column = column_mapping.get(column.name)
            raw_value = row.get(csv_column, '') if csv_column else ''
            
            # Pflichtfeld-Prüfung
            if column.required and (not csv_column or not raw_value.strip()):
                if column.default is not None:
                    fixed_data[column.name] = column.default
                    warnings.append(f"Zeile {row_number}: Fehlender Wert für '{column.name}', Standard verwendet: {column.default}")
                else:
                    errors.append(f"Zeile {row_number}: Pflichtfeld '{column.name}' fehlt")
                continue
            
            # Leere optionale Felder überspringen
            if not raw_value.strip() and not column.required:
                if column.default is not None:
                    fixed_data[column.name] = column.default
                continue
            
            # Datentyp-Konvertierung und Validierung
            try:
                converted_value = self._convert_and_validate(raw_value, column, row_number)
                fixed_data[column.name] = converted_value
            except ValueError as e:
                if column.default is not None:
                    fixed_data[column.name] = column.default
                    warnings.append(f"Zeile {row_number}: {str(e)}, Standard verwendet: {column.default}")
                else:
                    errors.append(f"Zeile {row_number}: {str(e)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            fixed_data=fixed_data,
            row_number=row_number
        )
    
    def _convert_and_validate(self, value: str, column: ColumnSchema, row_number: int) -> Any:
        """Konvertiert und validiert einen Wert"""
        if value is None:
            value = ""
        value = str(value).strip()
        
        # Datentyp-Konvertierung
        if column.data_type == float:
            try:
                converted = float(value.replace(',', '.'))  # Deutsche Dezimaltrennzeichen
            except ValueError:
                raise ValueError(f"'{column.name}' ist keine gültige Zahl: '{value}'")
        elif column.data_type == int:
            try:
                converted = int(float(value.replace(',', '.')))  # Ermöglicht "5.0" -> 5
            except ValueError:
                raise ValueError(f"'{column.name}' ist keine gültige Ganzzahl: '{value}'")
        else:
            converted = value
        
        # Wertebereich-Validierung (nur für Zahlen)
        if column.data_type in [int, float] and isinstance(converted, (int, float)):
            if column.min_value is not None and converted < column.min_value:
                raise ValueError(f"'{column.name}' zu klein: {converted} < {column.min_value}")
            if column.max_value is not None and converted > column.max_value:
                raise ValueError(f"'{column.name}' zu groß: {converted} > {column.max_value}")
        
        # Erlaubte Werte prüfen
        if column.allowed_values and str(converted) not in column.allowed_values:
            raise ValueError(f"'{column.name}' hat ungültigen Wert: '{converted}', erlaubt: {column.allowed_values}")
        
        return converted
    
    def validate_csv_file(self, filepath: Union[str, Path], csv_type: Optional[str] = None) -> Dict[str, Any]:
        """Validiert eine komplette CSV-Datei"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            return {
                'success': False,
                'status': 'error',
                'message': f"Datei nicht gefunden: {filepath}",
                'error': f"Datei nicht gefunden: {filepath}",
                'valid_rows': 0,
                'error_count': 1,
                'warning_count': 0,
                'errors': [f"Datei nicht gefunden: {filepath}"],
                'warnings': []
            }
        
        # CSV-Typ automatisch erkennen
        if csv_type is None:
            csv_type = self.detect_csv_type(filepath)
            if csv_type is None:
                return {
                    'success': False,
                    'status': 'error',
                    'message': f"Unbekannter CSV-Typ für Datei: {filepath.name}",
                    'error': f"Unbekannter CSV-Typ für Datei: {filepath.name}",
                    'valid_rows': 0,
                    'error_count': 1,
                    'warning_count': 0,
                    'errors': [f"Unbekannter CSV-Typ für Datei: {filepath.name}"],
                    'warnings': []
                }
        
        schema = self.schemas.get(csv_type)
        if not schema:
            return {
                'success': False,
                'status': 'error',
                'message': f"Kein Schema für CSV-Typ: {csv_type}",
                'error': f"Kein Schema für CSV-Typ: {csv_type}",
                'valid_rows': 0,
                'error_count': 1,
                'warning_count': 0,
                'errors': [f"Kein Schema für CSV-Typ: {csv_type}"],
                'warnings': []
            }
        
        valid_rows = []
        all_errors = []
        all_warnings = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as csvfile:
                # CSV-Dialect automatisch erkennen
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                if not sample.strip():
                    return {
                        'success': False,
                        'status': 'error',
                        'message': 'CSV-Datei ist leer',
                        'error': 'CSV-Datei ist leer',
                        'valid_rows': 0,
                        'error_count': 1,
                        'warning_count': 0,
                        'errors': ['CSV-Datei ist leer'],
                        'warnings': []
                    }
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                headers = list(reader.fieldnames) if reader.fieldnames else []
                
                if not headers:
                    return {
                        'success': False,
                        'status': 'error',
                        'message': 'Keine gültigen CSV-Header gefunden',
                        'error': 'Keine gültigen CSV-Header gefunden',
                        'valid_rows': 0,
                        'error_count': 1,
                        'warning_count': 0,
                        'errors': ['Keine gültigen CSV-Header gefunden'],
                        'warnings': []
                    }
                
                # Spalten-Mapping erstellen
                column_mapping = self.find_column_mapping(headers, schema)
                
                # Fehlende Pflicht-Spalten prüfen
                required_columns = [col.name for col in schema if col.required]
                missing_required = [col for col in required_columns if col not in column_mapping]
                
                if missing_required:
                    return {
                        'success': False,
                        'status': 'error',
                        'message': f"Fehlende Pflicht-Spalten: {missing_required}",
                        'error': f"Fehlende Pflicht-Spalten: {missing_required}",
                        'valid_rows': 0,
                        'error_count': len(missing_required),
                        'warning_count': 0,
                        'errors': [f"Fehlende Spalten: {missing_required}"],
                        'warnings': []
                    }
                
                # Zeilen validieren
                for row_num, row in enumerate(reader, start=2):  # Start bei 2 (Header ist Zeile 1)
                    result = self.validate_row(row, schema, column_mapping, row_num)
                    
                    if result.is_valid:
                        valid_rows.append(result.fixed_data)
                    
                    all_errors.extend(result.errors)
                    all_warnings.extend(result.warnings)
                
                logger.info(f"CSV-Validierung für {filepath.name}: {len(valid_rows)} gültige Zeilen, "
                           f"{len(all_errors)} Fehler, {len(all_warnings)} Warnungen")
                
                return {
                    'success': len(valid_rows) > 0,
                    'status': 'success' if len(valid_rows) > 0 else 'error',
                    'message': f"{len(valid_rows)} Zeilen erfolgreich validiert" if len(valid_rows) > 0 else "Keine gültigen Zeilen gefunden",
                    'csv_type': csv_type,
                    'valid_rows': len(valid_rows),
                    'error_count': len(all_errors),
                    'warning_count': len(all_warnings),
                    'data': valid_rows,
                    'errors': all_errors,
                    'warnings': all_warnings,
                    'total_rows': len(valid_rows) + len([e for e in all_errors if 'Zeile' in e]),
                    'column_mapping': column_mapping
                }
        
        except Exception as e:
            logger.error(f"Fehler beim Lesen der CSV-Datei {filepath}: {e}")
            return {
                'success': False,
                'status': 'error',
                'message': f"Lesefehler: {str(e)}",
                'error': f"Lesefehler: {str(e)}",
                'valid_rows': 0,
                'error_count': 1,
                'warning_count': 0,
                'errors': [f"Datei-Lesefehler: {str(e)}"],
                'warnings': []
            }
    
    def get_fallback_data(self, csv_type: str) -> List[Dict[str, Any]]:
        """Erstellt Fallback-Daten wenn CSV komplett fehlerhaft ist"""
        if csv_type == 'pferde':
            return [{
                'name': 'Notfall-Pferd',
                'gewicht': 500,
                'alter': 10,
                'box': 1,
                'aktiv': True
            }]
        elif csv_type == 'heu':
            return [{
                'Trockensubstanz': 85.0,
                'Rohprotein': 8.0,
                'Rohfaser': 30.0,
                'Gesamtzucker': 8.0,
                'Fruktan': 2.0,
                'ME-Pferd': 8.0,
                'Herkunft': 'Standard',
                'Jahrgang': 2025
            }]
        elif csv_type == 'heulage':
            return [{
                'Trockensubstanz': 45.0,
                'Rohprotein': 12.0,
                'Rohfaser': 25.0,
                'Gesamtzucker': 6.0,
                'Fruktan': 1.0,
                'ME-Pferd': 10.0,
                'pH-Wert': 4.5,
                'Siliergrad': 'gut'
            }]
        else:
            return []

# Globale Validator-Instanz
csv_validator = CSVValidator()