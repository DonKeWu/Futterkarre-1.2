# hardware/sensor_manager.py
import sys
from .hx711_sim import HX711SimSensor, USE_SIMULATION as HX_SIM
from .fu_sim import USE_SIMULATION as FU_SIM, get_sim_weight
from .hx711_sensor import HX711Sensor


class SmartSensorManager:
    def __init__(self, data_pin=5, clock_pin=6):
        self.data_pin = data_pin
        self.clock_pin = clock_pin
        self._sensor = None

    @property
    def sensor(self):
        """Gibt den aktuell richtigen Sensor zurück"""
        if not self._sensor or self._sensor_type_changed():
            self._create_sensor()
        return self._sensor

    def _sensor_type_changed(self):
        """Prüft ob Sensor-Typ gewechselt wurde"""
        is_sim_now = HX_SIM
        was_sim = isinstance(self._sensor, HX711SimSensor)
        return is_sim_now != was_sim

    def _create_sensor(self):
        """Erstellt den richtigen Sensor je nach Simulationsmodus"""
        if HX_SIM:
            self._sensor = HX711SimSensor()
        else:
            # Plattformprüfung aus alter Version
            if not sys.platform.startswith("linux") or "anaconda" in sys.executable.lower():
                print("Warnung: Verwende Simulation da nicht auf Raspberry Pi!")
                self._sensor = HX711SimSensor()
            else:
                self._sensor = HX711Sensor(self.data_pin, self.clock_pin)

    def read_weight(self) -> float:
        """Liest Gewicht mit Fütterungssimulation"""
        base_weight = self.sensor.read_weight()

        # Wenn Fütterungssimulation an ist, überschreibe mit Sim-Gewicht
        if FU_SIM:
            return get_sim_weight()

        return base_weight

    def read_debug_info(self) -> dict:
        """Debug-Informationen für Entwicklung"""
        info = {
            "hx_simulation": HX_SIM,
            "fu_simulation": FU_SIM,
            "platform": sys.platform,
            "sensor_type": type(self._sensor).__name__
        }

        # Einzelzellen nur bei Simulation
        if HX_SIM and hasattr(self.sensor, 'read_einzelzellen'):
            info["einzelzellen"] = self.sensor.read_einzelzellen()

        return info
