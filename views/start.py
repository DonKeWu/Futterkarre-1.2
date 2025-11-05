# views/start.py
import os
import views.icons.icons_rc
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class StartSeite(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.navigation = None  # Wird von MainWindow gesetzt

        # Ermittle den absoluten Pfad zur start.ui relativ zu diesem Skript
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, 'start.ui')
        uic.loadUi(ui_path, self)

        # Vollbild für PiTouch2 (1280x720) - komplette Display-Nutzung
        self.setFixedSize(1280, 720)
        
        # Position: oben links (0,0) - Display vollständig nutzen
        self.move(0, 0)

        # Button verbinden
        self.btn_start.clicked.connect(self.zu_auswahl)

    def zu_auswahl(self):
        if self.navigation:
            self.navigation.show_status("auswahl")

