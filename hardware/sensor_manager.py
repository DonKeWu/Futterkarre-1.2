# hardware/sensor_manager.py - KORRIGIERTE VERSION
import hardware.hx711_sim as hx711_sim
import hardware.fu_sim as fu_sim
import sys

class SmartSensorManager:
    def read_weight(self) -> float:
        """Liest Gewicht: Simulation oder echte Hardware"""

        # KORRIGIERT: Verwende ist_simulation_aktiv() statt USE_SIMULATION
        if hx711_sim.ist_simulation_aktiv():
            # Simulation aktiv
            if fu_sim.ist_simulation_aktiv():
                return fu_sim.get_sim_weight()  # Fütterungssimulation
            else:
                # HX711-Simulation - zufällige Werte
                import random
                gewicht = round(random.uniform(15.0, 45.0), 2)
                print(f"HX711-Simulation: {gewicht} kg")  # Debug
                return gewicht
        else:
            # PRODUKTIVBETRIEB - echte Hardware
            try:
                if sys.platform.startswith("linux") and "anaconda" not in sys.executable.lower():
                    # Auf Raspberry Pi - echte Hardware
                    from hardware.hx711_sensor import lese_gewicht_hx711
                    return lese_gewicht_hx711()
                else:
                    # Entwicklungsrechner - keine Hardware verfügbar
                    print("Warnung: Keine echte Hardware verfügbar (nicht auf Raspberry Pi)")
                    return 0.0
            except Exception as e:
                print(f"Fehler beim Lesen der echten Hardware: {e}")
                return 0.0
