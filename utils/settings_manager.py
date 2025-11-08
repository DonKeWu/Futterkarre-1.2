#!/usr/bin/env python3
"""
Settings Manager - Zentrale Benutzer-Einstellungen Verwaltung
Persistente Konfiguration für das Futterkarre-System

Funktionen:
- Systemeinstellungen (Sprache, Display, etc.)
- Kalibrierungs-Parameter (HX711, Nullpunkt)
- Futter-Parameter (Standard-Mengen, Limits)
- Hardware-Konfiguration (Simulation/Hardware)
- Automatische Speicherung/Laden von settings.json
"""

import json
import logging
import os
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict, field
from threading import Lock

logger = logging.getLogger(__name__)

@dataclass
class SystemSettings:
    """System-Einstellungen"""
    language: str = "de"
    display_timeout: int = 300  # Sekunden
    fullscreen: bool = True
    brightness: int = 80  # Prozent
    volume: int = 50
    auto_sleep: bool = True

@dataclass
class CalibrationSettings:
    """Kalibrierungs-Einstellungen für Waage"""
    tare_values: list = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])  # VL, VR, HL, HR
    scale_factors: list = field(default_factory=lambda: [1.0, 1.0, 1.0, 1.0])
    calibration_weights: list = field(default_factory=lambda: [20.0, 20.0, 20.0, 20.0])
    last_calibration: str = ""
    auto_tare_on_startup: bool = True

@dataclass
class FeedingSettings:
    """Fütterungs-Einstellungen"""
    default_feed_amount: float = 4.5  # kg
    max_feed_per_horse: float = 15.0  # kg
    min_feed_per_horse: float = 1.0   # kg
    max_total_load: float = 100.0     # kg
    warning_threshold: float = 10.0   # kg (Karre fast leer)
    simulation_mode: bool = True
    auto_reload_threshold: float = 5.0  # kg

@dataclass
class HardwareSettings:
    """Hardware-Einstellungen"""
    use_simulation: bool = True
    hx711_update_rate: int = 500  # ms
    sensor_timeout: int = 5000    # ms
    auto_hardware_detection: bool = True
    backup_to_usb: bool = False
    debug_mode: bool = False

@dataclass
class UISettings:
    """UI-Einstellungen"""
    theme: str = "default"
    font_size: int = 14
    button_size: str = "large"  # small, medium, large
    show_debug_info: bool = False
    animation_speed: str = "normal"  # slow, normal, fast
    confirmation_dialogs: bool = True

