#!/usr/bin/env python3
"""
TimerManager - Zentraler Singleton für UI-Timer-Verwaltung
Löst Memory-Leaks und redundante Timer-Aufrufe

Funktionen:
- Zentrale Verwaltung aller UI-Timer
- Automatisches Stoppen bei Seitenwechsel
- Memory-Leak-Prävention
- Timer-Überwachung und Debugging
"""

import time
import logging
from typing import Optional, Callable, Dict, Any
from threading import Lock
from dataclasses import dataclass
from PyQt5.QtCore import QTimer, QObject

logger = logging.getLogger(__name__)

@dataclass
class TimerInfo:
    """Information über einen registrierten Timer"""
    timer: QTimer
    interval: int
    callback: Callable
    component: str
    active: bool = False
    created_at: float = 0.0
    last_triggered: float = 0.0
    trigger_count: int = 0

class TimerManager:
    """
    Singleton für zentrale Timer-Verwaltung
    
    Koordiniert alle UI-Timer um Memory-Leaks zu verhindern:
    - FuetternSeite: Gewichts-Updates
    - BeladenSeite: Gewichts-Updates  
    - EinstellungenSeite: (deaktiviert)
    - MainWindow: Navigation-Timer
    """
    
    _instance: Optional['TimerManager'] = None
    _lock = Lock()
    
    def __new__(cls) -> 'TimerManager':
        """Singleton Pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Singleton-Schutz: Nur einmal initialisieren
        if hasattr(self, '_initialized'):
            return
        
        # Eigene Initialisierung ohne QObject
        self._initialized = True
        self._timers: Dict[str, TimerInfo] = {}
        self._active_page: Optional[str] = None
        
        logger.info("TimerManager initialisiert")
    
    def register_timer(self, timer_id: str, component: str, interval: int, 
                      callback: Callable, auto_start: bool = False) -> str:
        """
        Registriert einen neuen Timer
        
        Args:
            timer_id: Eindeutige Timer-ID
            component: UI-Komponente (FuetternSeite, BeladenSeite, etc.)
            interval: Intervall in Millisekunden
            callback: Callback-Funktion
            auto_start: Sofort starten
            
        Returns:
            Timer-ID (für spätere Referenz)
        """
        if timer_id in self._timers:
            logger.warning(f"Timer '{timer_id}' existiert bereits - überschreibe")
            self.unregister_timer(timer_id)
        
        # QTimer erstellen (ohne Parent - wird später managed)
        timer = QTimer()
        timer.timeout.connect(self._on_timer_triggered(timer_id, callback))
        
        # Timer-Info speichern
        timer_info = TimerInfo(
            timer=timer,
            interval=interval,
            callback=callback,
            component=component,
            created_at=time.time()
        )
        
        self._timers[timer_id] = timer_info
        
        if auto_start:
            self.start_timer(timer_id)
        
        logger.debug(f"Timer '{timer_id}' registriert ({component}, {interval}ms)")
        return timer_id
    
    def _on_timer_triggered(self, timer_id: str, callback: Callable) -> Callable:
        """Erstellt Timer-Callback mit Statistik-Tracking"""
        def wrapped_callback():
            if timer_id in self._timers:
                timer_info = self._timers[timer_id]
                timer_info.last_triggered = time.time()
                timer_info.trigger_count += 1
                
                try:
                    callback()
                except Exception as e:
                    logger.error(f"Timer '{timer_id}' Callback-Fehler: {e}")
            
        return wrapped_callback
    
    def start_timer(self, timer_id: str) -> bool:
        """
        Startet einen registrierten Timer
        
        Args:
            timer_id: Timer-ID
            
        Returns:
            True wenn erfolgreich gestartet
        """
        if timer_id not in self._timers:
            logger.error(f"Timer '{timer_id}' nicht registriert")
            return False
        
        timer_info = self._timers[timer_id]
        
        if not timer_info.active:
            timer_info.timer.start(timer_info.interval)
            timer_info.active = True
            logger.debug(f"Timer '{timer_id}' gestartet ({timer_info.interval}ms)")
            return True
        else:
            logger.debug(f"Timer '{timer_id}' bereits aktiv")
            return True
    
    def stop_timer(self, timer_id: str) -> bool:
        """
        Stoppt einen Timer
        
        Args:
            timer_id: Timer-ID
            
        Returns:
            True wenn erfolgreich gestoppt
        """
        if timer_id not in self._timers:
            logger.warning(f"Timer '{timer_id}' nicht registriert")
            return False
        
        timer_info = self._timers[timer_id]
        
        if timer_info.active:
            timer_info.timer.stop()
            timer_info.active = False
            logger.debug(f"Timer '{timer_id}' gestoppt")
            return True
        else:
            logger.debug(f"Timer '{timer_id}' bereits gestoppt")
            return True
    
    def stop_all_timers(self):
        """Stoppt alle aktiven Timer"""
        stopped_count = 0
        
        for timer_id, timer_info in self._timers.items():
            if timer_info.active:
                timer_info.timer.stop()
                timer_info.active = False
                stopped_count += 1
        
        logger.info(f"Alle Timer gestoppt ({stopped_count} aktive)")
    
    def stop_component_timers(self, component: str):
        """
        Stoppt alle Timer einer UI-Komponente
        
        Args:
            component: Komponenten-Name (z.B. "FuetternSeite")
        """
        stopped_timers = []
        
        for timer_id, timer_info in self._timers.items():
            if timer_info.component == component and timer_info.active:
                timer_info.timer.stop()
                timer_info.active = False
                stopped_timers.append(timer_id)
        
        if stopped_timers:
            logger.debug(f"Timer für {component} gestoppt: {stopped_timers}")
    
    def start_component_timers(self, component: str):
        """
        Startet alle Timer einer UI-Komponente
        
        Args:
            component: Komponenten-Name (z.B. "FuetternSeite")
        """
        started_timers = []
        
        for timer_id, timer_info in self._timers.items():
            if timer_info.component == component and not timer_info.active:
                timer_info.timer.start(timer_info.interval)
                timer_info.active = True
                started_timers.append(timer_id)
        
        if started_timers:
            logger.debug(f"Timer für {component} gestartet: {started_timers}")
    
    def set_active_page(self, page_name: str):
        """
        Wechselt die aktive Seite und verwaltet Timer entsprechend
        
        Args:
            page_name: Seitenname (FuetternSeite, BeladenSeite, etc.)
        """
        if self._active_page == page_name:
            return  # Keine Änderung
        
        # Alle Timer der vorherigen Seite stoppen
        if self._active_page:
            self.stop_component_timers(self._active_page)
        
        # Timer der neuen Seite starten
        self._active_page = page_name
        self.start_component_timers(page_name)
        
        logger.info(f"Aktive Seite gewechselt: {page_name}")
    
    def unregister_timer(self, timer_id: str) -> bool:
        """
        Entfernt einen Timer komplett
        
        Args:
            timer_id: Timer-ID
            
        Returns:
            True wenn erfolgreich entfernt
        """
        if timer_id not in self._timers:
            logger.warning(f"Timer '{timer_id}' nicht registriert")
            return False
        
        timer_info = self._timers[timer_id]
        
        # Timer stoppen falls aktiv
        if timer_info.active:
            timer_info.timer.stop()
        
        # Timer-Objekt löschen
        timer_info.timer.deleteLater()
        
        # Aus Registry entfernen
        del self._timers[timer_id]
        
        logger.debug(f"Timer '{timer_id}' entfernt")
        return True
    
    def get_timer_status(self) -> Dict[str, Any]:
        """
        Gibt Status aller Timer zurück
        
        Returns:
            Status-Dictionary mit Timer-Details
        """
        status = {
            'active_page': self._active_page,
            'total_timers': len(self._timers),
            'active_timers': sum(1 for t in self._timers.values() if t.active),
            'timers': {}
        }
        
        for timer_id, timer_info in self._timers.items():
            status['timers'][timer_id] = {
                'component': timer_info.component,
                'interval': timer_info.interval,
                'active': timer_info.active,
                'trigger_count': timer_info.trigger_count,
                'created_at': timer_info.created_at,
                'last_triggered': timer_info.last_triggered,
                'uptime': time.time() - timer_info.created_at
            }
        
        return status
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Gibt Memory-Statistiken zurück"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
                'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                'timer_count': len(self._timers),
                'active_timer_count': sum(1 for t in self._timers.values() if t.active)
            }
        except ImportError:
            # Fallback falls psutil nicht verfügbar
            return {
                'rss_mb': 0,
                'vms_mb': 0,
                'timer_count': len(self._timers),
                'active_timer_count': sum(1 for t in self._timers.values() if t.active)
            }
    
    def cleanup(self):
        """Aufräumen beim Programm-Ende"""
        logger.info("TimerManager Cleanup...")
        
        # Alle Timer stoppen und entfernen
        for timer_id in list(self._timers.keys()):
            self.unregister_timer(timer_id)
        
        self._active_page = None
        logger.info("TimerManager Cleanup abgeschlossen")

# Globale Instanz - späte Initialisierung
_timer_manager_instance: Optional[TimerManager] = None

def get_timer_manager() -> TimerManager:
    """Gibt die globale TimerManager-Instanz zurück (Lazy Loading)"""
    global _timer_manager_instance
    if _timer_manager_instance is None:
        _timer_manager_instance = TimerManager()
    return _timer_manager_instance