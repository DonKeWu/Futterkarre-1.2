# hardware/hx711_sim.py

import sys
import random

USE_SIMULATION = True

# hardware/hx711_sim.py
import random
import sys
from .sensor_interface import WeightSensorInterface

USE_SIMULATION = False  # Global flag


def setze_simulation(enabled: bool):
    """Schaltet Simulation ein/aus"""
    global USE_SIMULATION
    USE_SIMULATION = enabled
    print(f"HX711 Simulation: {'Ein' if enabled else 'Aus'}")


def simuliere_gewicht():
    """Simuliert realistisches Karrengewicht (0-100kg)"""
    return round(random.uniform(0, 100), 2)


def lese_einzelzellen():
    """Simuliert 4 einzelne Wägezellen für Debugging"""
    if USE_SIMULATION:
        return [round(random.uniform(0, 25), 2) for _ in range(4)]
    else:
        # Plattformprüfung aus alter Version
        if not sys.platform.startswith("linux") or "anaconda" in sys.executable.lower():
            print("Echtbetrieb nur auf Raspberry Pi möglich! Gebe 0er-Liste zurück.")
            return [0.0, 0.0, 0.0, 0.0]
        # Hier würde echte Einzelzellen-Abfrage stehen
        return [0.0, 0.0, 0.0, 0.0]


class HX711SimSensor(WeightSensorInterface):
    def __init__(self):
        self.base_weight = 5.0  # Grundgewicht der leeren Karre

    def read_weight(self) -> float:
        """Liest Gewicht mit Plattformprüfung aus alter Version"""
        if USE_SIMULATION:
            return simuliere_gewicht()
        else:
            # Clevere Plattformprüfung aus alter Version
            if not sys.platform.startswith("linux") or "anaconda" in sys.executable.lower():
                print("Echtbetrieb nur auf Raspberry Pi möglich! Gebe 0 zurück.")
                return 0.0

            # Hier würde echter HX711-Code stehen
            try:
                from hardware.hx711 import lese_gewicht_hx711
                return lese_gewicht_hx711()
            except ImportError:
                print("HX711-Bibliothek nicht verfügbar!")
                return 0.0

    def read_einzelzellen(self):
        """Zusätzliche Methode für Debugging"""
        return lese_einzelzellen()


# Globale Funktionen für Kompatibilität mit alter API
def lese_gewicht():
    """Kompatibilitätsfunktion für alten Code"""
    sensor = HX711SimSensor()
    return sensor.read_weight()

