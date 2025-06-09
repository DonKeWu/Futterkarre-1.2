# test_einstellungen.py
import sys
import os

# Pfad zum Projekt hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt

# Direkte Imports ohne main.py
from views.einstellungen_seite import EinstellungenSeite
from hardware.sensor_manager import SmartSensorManager


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test: Einstellungsseite")
        self.setFixedSize(1024, 600)

        # Sensor Manager für Test
        self.sensor_manager = SmartSensorManager()

        # Einstellungsseite als Central Widget
        self.einstellungen = EinstellungenSeite(self, self.sensor_manager)
        self.setCentralWidget(self.einstellungen)


def main():
    app = QApplication(sys.argv)

    # Für Touch-Optimierung
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    window = TestWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
