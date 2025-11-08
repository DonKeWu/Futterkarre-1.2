"""
UI-Utilities für bessere UI-Responsivität und zentrale UI-Operationen.

Enthält zentrale Methoden für:
- UI-Events verarbeiten
- UI-Timing und Responsivität
- Gemeinsame UI-Patterns
"""
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class UIUtils:
    """Zentrale UI-Utilities für bessere Code-Organisation"""
    
    @staticmethod
    def process_events(reason: str = "UI-Update"):
        """
        Zentrale Methode für UI-Event-Verarbeitung.
        
        Args:
            reason: Grund für processEvents (für Logging)
        """
        try:
            if QApplication.instance():
                QApplication.processEvents()
                logger.debug(f"UI-Events verarbeitet: {reason}")
            else:
                logger.warning("Keine QApplication-Instanz verfügbar")
        except Exception as e:
            logger.error(f"Fehler bei processEvents ({reason}): {e}")
    
    @staticmethod 
    def delayed_execution(func: Callable, delay_ms: int = 50, reason: str = "Delayed execution"):
        """
        Führt eine Funktion nach kurzer Verzögerung aus.
        Nützlich für UI-Timing-Probleme.
        
        Args:
            func: Auszuführende Funktion
            delay_ms: Verzögerung in Millisekunden
            reason: Grund für die Verzögerung (für Logging)
        """
        def execute():
            try:
                logger.debug(f"Verzögerte Ausführung: {reason}")
                func()
            except Exception as e:
                logger.error(f"Fehler bei verzögerter Ausführung ({reason}): {e}")
        
        QTimer.singleShot(delay_ms, execute)
    
    @staticmethod
    def update_ui_and_process(widget, update_func: Callable, reason: str = "UI-Update"):
        """
        Führt UI-Update aus und verarbeitet Events für bessere Responsivität.
        
        Args:
            widget: Das zu aktualisierende Widget
            update_func: Funktion die das Update durchführt
            reason: Grund für das Update (für Logging)
        """
        try:
            logger.debug(f"UI-Update startet: {reason}")
            update_func()
            UIUtils.process_events(f"{reason} - nach Update")
            logger.debug(f"UI-Update abgeschlossen: {reason}")
        except Exception as e:
            logger.error(f"Fehler bei UI-Update ({reason}): {e}")
    
    @staticmethod
    def safe_widget_update(widget, attribute: str, value, reason: str = "Widget-Update"):
        """
        Sicheres Widget-Attribut-Update mit Error-Handling.
        
        Args:
            widget: Das zu aktualisierende Widget
            attribute: Name des zu setzenden Attributs
            value: Neuer Wert
            reason: Grund für das Update (für Logging)
        """
        try:
            if hasattr(widget, attribute):
                setattr(widget, attribute, value)
                logger.debug(f"Widget-Update erfolgreich: {attribute} = {value} ({reason})")
            else:
                logger.warning(f"Widget hat kein Attribut '{attribute}' ({reason})")
        except Exception as e:
            logger.error(f"Fehler bei Widget-Update {attribute} ({reason}): {e}")


class UITiming:
    """Spezielle Timing-Utilities für UI-Responsivität"""
    
    @staticmethod
    def ensure_ui_responsiveness(func: Callable, *args, process_events: bool = True, **kwargs):
        """
        Führt Funktion aus und stellt UI-Responsivität sicher.
        
        Args:
            func: Auszuführende Funktion
            process_events: Ob processEvents() aufgerufen werden soll
            *args, **kwargs: Parameter für die Funktion
        """
        try:
            result = func(*args, **kwargs)
            if process_events:
                UIUtils.process_events(f"Nach {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Fehler bei {func.__name__}: {e}")
            raise
    
    @staticmethod
    def batch_ui_updates(updates: list, reason: str = "Batch-Update"):
        """
        Führt mehrere UI-Updates in einem Batch aus.
        
        Args:
            updates: Liste von (widget, attribute, value) Tupeln
            reason: Grund für die Updates (für Logging)
        """
        logger.debug(f"Batch-UI-Update startet: {len(updates)} Updates ({reason})")
        
        for widget, attribute, value in updates:
            UIUtils.safe_widget_update(widget, attribute, value, f"{reason} - {attribute}")
        
        UIUtils.process_events(f"{reason} - Batch abgeschlossen")
        logger.debug(f"Batch-UI-Update abgeschlossen: {reason}")