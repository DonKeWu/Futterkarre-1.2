# config/app_config.py
class AppConfig:
    # Display-Einstellungen für PyQt5 - AUTO-SCALING für alle Auflösungen
    QT_AUTO_SCREEN_SCALE_FACTOR = "1"
    QT_ENABLE_HIGHDPI_SCALING = "1"
    QT_SCALE_FACTOR = "1.0"  # Automatische Skalierung aktiviert

    # Debug-Modus - FEHLTE!
    DEBUG_MODE = True

    # Hardware-Einstellungen
    USE_HARDWARE_SIMULATION = True

    # Logging-Level
    LOG_LEVEL = "INFO"

    # Pfade
    DATA_PATH = "data/"
    LOGS_PATH = "logs/"

    # UI-Einstellungen - Raspberry Pi Touch Display 2 (Landscape)
    # Fenster um 60px nach unten verschoben, damit Raspberry Logo sichtbar bleibt
    WINDOW_WIDTH = 1280   # Native Breite (Landscape)
    WINDOW_HEIGHT = 660   # Native Höhe minus 60px für Logo-Bereich
    WINDOW_Y_OFFSET = 60  # Verschiebung nach unten
    TOUCH_OPTIMIZED = True


