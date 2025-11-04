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

    # UI-Einstellungen - RESPONSIVE für alle Bildschirmgrößen
    WINDOW_WIDTH = 1024   # Basis-Breite
    WINDOW_HEIGHT = 768   # Basis-Höhe (wird automatisch angepasst)
    TOUCH_OPTIMIZED = True


