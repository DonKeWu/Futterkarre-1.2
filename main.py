# main.py - NUR Grundfunktionen
from config.logging_config import setup_logging

setup_logging()
import logging

logger = logging.getLogger(__name__)

import sys
import os
from config.app_config import AppConfig
from hardware.sensor_manager import SmartSensorManager
from views.main_window import MainWindow

# DPI-Einstellungen - KOMPLETT DEAKTIVIERT für native Skalierung
# os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
# os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
# os.environ["QT_SCALE_FACTOR"] = "1.0"

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication

# KEINE DPI-Skalierung mehr - natürliche Größe
# QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
# QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


def main():
    try:
        # 1. Hardware initialisieren
        sensor_manager = SmartSensorManager()
        logger.info("Sensor Manager initialisiert")

        # 2. Simulation aktivieren für Entwicklung
        if AppConfig.DEBUG_MODE:
            import hardware.hx711_sim as hx711_sim
            hx711_sim.setze_simulation(True)
            logger.info("HX711-Simulation aktiviert")

            # DEBUG: Sofort testen
            print(f"DEBUG: HX711 aktiv? {hx711_sim.ist_simulation_aktiv()}")

        # 3. PyQt-Anwendung starten - OHNE Daten zu laden!
        app = QApplication(sys.argv)
        window = MainWindow(sensor_manager)  # Keine heu_namen mehr!
        
        # ECHTER Fullscreen-Modus - versteckt Statusleiste komplett
        window.showFullScreen()
        logger.info("MainWindow gestartet im ECHTEN Fullscreen-Modus")

        sys.exit(app.exec_())

    except Exception as e:
        logger.error(f"Kritischer Fehler in main(): {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

