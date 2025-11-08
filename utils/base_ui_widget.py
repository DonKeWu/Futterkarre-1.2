#!/usr/bin/env python3
"""
UI-Basis-Klasse für alle View-Komponenten
Zentralisiert häufige UI-Patterns und reduziert Code-Duplikate

Gemeinsame Patterns:
- UI-Loading (uic.loadUi + Fallback)
- Button-Verbindungen
- Vollbild-Setup für PiTouch2 
- Navigation-Integration
- Manager-Initialisierung
"""

import os
import logging
from pathlib import Path
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QWidget

# Manager Imports
from utils.settings_manager import get_settings_manager
from utils.database_manager import get_database_manager  
from utils.timer_manager import get_timer_manager

logger = logging.getLogger(__name__)


class BaseUIWidget(QtWidgets.QWidget):
    """
    Basis-Klasse für alle View-Widgets mit gemeinsamen UI-Patterns
    
    Features:
    ✅ Automatisches UI-Loading mit Fallback
    ✅ PiTouch2-optimierte Vollbild-Einstellungen
    ✅ Manager-Integration (Settings, Database, Timer)
    ✅ Navigation-Unterstützung
    ✅ Einheitliche Button-Verbindungs-Patterns
    """
    
    def __init__(self, parent=None, ui_filename=None):
        super().__init__(parent)
        
        # Navigation (wird von MainWindow gesetzt)
        self.navigation = None
        
        # Manager-Integration
        self.settings_manager = get_settings_manager()
        self.db_manager = get_database_manager()
        self.timer_manager = get_timer_manager()
        
        # UI laden
        if ui_filename:
            self.load_ui_or_fallback(ui_filename)
        
        # PiTouch2-optimierte Einstellungen
        self.setup_pitouch_display()
        
    def load_ui_or_fallback(self, ui_filename: str):
        """
        Lädt UI-Datei mit robustem Error-Handling
        
        Args:
            ui_filename: Name der .ui-Datei (z.B. "start.ui")
        """
        from utils.error_handler import error_handler
        
        def load_ui():
            # UI-Dateien sind im views/ Ordner, nicht in utils/
            views_dir = Path(__file__).parent.parent / "views" 
            ui_path = views_dir / ui_filename
            if not ui_path.exists():
                raise FileNotFoundError(f"UI-Datei nicht gefunden: {ui_path}")
            
            uic.loadUi(str(ui_path), self)
            return True
        
        return error_handler.safe_execute(
            load_ui,
            fallback_value=False,
            operation_name=f"UI-Loading {ui_filename}",
            show_user_error=False
        )
    
    def setup_pitouch_display(self):
        """
        PiTouch2-optimierte Display-Einstellungen
        
        - Vollbild: 1280x720 (komplette Display-Nutzung)
        - Position: oben links (0,0)
        """
        self.setFixedSize(1280, 720)
        self.move(0, 0)
        logger.debug("PiTouch2-Display-Settings aktiviert")
    
    def connect_buttons_safe(self, button_connections: dict):
        """
        Sichere Button-Verbindung mit hasattr-Check
        
        Args:
            button_connections: Dict mit {"button_name": callback_method}
        
        Example:
            self.connect_buttons_safe({
                "btn_start": self.start_clicked,
                "btn_back": self.back_clicked,
                "btn_settings": self.settings_clicked
            })
        """
        for button_name, callback in button_connections.items():
            if hasattr(self, button_name):
                button = getattr(self, button_name)
                button.clicked.connect(callback)
                logger.debug(f"Button {button_name} verbunden")
            else:
                logger.debug(f"Button {button_name} nicht gefunden")
    
    def safe_navigation(self, target: str, context=None):
        """
        Robuste Navigation mit Error-Handling und Recovery
        
        Args:
            target: Ziel-Seite (z.B. "start", "auswahl")
            context: Optionaler Kontext
        """
        from utils.error_handler import error_handler, recovery_manager
        
        def navigate():
            if not self.navigation:
                raise AttributeError("Navigation nicht verfügbar")
                
            if not hasattr(self.navigation, 'show_status'):
                raise AttributeError("Navigation hat keine show_status Methode")
                
            self.navigation.show_status(target, context)
            return True
        
        success = error_handler.safe_execute(
            navigate,
            fallback_value=False,
            operation_name=f"Navigation zu {target}",
            show_user_error=False
        )
        
        # Bei Navigationsfehler: Recovery zur sicheren Startseite
        if not success and target != "start":
            logger.warning(f"Navigation zu {target} fehlgeschlagen - Recovery zur Startseite")
            recovery_manager.recover_navigation(self.navigation, "start")
    
    def back_clicked(self):
        """Standard Zurück-Button Implementierung"""
        logger.info("Zurück-Button geklickt")
        if self.navigation and hasattr(self.navigation, 'go_back'):
            self.navigation.go_back()
        else:
            # Fallback: zur Start-Seite
            self.safe_navigation("start")
    
    def settings_clicked(self):
        """Standard Einstellungen-Button Implementierung"""
        logger.info("Einstellungen-Button geklickt")
        self.safe_navigation("einstellungen")


class BaseViewWidget(BaseUIWidget):
    """
    Erweiterte Basis-Klasse für Haupt-View-Widgets
    
    Zusätzliche Features:
    ✅ ShowEvent/HideEvent Logging
    ✅ Timer-Manager Integration
    ✅ Standard Button-Patterns
    """
    
    def __init__(self, parent=None, ui_filename=None, page_name=None):
        super().__init__(parent, ui_filename)
        self.page_name = page_name or self.__class__.__name__.lower()
        
        # Standard-Button-Verbindungen nach UI-Load
        self.connect_standard_buttons()
    
    def connect_standard_buttons(self):
        """Verbindet häufige Standard-Buttons"""
        standard_buttons = {
            "btn_back": self.back_clicked,
            "btn_settings": self.settings_clicked,
            "btn_zurueck": self.back_clicked,  # Alternative Schreibweise
        }
        self.connect_buttons_safe(standard_buttons)
    
    def showEvent(self, event):
        """Wird aufgerufen wenn Seite angezeigt wird"""
        super().showEvent(event)
        
        # Timer für diese Seite registrieren
        if hasattr(self.timer_manager, 'set_active_page'):
            self.timer_manager.set_active_page(self.page_name)
        
        logger.debug(f"{self.__class__.__name__} angezeigt")
    
    def hideEvent(self, event):
        """Wird aufgerufen wenn Seite versteckt wird"""
        super().hideEvent(event)
        logger.debug(f"{self.__class__.__name__} versteckt")