class SettingsManager:
    """
    Singleton für zentrale Einstellungs-Verwaltung
    
    Verwaltet alle Benutzer-Einstellungen persistent:
    - System-Konfiguration
    - Kalibrierungs-Parameter
    - Fütterungs-Einstellungen
    - Hardware-Konfiguration
    - UI-Präferenzen
    """
    
    _instance: Optional['SettingsManager'] = None
    _lock = Lock()
    
    def __new__(cls) -> 'SettingsManager':
        """Singleton Pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Verhindere Mehrfach-Initialisierung
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        
        # Settings-Datei
        self.settings_file = Path("config") / "settings.json"
        self.backup_file = Path("config") / "settings_backup.json"
        
        # Einstellungs-Kategorien
        self.system = SystemSettings()
        self.calibration = CalibrationSettings()
        self.feeding = FeedingSettings()
        self.hardware = HardwareSettings()
        self.ui = UISettings()
        
        # Callbacks für Änderungen
        self._change_callbacks: Dict[str, list] = {}
        
        # Config-Ordner erstellen
        os.makedirs("config", exist_ok=True)
        
        # Einstellungen laden
        self.load_settings()
        
        logger.info("SettingsManager initialisiert")
    
    def load_settings(self) -> bool:
        """
        Lädt Einstellungen aus JSON-Datei
        
        Returns:
            True wenn erfolgreich geladen
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Einstellungen aus JSON laden
                if 'system' in data:
                    self.system = SystemSettings(**data['system'])
                if 'calibration' in data:
                    self.calibration = CalibrationSettings(**data['calibration'])
                if 'feeding' in data:
                    # Robuste Filterung für FeedingSettings - nur bekannte Parameter
                    feeding_data = {}
                    valid_feeding_keys = {'default_feed_amount', 'max_feed_per_horse', 'min_feed_per_horse', 
                                        'max_total_load', 'warning_threshold', 'simulation_mode', 'auto_reload_threshold'}
                    for key, value in data['feeding'].items():
                        if key in valid_feeding_keys:
                            feeding_data[key] = value
                        else:
                            logger.warning(f"Überspringe unbekannten FeedingSettings Parameter: {key}")
                    self.feeding = FeedingSettings(**feeding_data)
                if 'hardware' in data:
                    # Robuste Filterung für HardwareSettings - nur bekannte Parameter
                    hardware_data = {}
                    valid_hardware_keys = {'use_simulation', 'hx711_update_rate', 'sensor_timeout', 
                                         'auto_hardware_detection', 'backup_to_usb', 'debug_mode'}
                    for key, value in data['hardware'].items():
                        if key in valid_hardware_keys:
                            hardware_data[key] = value
                        else:
                            logger.warning(f"Überspringe unbekannten HardwareSettings Parameter: {key}")
                    self.hardware = HardwareSettings(**hardware_data)
                if 'ui' in data:
                    self.ui = UISettings(**data['ui'])
                
                logger.info(f"Einstellungen geladen aus {self.settings_file}")
                return True
            else:
                logger.info("Keine Einstellungsdatei gefunden - verwende Standardwerte")
                self.save_settings()  # Standardwerte speichern
                return False
                
        except Exception as e:
            logger.error(f"Fehler beim Laden der Einstellungen: {e}")
            self._try_load_backup()
            return False
    
    def _try_load_backup(self):
        """Versucht Backup-Einstellungen zu laden"""
        try:
            if self.backup_file.exists():
                with open(self.backup_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Backup laden (vereinfacht)
                logger.warning("Lade Backup-Einstellungen")
                # Implementierung analog zu load_settings()
        except Exception as e:
            logger.error(f"Backup-Laden fehlgeschlagen: {e}")
    
    def save_settings(self) -> bool:
        """
        Speichert aktuelle Einstellungen in JSON-Datei
        
        Returns:
            True wenn erfolgreich gespeichert
        """
        try:
            # Backup der aktuellen Datei erstellen
            if self.settings_file.exists():
                import shutil
                shutil.copy2(self.settings_file, self.backup_file)
            
            # Einstellungen zusammenfassen
            data = {
                'system': asdict(self.system),
                'calibration': asdict(self.calibration),
                'feeding': asdict(self.feeding),
                'hardware': asdict(self.hardware),
                'ui': asdict(self.ui),
                'metadata': {
                    'version': '1.2',
                    'last_saved': str(Path().cwd()),
                    'timestamp': str(Path().stat().st_mtime) if Path().exists() else ""
                }
            }
            
            # Speichern
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Einstellungen gespeichert in {self.settings_file}")
            
            # Callbacks ausführen
            self._notify_change('all')
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Einstellungen: {e}")
            return False
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """
        Holt eine spezifische Einstellung
        
        Args:
            category: Kategorie (system, calibration, feeding, hardware, ui)
            key: Einstellungs-Schlüssel
            default: Standardwert falls nicht gefunden
            
        Returns:
            Einstellungswert oder default
        """
        try:
            category_obj = getattr(self, category)
            return getattr(category_obj, key, default)
        except AttributeError:
            logger.warning(f"Einstellung nicht gefunden: {category}.{key}")
            return default
    
    def set_setting(self, category: str, key: str, value: Any, save: bool = True) -> bool:
        """
        Setzt eine spezifische Einstellung
        
        Args:
            category: Kategorie
            key: Einstellungs-Schlüssel
            value: Neuer Wert
            save: Sofort speichern
            
        Returns:
            True wenn erfolgreich gesetzt
        """
        try:
            category_obj = getattr(self, category)
            old_value = getattr(category_obj, key, None)
            
            setattr(category_obj, key, value)
            
            logger.debug(f"Einstellung geändert: {category}.{key} = {value} (war: {old_value})")
            
            if save:
                self.save_settings()
            
            # Callbacks für diese Kategorie ausführen
            self._notify_change(category)
            
            return True
            
        except AttributeError:
            logger.error(f"Ungültige Einstellung: {category}.{key}")
            return False
    
    def register_change_callback(self, category: str, callback):
        """
        Registriert Callback für Einstellungsänderungen
        
        Args:
            category: Kategorie oder 'all' für alle Änderungen
            callback: Callback-Funktion
        """
        if category not in self._change_callbacks:
            self._change_callbacks[category] = []
        
        self._change_callbacks[category].append(callback)
        logger.debug(f"Callback für '{category}' registriert")
    
    def _notify_change(self, category: str):
        """Benachrichtigt Callbacks über Änderungen"""
        # Spezifische Kategorie
        if category in self._change_callbacks:
            for callback in self._change_callbacks[category]:
                try:
                    callback(category)
                except Exception as e:
                    logger.error(f"Callback-Fehler für {category}: {e}")
        
        # 'all' Callbacks
        if 'all' in self._change_callbacks:
            for callback in self._change_callbacks['all']:
                try:
                    callback(category)
                except Exception as e:
                    logger.error(f"All-Callback-Fehler: {e}")
    
    def reset_category(self, category: str) -> bool:
        """
        Setzt eine Kategorie auf Standardwerte zurück
        
        Args:
            category: Kategorie zum Zurücksetzen
            
        Returns:
            True wenn erfolgreich
        """
        try:
            if category == 'system':
                self.system = SystemSettings()
            elif category == 'calibration':
                self.calibration = CalibrationSettings()
            elif category == 'feeding':
                self.feeding = FeedingSettings()
            elif category == 'hardware':
                self.hardware = HardwareSettings()
            elif category == 'ui':
                self.ui = UISettings()
            else:
                logger.error(f"Unbekannte Kategorie: {category}")
                return False
            
            self.save_settings()
            logger.info(f"Kategorie '{category}' zurückgesetzt")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Zurücksetzen von {category}: {e}")
            return False
    
    def export_settings(self, export_path: Union[str, Path]) -> bool:
        """Exportiert Einstellungen in externe Datei"""
        try:
            export_path = Path(export_path)
            
            data = {
                'system': asdict(self.system),
                'calibration': asdict(self.calibration),
                'feeding': asdict(self.feeding),
                'hardware': asdict(self.hardware),
                'ui': asdict(self.ui),
                'export_info': {
                    'exported_at': str(Path().cwd()),
                    'version': '1.2'
                }
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Einstellungen exportiert nach {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Export fehlgeschlagen: {e}")
            return False
    
    def import_settings(self, import_path: Union[str, Path]) -> bool:
        """Importiert Einstellungen aus externer Datei"""
        try:
            import_path = Path(import_path)
            
            if not import_path.exists():
                logger.error(f"Import-Datei nicht gefunden: {import_path}")
                return False
            
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validierung und Import
            if 'system' in data:
                self.system = SystemSettings(**data['system'])
            if 'calibration' in data:
                self.calibration = CalibrationSettings(**data['calibration'])
            if 'feeding' in data:
                # Robuste Filterung für FeedingSettings - nur bekannte Parameter
                feeding_data = {}
                valid_feeding_keys = {'default_feed_amount', 'max_feed_per_horse', 'min_feed_per_horse', 
                                    'max_total_load', 'warning_threshold', 'simulation_mode', 'auto_reload_threshold'}
                for key, value in data['feeding'].items():
                    if key in valid_feeding_keys:
                        feeding_data[key] = value
                self.feeding = FeedingSettings(**feeding_data)
            if 'hardware' in data:
                # Robuste Filterung für HardwareSettings - nur bekannte Parameter
                hardware_data = {}
                valid_hardware_keys = {'use_simulation', 'hx711_update_rate', 'sensor_timeout', 
                                     'auto_hardware_detection', 'backup_to_usb', 'debug_mode'}
                for key, value in data['hardware'].items():
                    if key in valid_hardware_keys:
                        hardware_data[key] = value
                self.hardware = HardwareSettings(**hardware_data)
            if 'ui' in data:
                self.ui = UISettings(**data['ui'])
            
            self.save_settings()
            logger.info(f"Einstellungen importiert von {import_path}")
            return True
            
        except Exception as e:
            logger.error(f"Import fehlgeschlagen: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Gibt alle Einstellungen zurück"""
        return {
            'system': asdict(self.system),
            'calibration': asdict(self.calibration),
            'feeding': asdict(self.feeding),
            'hardware': asdict(self.hardware),
            'ui': asdict(self.ui)
        }

# Globale Instanz
_settings_manager_instance: Optional[SettingsManager] = None

def get_settings_manager() -> SettingsManager:
    """Gibt die globale SettingsManager-Instanz zurück (Lazy Loading)"""
    global _settings_manager_instance
    if _settings_manager_instance is None:
        _settings_manager_instance = SettingsManager()
    return _settings_manager_instance