# views/einstellungen_seite.py - Vereinfachte Einstellungen
import os
import logging

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer
import hardware.hx711_sim as hx711_sim

logger = logging.getLogger(__name__)

class EinstellungenSeite(QWidget):
    def __init__(self, sensor_manager):
        super().__init__()
        self.sensor_manager = sensor_manager
        self.navigation = None
        logger.info("EinstellungenSeite wird initialisiert")

        # UI-Datei laden
        ui_path = os.path.join(os.path.dirname(__file__), "einstellungen_seite.ui")
        uic.loadUi(ui_path, self)

        # Feste Fenstergröße für PiTouch2 (1280x720, minus 60px Statusleiste)
        self.setFixedSize(1280, 660)
        
        # Position: unter der Raspberry Pi Statusleiste (60px Abstand von oben)
        self.move(0, 60)

        # Standard-Simulation EIN (für Development)
        hx711_sim.setze_simulation(True)

        # Nur noch ein Simulation-Button
        self.btn_simulation_toggle.setCheckable(True)
        self.btn_simulation_toggle.setChecked(True)  # Standard: AN

        # Events verbinden
        self.connect_buttons()

        # Timer erstellen, aber NICHT für Gewichtsanzeige verwenden
        self.timer = QTimer()
        # self.timer.timeout.connect(self.update_weight)  # ENTFERNT!

    def start_timer(self):
        """Timer nicht mehr nötig auf Einstellungsseite"""
        pass  # Kein Timer für Gewichtsanzeige

    def stop_timer(self):
        """Timer nicht mehr nötig auf Einstellungsseite"""
        pass  # Kein Timer für Gewichtsanzeige

    def toggle_hx_simulation(self, checked):
        hx711_sim.setze_simulation(checked)
        logger.info(f"HX711 Simulation: {'aktiviert' if checked else 'deaktiviert'}")

    # toggle_fu_simulation entfernt - nur noch eine Simulation

    def zurueck_geklickt(self):
        """INTELLIGENTE Navigation - geht zur vorherigen Seite zurück"""
        logger.info("Zurück-Button geklickt - Intelligente Navigation")
        if self.navigation:
            self.navigation.go_back()  # Verwendet jetzt go_back() statt show_status("auswahl")
        else:
            logger.error("Navigation nicht verfügbar!")

    def update_weight(self):
        """Gewichtsanzeige gehört zur Kalibrierungsseite, nicht hier"""
        pass

    def connect_buttons(self):
        """Verbindet ALLE Buttons der Seite"""
        # Nur noch HX711-Simulation Button
        self.btn_simulation_toggle.clicked.connect(self.toggle_hx_simulation)

        # BACK-BUTTON VERBINDEN
        self.btn_back.clicked.connect(self.zurueck_geklickt)

        # NEUER Button für Futter-Konfiguration
        if hasattr(self, 'btn_futter_config'):
            self.btn_futter_config.clicked.connect(self.zu_futter_konfiguration)
            logger.info("Futter-Konfigurations-Button verbunden")
        else:
            logger.warning("btn_futter_config nicht gefunden - UI nicht aktuell?")

        logger.info("Alle Einstellungs-Buttons verbunden")

    def zu_futter_konfiguration(self):
        """Navigation zur Futter-Konfigurationsseite"""
        if self.navigation:
            logger.info("Wechsel zur Futter-Konfiguration")
            self.navigation.show_status("futter_konfiguration")