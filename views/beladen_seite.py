# views/beladen_seite.py
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer


class BeladenSeite(QWidget):
    def __init__(self, parent, sensor_manager):
        super().__init__(parent)
        self.sensor_manager = sensor_manager

        # UI laden (oder im Code erstellen)
        ui_path = os.path.join(os.path.dirname(__file__), "beladen_seite.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        else:
            self.create_ui_in_code()

        # Timer für Gewichtsanzeige
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_weight)
        self.timer.start(1000)

    def create_ui_in_code(self):
        # Fallback falls keine UI-Datei vorhanden
        from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton
        layout = QVBoxLayout()
        self.label_gewicht = QLabel("Gewicht: -- kg")
        self.btn_beladung_abgeschlossen = QPushButton("Beladung abgeschlossen")
        layout.addWidget(self.label_gewicht)
        layout.addWidget(self.btn_beladung_abgeschlossen)
        self.setLayout(layout)

    def update_weight(self):
        try:
            weight = self.sensor_manager.read_weight()
            self.label_gewicht.setText(f"Gewicht: {weight:.2f} kg")
        except Exception as e:
            self.label_gewicht.setText("Fehler beim Wiegen!")
