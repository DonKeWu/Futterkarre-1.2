#!/usr/bin/env python3
"""
Theme Manager - Globale Theme-Verwaltung für das Futterkarre-System
Lädt und wendet QSS-Themes systemweit an

Funktionen:
- Theme-Loading aus config/themes/
- Globale Theme-Anwendung auf QApplication
- Theme-Wechsel zur Laufzeit
- Theme-Validierung und Fallbacks
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

class ThemeManager(QObject):
    """
    Globaler Theme-Manager für einheitliche Theme-Anwendung
    
    Verwaltet:
    - QSS-Theme-Dateien
    - Globale Theme-Anwendung
    - Theme-Wechsel-Events
    - Fallback-Themes
    """
    
    # Signal wenn Theme gewechselt wurde
    theme_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Theme-Verzeichnis
        self.project_root = Path(__file__).parent.parent
        self.themes_dir = self.project_root / "config" / "themes"
        
        # Verfügbare Themes
        self.available_themes = {
            "Standard": "standard.qss",
            "Nacht (Blau)": "nacht_blau.qss", 
            "Natur (Grün)": "natur_gruen.qss",
            "Ultra-Dunkel": "ultra_dunkel.qss"
        }
        
        # Aktuelles Theme
        self.current_theme = "Standard"
        self.current_stylesheet = ""
        
        # Theme-Cache für Performance
        self.theme_cache: Dict[str, str] = {}
        
        logger.info("ThemeManager initialisiert")
    
    def load_theme(self, theme_name: str) -> Optional[str]:
        """
        Lädt QSS-Stylesheet für angegebenes Theme
        
        Args:
            theme_name: Name des Themes (z.B. "Standard", "Nacht (Blau)")
            
        Returns:
            QSS-Stylesheet als String oder None bei Fehler
        """
        try:
            # Cache prüfen
            if theme_name in self.theme_cache:
                logger.debug(f"Theme '{theme_name}' aus Cache geladen")
                return self.theme_cache[theme_name]
            
            # Theme-Datei finden
            if theme_name not in self.available_themes:
                logger.warning(f"Unbekanntes Theme: {theme_name}")
                return None
            
            theme_file = self.themes_dir / self.available_themes[theme_name]
            
            if not theme_file.exists():
                logger.error(f"Theme-Datei nicht gefunden: {theme_file}")
                return None
            
            # QSS-Datei laden
            with open(theme_file, 'r', encoding='utf-8') as f:
                stylesheet = f.read()
            
            # In Cache speichern
            self.theme_cache[theme_name] = stylesheet
            
            logger.info(f"Theme '{theme_name}' geladen ({len(stylesheet)} Zeichen)")
            return stylesheet
            
        except Exception as e:
            logger.error(f"Fehler beim Laden von Theme '{theme_name}': {e}")
            return None
    
    def apply_theme(self, theme_name: str, app: Optional[QApplication] = None) -> bool:
        """
        Wendet Theme global auf QApplication an
        
        Args:
            theme_name: Name des anzuwendenden Themes
            app: QApplication-Instanz (optional, wird automatisch ermittelt)
            
        Returns:
            True wenn erfolgreich angewendet
        """
        try:
            # QApplication finden
            if app is None:
                app_instance = QApplication.instance()
                if app_instance is None or not isinstance(app_instance, QApplication):
                    logger.warning("Keine QApplication-Instanz gefunden")
                    return False
                app = app_instance
            
            # Theme laden
            stylesheet = self.load_theme(theme_name)
            if stylesheet is None:
                # Fallback auf Standard-Theme
                if theme_name != "Standard":
                    logger.warning(f"Fallback auf Standard-Theme wegen Fehler bei '{theme_name}'")
                    return self.apply_theme("Standard", app)
                else:
                    logger.error("Auch Standard-Theme konnte nicht geladen werden")
                    return False
            
            # Stylesheet anwenden
            app.setStyleSheet(stylesheet)
            
            # Status aktualisieren
            old_theme = self.current_theme
            self.current_theme = theme_name
            self.current_stylesheet = stylesheet
            
            logger.info(f"Theme gewechselt von '{old_theme}' zu '{theme_name}'")
            
            # Signal emittieren
            self.theme_changed.emit(theme_name)
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Anwenden von Theme '{theme_name}': {e}")
            return False
    
    def get_available_themes(self) -> list:
        """
        Gibt Liste der verfügbaren Theme-Namen zurück
        
        Returns:
            Liste der Theme-Namen
        """
        return list(self.available_themes.keys())
    
    def get_current_theme(self) -> str:
        """
        Gibt Name des aktuell angewendeten Themes zurück
        
        Returns:
            Name des aktuellen Themes
        """
        return self.current_theme
    
    def validate_themes(self) -> Dict[str, bool]:
        """
        Validiert alle verfügbaren Themes
        
        Returns:
            Dictionary mit Theme-Name -> Verfügbar (bool)
        """
        validation_results = {}
        
        for theme_name, theme_file in self.available_themes.items():
            theme_path = self.themes_dir / theme_file
            
            try:
                # Datei existiert?
                if not theme_path.exists():
                    validation_results[theme_name] = False
                    logger.warning(f"Theme-Datei fehlt: {theme_path}")
                    continue
                
                # Datei lesbar?
                with open(theme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Mindest-Inhalt vorhanden?
                if len(content.strip()) < 10:
                    validation_results[theme_name] = False
                    logger.warning(f"Theme-Datei zu kurz: {theme_path}")
                    continue
                
                # Basis-QSS-Syntax vorhanden?
                if 'QWidget' not in content and 'QPushButton' not in content:
                    validation_results[theme_name] = False
                    logger.warning(f"Theme-Datei scheint kein gültiges QSS zu sein: {theme_path}")
                    continue
                
                validation_results[theme_name] = True
                logger.debug(f"Theme '{theme_name}' ist gültig")
                
            except Exception as e:
                validation_results[theme_name] = False
                logger.error(f"Fehler bei Theme-Validierung '{theme_name}': {e}")
        
        valid_count = sum(validation_results.values())
        total_count = len(validation_results)
        logger.info(f"Theme-Validierung: {valid_count}/{total_count} Themes gültig")
        
        return validation_results
    
    def clear_cache(self):
        """Leert Theme-Cache (z.B. nach Theme-Datei-Änderungen)"""
        old_count = len(self.theme_cache)
        self.theme_cache.clear()
        logger.info(f"Theme-Cache geleert ({old_count} Einträge entfernt)")
    
    def reload_current_theme(self, app: Optional[QApplication] = None) -> bool:
        """
        Lädt aktuelles Theme neu (z.B. nach Datei-Änderungen)
        
        Args:
            app: QApplication-Instanz (optional)
            
        Returns:
            True wenn erfolgreich neu geladen
        """
        # Cache für aktuelles Theme löschen
        if self.current_theme in self.theme_cache:
            del self.theme_cache[self.current_theme]
        
        # Theme neu anwenden
        return self.apply_theme(self.current_theme, app)
    
    def create_theme_preview(self, theme_name: str) -> str:
        """
        Erstellt CSS für Theme-Vorschau (vereinfacht)
        
        Args:
            theme_name: Theme für Vorschau
            
        Returns:
            Vereinfachtes CSS für Vorschau-Widgets
        """
        stylesheet = self.load_theme(theme_name)
        if not stylesheet:
            return ""
        
        # Nur relevante Teile für Vorschau extrahieren
        preview_css = ""
        
        lines = stylesheet.split('\n')
        in_widget_section = False
        in_button_section = False
        in_frame_section = False
        
        for line in lines:
            line = line.strip()
            
            # QWidget Basis-Farben
            if line.startswith('QWidget {'):
                in_widget_section = True
            elif in_widget_section and line.startswith('}'):
                in_widget_section = False
            elif in_widget_section and ('background-color' in line or 'color:' in line):
                preview_css += line + '\n'
            
            # QPushButton Styles
            elif line.startswith('QPushButton {'):
                in_button_section = True
                preview_css += 'QPushButton {\n'
            elif in_button_section and line.startswith('}'):
                in_button_section = False
                preview_css += '}\n'
            elif in_button_section:
                preview_css += line + '\n'
            
            # QFrame Styles
            elif line.startswith('QFrame {'):
                in_frame_section = True
                preview_css += 'QFrame {\n'
            elif in_frame_section and line.startswith('}'):
                in_frame_section = False
                preview_css += '}\n'
            elif in_frame_section:
                preview_css += line + '\n'
        
        return preview_css

# Globale Theme-Manager Instanz
_theme_manager_instance: Optional[ThemeManager] = None

def get_theme_manager() -> ThemeManager:
    """
    Gibt globale ThemeManager-Instanz zurück (Singleton)
    
    Returns:
        ThemeManager-Instanz
    """
    global _theme_manager_instance
    if _theme_manager_instance is None:
        _theme_manager_instance = ThemeManager()
    return _theme_manager_instance

def apply_theme_globally(theme_name: str) -> bool:
    """
    Convenience-Funktion für globale Theme-Anwendung
    
    Args:
        theme_name: Name des anzuwendenden Themes
        
    Returns:
        True wenn erfolgreich
    """
    return get_theme_manager().apply_theme(theme_name)