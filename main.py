# main.py - Pi5-optimiert mit erweitertem Logging
from config.logging_config import setup_logging, get_pi5_logger
import logging

# Pi5-optimiertes Logging initialisieren
pi5_logger = setup_logging(enable_remote_debug=False)
logger = logging.getLogger(__name__)

# Context-spezifische Logger für verschiedene Bereiche
startup_logger = pi5_logger.create_context_logger("startup")
deployment_logger = pi5_logger.create_context_logger("pi5-deployment")

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
        startup_logger.info("🚀 Futterkarre Pi5-Startup gestartet")
        
        # System-Metriken loggen
        pi5_logger.log_system_metrics()
        
        # 1. Hardware initialisieren
        startup_logger.info("⚙️ Hardware-Initialisierung...")
        sensor_manager = SmartSensorManager()
        startup_logger.info("✅ Sensor Manager initialisiert")

        # 2. Hardware-Modus aktivieren
        deployment_logger.info("🔧 Hardware-only Modus aktiviert")
        startup_logger.info("✅ Hardware-Modus bereit")

        # 3. PyQt-Anwendung starten
        startup_logger.info("🖥️ PyQt5-GUI wird initialisiert...")
        app = QApplication(sys.argv)
        window = MainWindow(sensor_manager)
        
        # 4. Display-Modus basierend auf Parametern
        if "--window" in sys.argv or "--windows" in sys.argv:
            window.resize(1280, 720)
            window.show()
            startup_logger.info("🪟 MainWindow gestartet im Fenster-Modus (1280x720)")
            deployment_logger.info("Fenster-Modus aktiv - wahrscheinlich Test-Umgebung")
        else:
            window.showFullScreen()
            startup_logger.info("📺 MainWindow gestartet im Vollbild-Modus (Pi5-Display)")
            deployment_logger.info("Vollbild-Modus aktiv - Pi5-Produktion")
        
        startup_logger.info("🎯 Futterkarre erfolgreich gestartet - GUI bereit")
        
        # Event-Loop starten
        sys.exit(app.exec_())
        
    except Exception as e:
        startup_logger.error(f"❌ Kritischer Startup-Fehler: {e}")
        deployment_logger.error(f"Pi5-Deployment fehlgeschlagen: {e}")
        
        # Debug-Informationen für Remote-Diagnose
        import traceback
        deployment_logger.error(f"Traceback: {traceback.format_exc()}")
        
        sys.exit(1)


if __name__ == "__main__":
    main()

