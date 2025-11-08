#!/usr/bin/env python3
"""
WeightManager - Zentraler Singleton für Gewichtsverwaltung
Löst Inkonsistenzen zwischen Simulation und Hardware

Funktionen:
- Einheitliche Gewichtsquelle für alle UI-Komponenten
- Automatische Simulation/Hardware-Umschaltung
- State-Management für Gewichtssynchronisation
- Event-basierte Gewichtsupdates für UI
"""

import time
import logging
from typing import Optional, Callable, Dict, Any
from threading import Lock
from dataclasses import dataclass, field

# Hardware-Module
import hardware.hx711_sim as hx711_sim

logger = logging.getLogger(__name__)

@dataclass
class WeightState:
    """Zentraler Gewichtszustand"""
    current_weight: float = 0.0
    last_update: float = field(default_factory=time.time)
    is_simulation: bool = True
    hardware_available: bool = False
    error_count: int = 0
    last_error: Optional[str] = None

class WeightManager:
    """
    Singleton für zentrale Gewichtsverwaltung
    
    Koordiniert zwischen:
    - HX711 Hardware (4 Wägezellen)
    - Simulation (hx711_sim)
    - UI-Updates (FuetternSeite, BeladenSeite)
    """
    
    _instance: Optional['WeightManager'] = None
    _lock = Lock()
    
    def __new__(cls) -> 'WeightManager':
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
        self.state = WeightState()
        self._observers: Dict[str, Callable[[float], None]] = {}
        self._hardware_interface = None
        
        # Hardware-Verfügbarkeit prüfen
        self._detect_hardware()
        
        logger.info(f"WeightManager initialisiert - Hardware: {self.state.hardware_available}, Simulation: {self.state.is_simulation}")
    
    def _detect_hardware(self):
        """Prüft Hardware-Verfügbarkeit und initialisiert entsprechend"""
        try:
            import sys
            if sys.platform.startswith("linux") and "anaconda" not in sys.executable.lower():
                # Auf Raspberry Pi - versuche echte Hardware
                try:
                    from hardware.hx711_real import lese_gewicht_hx711, hx_sensors
                    if hx_sensors:  # Hardware erfolgreich initialisiert
                        self.state.hardware_available = True
                        self.state.is_simulation = False
                        self._hardware_interface = 'real'
                        logger.info("✅ HX711 Hardware erkannt und initialisiert")
                    else:
                        raise RuntimeError("HX711-Sensoren nicht verfügbar")
                except Exception as e:
                    logger.warning(f"HX711 Hardware nicht verfügbar: {e}")
                    self._fallback_to_simulation()
            else:
                # Entwicklungsrechner - automatisch Simulation
                self._fallback_to_simulation()
                
        except Exception as e:
            logger.error(f"Hardware-Erkennung fehlgeschlagen: {e}")
            self._fallback_to_simulation()
    
    def _fallback_to_simulation(self):
        """Wechselt zur Simulation"""
        self.state.hardware_available = False
        self.state.is_simulation = True
        self._hardware_interface = 'simulation'
        
        # Simulation aktivieren
        hx711_sim.setze_simulation(True)
        logger.info("🎮 Fallback zu HX711-Simulation aktiviert")
    
    def read_weight(self, use_cache: bool = True) -> float:
        """
        Liest aktuelles Gewicht von Hardware oder Simulation
        
        Args:
            use_cache: Verwende zwischengespeicherten Wert wenn verfügbar
            
        Returns:
            Gewicht in kg
        """
        current_time = time.time()
        
        # Cache-Logik: Nur alle 100ms neu lesen (Performance)
        if use_cache and (current_time - self.state.last_update) < 0.1:
            return self.state.current_weight
        
        try:
            if self.state.is_simulation:
                # Simulation verwenden
                weight = hx711_sim.simuliere_gewicht()
            else:
                # Echte Hardware verwenden
                from hardware.hx711_real import lese_gewicht_hx711
                weight = lese_gewicht_hx711()
            
            # State aktualisieren
            self.state.current_weight = max(0.0, weight)  # Negative Gewichte verhindern
            self.state.last_update = current_time
            self.state.error_count = 0
            self.state.last_error = None
            
            # Observer benachrichtigen
            self._notify_observers(self.state.current_weight)
            
            return self.state.current_weight
            
        except Exception as e:
            self.state.error_count += 1
            self.state.last_error = str(e)
            logger.error(f"Gewichtslesung fehlgeschlagen: {e}")
            
            # Bei wiederholten Fehlern zur Simulation wechseln
            if self.state.error_count > 3 and not self.state.is_simulation:
                logger.warning("Zu viele Hardware-Fehler - Wechsel zur Simulation")
                self._fallback_to_simulation()
                return self.read_weight(use_cache=False)
            
            return self.state.current_weight  # Letzten gültigen Wert zurückgeben
    
    def read_individual_cells(self) -> list[float]:
        """
        Liest die 4 Wägezellen einzeln (für Kalibrierung/Debugging)
        
        Returns:
            Liste mit 4 Gewichtswerten [VL, VR, HL, HR]
        """
        try:
            if self.state.is_simulation:
                return hx711_sim.lese_einzelzellen()
            else:
                from hardware.hx711_real import lese_einzelzellwerte_hx711
                return lese_einzelzellwerte_hx711()
                
        except Exception as e:
            logger.error(f"Einzelzellwerte nicht lesbar: {e}")
            return [0.0, 0.0, 0.0, 0.0]
    
    def register_observer(self, name: str, callback: Callable[[float], None]):
        """
        Registriert einen Observer für Gewichtsupdates
        
        Args:
            name: Eindeutige ID des Observers
            callback: Funktion die bei Gewichtsänderung aufgerufen wird
        """
        self._observers[name] = callback
        logger.debug(f"Observer '{name}' registriert")
    
    def unregister_observer(self, name: str):
        """Entfernt einen Observer"""
        if name in self._observers:
            del self._observers[name]
            logger.debug(f"Observer '{name}' entfernt")
    
    def _notify_observers(self, weight: float):
        """Benachrichtigt alle Observer über Gewichtsänderung"""
        for name, callback in self._observers.items():
            try:
                callback(weight)
            except Exception as e:
                logger.error(f"Observer '{name}' Fehler: {e}")
    
    def set_simulation_mode(self, enabled: bool):
        """
        Schaltet zwischen Simulation und Hardware um
        
        Args:
            enabled: True für Simulation, False für Hardware
        """
        if enabled:
            self._fallback_to_simulation()
        else:
            if self.state.hardware_available:
                self.state.is_simulation = False
                self._hardware_interface = 'real'
                hx711_sim.setze_simulation(False)
                logger.info("🔧 Gewichtsmodus: Hardware")
            else:
                logger.warning("Hardware nicht verfügbar - bleibe bei Simulation")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Gibt aktuellen Status zurück
        
        Returns:
            Status-Dictionary mit Details
        """
        return {
            'current_weight': self.state.current_weight,
            'is_simulation': self.state.is_simulation,
            'hardware_available': self.state.hardware_available,
            'interface': self._hardware_interface,
            'last_update': self.state.last_update,
            'error_count': self.state.error_count,
            'last_error': self.state.last_error,
            'observers_count': len(self._observers)
        }
    
    def tare_weight(self) -> bool:
        """
        Setzt Nullpunkt (Tara) für alle Wägezellen
        
        Returns:
            True wenn erfolgreich
        """
        try:
            if self.state.is_simulation:
                # Simulation: Gewicht auf 0 setzen
                hx711_sim.reset_karre()
                logger.info("Simulation: Nullpunkt gesetzt")
                return True
            else:
                # Hardware: Alle Sensoren tarieren
                from hardware.hx711_real import nullpunkt_setzen_alle
                success = nullpunkt_setzen_alle()
                if success:
                    logger.info("Hardware: Nullpunkt gesetzt")
                return bool(success)
                
        except Exception as e:
            logger.error(f"Nullpunkt setzen fehlgeschlagen: {e}")
            return False
    
    def simulate_weight_change(self, delta_kg: float):
        """
        Simuliert Gewichtsänderung (nur in Simulation)
        
        Args:
            delta_kg: Gewichtsänderung in kg (positiv = hinzufügen, negativ = entfernen)
        """
        if not self.state.is_simulation:
            logger.warning("Gewichtssimulation nur im Simulationsmodus möglich")
            return
        
        workflow_sim = hx711_sim.get_workflow_simulation()
        alte_menge = workflow_sim.karre_gewicht
        print(f"🔄 simulate_weight_change({delta_kg:+.1f}kg) - Vor: {alte_menge:.1f}kg")
        
        if delta_kg > 0:
            hx711_sim.karre_beladen(delta_kg)
        elif delta_kg < 0:
            # Manuelle Entnahme simulieren
            workflow_sim.karre_gewicht += delta_kg
            if workflow_sim.karre_gewicht < 0:
                workflow_sim.karre_gewicht = 0.0
        
        neue_menge = workflow_sim.karre_gewicht
        logger.info(f"Simulation: Gewicht um {delta_kg:+.1f}kg geändert")
        print(f"✅ Nach Änderung: {neue_menge:.1f}kg (Differenz: {neue_menge - alte_menge:+.1f}kg)")

# Globale Instanz für einfachen Zugriff
weight_manager = WeightManager()

def get_weight_manager() -> WeightManager:
    """Gibt die globale WeightManager-Instanz zurück"""
    return weight_manager