# views/auswahl_seite.py
import logging
import views.icons.icons_rc
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from pathlib import Path

logger = logging.getLogger(__name__)


class AuswahlSeite(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.navigation = None  # Wird von MainWindow gesetzt
        ui_path = Path(__file__).parent / "auswahl_seite.ui"
        uic.loadUi(str(ui_path), self)

        # Feste Fenstergröße für PiTouch2 (1280x720, minus 60px Statusleiste)
        self.setFixedSize(1280, 660)
        
        # Position: unter der Raspberry Pi Statusleiste (60px Abstand von oben)
        self.move(0, 60)

        # Buttons verbinden - aber erst nach dem UI-Laden!
        self.connect_buttons()

    def connect_buttons(self):
        """Verbindet Buttons nach UI-Laden"""
        if hasattr(self, 'btn_to_side_fu_heu'):
            self.btn_to_side_fu_heu.clicked.connect(self.zu_heu_futter)
        if hasattr(self, 'btn_to_side_fu_heulage'):
            self.btn_to_side_fu_heulage.clicked.connect(self.zu_heulage_futter)
        if hasattr(self, 'btn_to_side_fu_laden'):
            self.btn_to_side_fu_laden.clicked.connect(self.zu_beladen)
        if hasattr(self, 'btn_to_side_settings'):
            self.btn_to_side_settings.clicked.connect(self.zu_einstellungen)

        logger.info("AuswahlSeite Buttons verbunden")

    def zu_heu_futter(self):
        if self.navigation:
            self.navigation.show_status("fuettern")

    def zu_heulage_futter(self):
        if self.navigation:
            self.navigation.show_status("fuettern")

    def zu_beladen(self):
        if self.navigation:
            self.navigation.show_status("beladen")

    def zu_einstellungen(self):
        if self.navigation:
            self.navigation.show_status("einstellungen")
