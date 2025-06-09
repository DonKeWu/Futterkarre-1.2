# main.py (aufgeräumt)
import sys
from PyQt5.QtWidgets import QApplication
from views.main_window import MainWindow
from hardware.sensor_manager import SmartSensorManager  # Statt sensor_switch
from config.logging_config import setup_logging
import logging


def main():
    # Logging einrichten
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Futterkarre 2.0 startet")

    app = QApplication(sys.argv)

    # SensorManager statt direkter Sensor
    sensor_manager = SmartSensorManager()

    # Dummy Heu-Namen (später aus CSV laden)
    heu_namen = ["Heu 2025", "Heulage 2025"]

    window = MainWindow(sensor_manager, heu_namen)
    window.show()

    logger.info("App gestartet")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

