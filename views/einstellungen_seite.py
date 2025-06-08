# views/einstellungen_seite.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel


class EinstellungenSeite(QWidget):
    def __init__(self, parent, sensor_manager):
        super().__init__(parent)
        self.sensor_manager = sensor_manager
        layout = QVBoxLayout()

        # WE-Auswahl
        self.btn_we_auswahl = QPushButton("Wiegeeinheit auswählen")
        self.btn_we_auswahl.clicked.connect(self.oeffne_we_auswahl)
        layout.addWidget(self.btn_we_auswahl)

        self.label_aktuelle_we = QLabel("Aktuelle WE: Futterkarre")
        layout.addWidget(self.label_aktuelle_we)

        # Simulation
        self.btn_simulation = QPushButton("Simulation an/aus")
        self.btn_simulation.setCheckable(True)
        self.btn_simulation.clicked.connect(self.toggle_simulation)
        layout.addWidget(self.btn_simulation)

        # Kalibrierung
        self.btn_kalibrieren = QPushButton("Kalibrieren")
        self.btn_kalibrieren.clicked.connect(self.kalibrierung_starten)
        layout.addWidget(self.btn_kalibrieren)

        # Gewichtsanzeige
        self.label_gewicht = QLabel("Gewicht: -- kg")
        layout.addWidget(self.label_gewicht)

        self.setLayout(layout)
