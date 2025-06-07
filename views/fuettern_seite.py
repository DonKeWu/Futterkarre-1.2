# views/fuettern_seite.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QButtonGroup
from PyQt5.QtCore import Qt

class FuetternSeite(QWidget):
    def __init__(self, pferd=None, parent=None):
        super().__init__(parent)
        self.pferd = pferd  # Optional: aktuelles Pferd-Objekt

        # Layouts
        main_layout = QVBoxLayout()
        futterart_layout = QHBoxLayout()
        navigation_layout = QHBoxLayout()

        # Pferdeanzeige
        self.label_pferd = QLabel("Kein Pferd gewählt")
        self.label_pferd.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.label_pferd)

        # Futterart-Schalter (Wechselschaltung)
        self.futterart_group = QButtonGroup(self)
        self.futterart_buttons = {}
        futterarten = ["Heu", "Heulage", "Kraftfutter", "Hafer"]
        for i, art in enumerate(futterarten):
            btn = QPushButton(art)
            btn.setCheckable(True)
            btn.setMinimumHeight(80)
            btn.setMinimumWidth(180)
            if i == 0:
                btn.setChecked(True)  # Standard: Heu ausgewählt
            self.futterart_group.addButton(btn, i)
            self.futterart_buttons[art] = btn
            futterart_layout.addWidget(btn)
        main_layout.addLayout(futterart_layout)

        # Gewichtsanzeige (hier als Platzhalter)
        self.label_gewicht = QLabel("Gewicht: -- kg")
        self.label_gewicht.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.label_gewicht)

        # Navigationsbuttons
        self.btn_nachladen = QPushButton("Nachladen")
        self.btn_fuettern = QPushButton("Füttern")
        self.btn_naechstes_pferd = QPushButton("Nächstes Pferd")
        self.btn_nachladen.setMinimumHeight(60)
        self.btn_fuettern.setMinimumHeight(60)
        self.btn_naechstes_pferd.setMinimumHeight(60)
        navigation_layout.addWidget(self.btn_nachladen)
        navigation_layout.addWidget(self.btn_fuettern)
        navigation_layout.addWidget(self.btn_naechstes_pferd)
        main_layout.addLayout(navigation_layout)

        self.setLayout(main_layout)

        # Events verbinden (hier nur als Platzhalter)
        self.futterart_group.buttonClicked.connect(self.futterart_gewaehlt)
        self.btn_fuettern.clicked.connect(self.fuettern)
        self.btn_nachladen.clicked.connect(self.nachladen)
        self.btn_naechstes_pferd.clicked.connect(self.naechstes_pferd)

    def futterart_gewaehlt(self, button):
        print(f"Futterart gewählt: {button.text()}")

    def fuettern(self):
        print("Fütterung bestätigt!")

    def nachladen(self):
        print("Nachladen gedrückt!")

    def naechstes_pferd(self):
        print("Nächstes Pferd gedrückt!")

    def setze_pferd(self, pferd):
        """Setzt das aktuelle Pferd und aktualisiert die Anzeige."""
        self.pferd = pferd
        self.label_pferd.setText(f"{pferd.name} ({pferd.gewicht} kg)")
