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
    # Fullscreen-Modus - komplette Display-Nutzung 1280x720
    WINDOW_WIDTH = 1280   # Native Breite (Landscape)
    WINDOW_HEIGHT = 720   # Native Höhe - Fullscreen
    WINDOW_Y_OFFSET = 0   # Fullscreen - keine Verschiebung
    TOUCH_OPTIMIZED = True


