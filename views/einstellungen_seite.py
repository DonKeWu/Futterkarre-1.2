# views/einstellungen_seite.py
import os
import logging
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer
import hardware.hx711_sim as hx711_sim
import hardware.fu_sim as fu_sim

logger = logging.getLogger(__name__)

class EinstellungenSeite(QWidget):
    def __init__(self, parent, sensor_manager):
        super().__init__(parent)
        self.sensor_manager = sensor_manager
        logger.info("EinstellungenSeite wird initialisiert")

        # UI-Datei laden
        ui_path = os.path.join(os.path.dirname(__file__), "einstellungen_seite.ui")
        uic.loadUi(ui_path, self)

        # Simulationen standardmäßig AUS
        hx711_sim.setze_simulation(False)
        fu_sim.setze_simulation(False)

        # Buttons als Schalter konfigurieren
        self.btn_simulation_toggle.setCheckable(True)
        self.btn_simulation_toggle.setChecked(False)

        self.btn_fu_sim_toggle.setCheckable(True)
        self.btn_fu_sim_toggle.setChecked(False)

        # Events verbinden
        self.btn_simulation_toggle.clicked.connect(self.toggle_hx_simulation)
        self.btn_fu_sim_toggle.clicked.connect(self.toggle_fu_simulation)
        self.btn_back.clicked.connect(self.zurueck_geklickt)

        # Timer für Gewichtsanzeige
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_weight)
        self.timer.start(1000)

    def toggle_hx_simulation(self, checked):
        hx711_sim.setze_simulation(checked)
        logger.info(f"HX711 Simulation: {'aktiviert' if checked else 'deaktiviert'}")

    def toggle_fu_simulation(self, checked):
        fu_sim.setze_simulation(checked)
        logger.info(f"Fütterungs-Simulation: {'aktiviert' if checked else 'deaktiviert'}")

    def zurueck_geklickt(self):
        logger.info("Zurück-Button geklickt - Navigation zur Auswahl-Seite")
        if self.parent():
            self.parent().show_status("auswahl")
        else:
            logger.warning("Parent-Objekt nicht verfügbar für Navigation")

    def update_weight(self):
        try:
            weight = self.sensor_manager.read_weight()
            self.label_gewicht.setText(f"Gewicht: {weight:.2f} kg")
        except Exception as e:
            logger.error(f"Fehler beim Wiegen: {e}")
            self.label_gewicht.setText("Fehler beim Wiegen!")

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    import random

    app = QApplication(sys.argv)
    
    class DummySensor:
        def read_weight(self):
            if hx711_sim.USE_SIMULATION:
                return round(random.uniform(10, 100), 2)
            else:
                return 25.7

    window = EinstellungenSeite(None, DummySensor())
    window.resize(1024, 600)
    window.show()

    sys.exit(app.exec_())