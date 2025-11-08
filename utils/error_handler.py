#!/usr/bin/env python3
"""
Robuster Error-Handler für bessere Fehlerbehandlung
Zentralisiert Error-Patterns und bietet bessere User-Experience

Features:
- Try-Catch-Wrapper für häufige Operationen
- User-freundliche Error-Messages
- Fallback-Strategien
- Logging-Integration  
- Recovery-Mechanismen
"""

import logging
import traceback
from typing import Any, Callable, Dict, Optional, Union
from functools import wraps
from pathlib import Path

logger = logging.getLogger(__name__)


class ErrorHandler:
    """
    Zentraler Error-Handler für robuste Fehlerbehandlung
    
    Funktionen:
    ✅ Try-Catch-Wrapper für Operations
    ✅ Fallback-Strategien
    ✅ User-freundliche Fehlermeldungen
    ✅ Recovery-Mechanismen
    """
    
    @staticmethod
    def safe_execute(
        operation: Callable,
        fallback_value: Any = None,
        operation_name: str = "Operation",
        show_user_error: bool = True,
        log_level: int = logging.ERROR
    ) -> Any:
        """
        Führt Operation sicher aus mit Fallback
        
        Args:
            operation: Callable - Funktion die ausgeführt werden soll
            fallback_value: Rückgabe-Wert bei Fehler
            operation_name: Beschreibung für Logging
            show_user_error: Ob User-Benachrichtigung gezeigt werden soll
            log_level: Logging-Level für Fehler
            
        Returns:
            Ergebnis der Operation oder fallback_value
        """
        try:
            result = operation()
            logger.debug(f"✅ {operation_name} erfolgreich")
            return result
            
        except Exception as e:
            logger.log(log_level, f"❌ {operation_name} fehlgeschlagen: {e}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            
            if show_user_error:
                ErrorHandler._log_user_friendly_error(operation_name, str(e))
            
            return fallback_value
    
    @staticmethod
    def safe_file_operation(
        filepath: Union[str, Path],
        operation: Callable[[Path], Any],
        fallback_value: Any = None,
        create_fallback: bool = False
    ) -> Any:
        """
        Sichere Datei-Operation mit Fallbacks
        
        Args:
            filepath: Pfad zur Datei
            operation: Funktion die auf Datei ausgeführt wird
            fallback_value: Rückgabe bei Fehler
            create_fallback: Ob Fallback-Datei erstellt werden soll
            
        Returns:
            Ergebnis oder fallback_value
        """
        filepath = Path(filepath)
        
        # Existenz prüfen
        if not filepath.exists():
            logger.warning(f"📁 Datei nicht gefunden: {filepath}")
            
            if create_fallback:
                ErrorHandler._create_fallback_file(filepath)
            else:
                return fallback_value
        
        # Operation ausführen
        return ErrorHandler.safe_execute(
            lambda: operation(filepath),
            fallback_value,
            f"Datei-Operation auf {filepath.name}"
        )
    
    @staticmethod
    def safe_ui_operation(
        widget_name: str,
        operation: Callable,
        fallback_action: Optional[Callable] = None,
        suppress_errors: bool = False
    ) -> bool:
        """
        Sichere UI-Operation mit Fallback-Aktionen
        
        Args:
            widget_name: Name des UI-Elements für Logging
            operation: UI-Operation die ausgeführt werden soll  
            fallback_action: Alternative Aktion bei Fehler
            suppress_errors: Ob Fehler unterdrückt werden sollen
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            operation()
            logger.debug(f"🖥️ UI-Operation '{widget_name}' erfolgreich")
            return True
            
        except Exception as e:
            if not suppress_errors:
                logger.error(f"🖥️ UI-Operation '{widget_name}' fehlgeschlagen: {e}")
            
            # Fallback-Aktion ausführen
            if fallback_action:
                try:
                    fallback_action()
                    logger.info(f"🔄 Fallback für '{widget_name}' erfolgreich")
                except Exception as fe:
                    logger.error(f"🔄 Fallback für '{widget_name}' auch fehlgeschlagen: {fe}")
            
            return False
    
    @staticmethod
    def with_error_handling(
        operation_name: str = "Operation",
        fallback_value: Any = None,
        suppress_errors: bool = False
    ):
        """
        Decorator für automatische Fehlerbehandlung
        
        Args:
            operation_name: Beschreibung der Operation
            fallback_value: Rückgabe-Wert bei Fehler
            suppress_errors: Ob Fehler unterdrückt werden
        
        Usage:
            @ErrorHandler.with_error_handling("CSV laden", fallback_value=[])
            def load_csv_data():
                # Deine Funktion hier
                pass
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return ErrorHandler.safe_execute(
                    lambda: func(*args, **kwargs),
                    fallback_value,
                    operation_name,
                    show_user_error=not suppress_errors
                )
            return wrapper
        return decorator
    
    @staticmethod
    def _log_user_friendly_error(operation: str, error_msg: str):
        """Loggt user-freundliche Fehlermeldung"""
        
        # Häufige Fehler-Patterns erkennen und übersetzen
        friendly_errors = {
            "FileNotFoundError": "📁 Datei nicht gefunden",
            "PermissionError": "🔒 Keine Berechtigung für Datei-Zugriff", 
            "ConnectionError": "🌐 Verbindungsfehler",
            "TimeoutError": "⏱️ Zeitüberschreitung",
            "ValueError": "📊 Ungültige Daten",
            "KeyError": "🔑 Fehlender Parameter",
            "AttributeError": "⚙️ UI-Element nicht verfügbar"
        }
        
        # Error-Typ erkennen
        error_type = error_msg.split(":")[0] if ":" in error_msg else "UnknownError"
        friendly_msg = friendly_errors.get(error_type, "❌ Unbekannter Fehler")
        
        logger.warning(f"User-Info: {operation} → {friendly_msg}")
    
    @staticmethod
    def _create_fallback_file(filepath: Path):
        """Erstellt eine Fallback-Datei mit Minimal-Daten"""
        try:
            # Verzeichnis erstellen falls nötig
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Minimal-CSV basierend auf Dateiname
            if 'pferde' in filepath.name.lower():
                content = "Name,Gewicht,Alter,Box,Aktiv\nNotfall-Pferd,500,10,1,True\n"
            elif 'heu' in filepath.name.lower():
                content = "Trockensubstanz,Rohprotein,Rohfaser,Gesamtzucker,Fruktan,ME-Pferd,Herkunft,Jahrgang\n85.0,8.0,30.0,8.0,2.0,8.0,Standard,2025\n"
            elif 'heulage' in filepath.name.lower():
                content = "Trockensubstanz,Rohprotein,Rohfaser,Gesamtzucker,Fruktan,ME-Pferd,Herkunft,Jahrgang\n45.0,12.0,25.0,5.0,1.5,10.0,Standard,2025\n"
            else:
                content = "# Fallback-Datei automatisch erstellt\n"
            
            filepath.write_text(content, encoding='utf-8')
            logger.info(f"📝 Fallback-Datei erstellt: {filepath}")
            
        except Exception as e:
            logger.error(f"Fallback-Datei-Erstellung fehlgeschlagen: {e}")


class RecoveryManager:
    """
    Manager für Recovery-Strategien bei kritischen Fehlern
    """
    
    @staticmethod
    def recover_ui_state(widget, default_state: Dict[str, Any]):
        """
        Stellt UI-Widget in Default-Zustand wieder her
        
        Args:
            widget: PyQt-Widget
            default_state: Dictionary mit Default-Werten
        """
        for property_name, default_value in default_state.items():
            ErrorHandler.safe_ui_operation(
                f"Reset {property_name}",
                lambda: setattr(widget, property_name, default_value),
                suppress_errors=True
            )
    
    @staticmethod
    def recover_navigation(navigation_obj, safe_target: str = "start"):
        """
        Sichere Navigation-Recovery
        
        Args:
            navigation_obj: Navigation-Objekt  
            safe_target: Sichere Ziel-Seite
        """
        ErrorHandler.safe_execute(
            lambda: navigation_obj.show_status(safe_target),
            operation_name="Navigation Recovery",
            fallback_value=None
        )
    
    @staticmethod
    def emergency_fallback_data():
        """Liefert Notfall-Daten für kritische System-Ausfälle"""
        return {
            'pferde': [{'name': 'Notfall-Pferd', 'gewicht': 500, 'alter': 10}],
            'heu': [{'Trockensubstanz': 85.0, 'ME-Pferd': 8.0}],
            'heulage': [{'Trockensubstanz': 45.0, 'ME-Pferd': 10.0}]
        }


# Globale Error-Handler Instanz für einfachen Import
error_handler = ErrorHandler()
recovery_manager = RecoveryManager()