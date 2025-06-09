# views/main_window.py
import logging
from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore import QTimer

from views.start import StartSeite
from views.fuettern_seite import FuetternSeite
from views.auswahl_seite import AuswahlSeite
from views.einstellungen_seite import EinstellungenSeite
from views.beladen_seite import BeladenSeite  # Neue Klasse statt create_load_screen

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, sensor_manager, heu_namen=None):
        super().__init__()
        self.sensor_manager = sensor_manager  # Statt sensor
        self.heu_namen = heu_namen if heu_namen is not None else []
        logger.info("MainWindow wird initialisiert")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Futterkarre 2.0")
        self.setFixedSize(1024, 600)

        self.stacked_widget = QStackedWidget()

        # Seiten anlegen (alle als Klassen)
        self.start_screen = StartSeite()
        self.auswahl_seite = AuswahlSeite(parent=self)
        self.beladen_seite = BeladenSeite(parent=self, sensor_manager=self.sensor_manager)
        self.fuettern_seite = FuetternSeite(parent=self)
        self.einstellungen_seite = EinstellungenSeite(parent=self, sensor_manager=self.sensor_manager)

        # Seiten zum Stack hinzufügen
        self.stacked_widget.addWidget(self.start_screen)  # Index 0
        self.stacked_widget.addWidget(self.auswahl_seite)  # Index 1
        self.stacked_widget.addWidget(self.beladen_seite)  # Index 2
        self.stacked_widget.addWidget(self.fuettern_seite)  # Index 3
        self.stacked_widget.addWidget(self.einstellungen_seite)  # Index 4

        self.setCentralWidget(self.stacked_widget)
        self.show_status("start")

        # Navigation verbinden
        self.connect_navigation()

    def connect_navigation(self):
        """Verbindet alle Navigations-Events"""
        # Start → Auswahl
        self.start_screen.btn_start.clicked.connect(lambda: self.show_status("auswahl"))

        # Beladen → Füttern
        self.beladen_seite.btn_beladung_abgeschlossen.clicked.connect(
            lambda: self.show_status("fuettern")
        )

        # Füttern Navigation
        self.fuettern_seite.btn_naechstes_pferd.clicked.connect(
            lambda: self.show_status("start")  # Zurück zum Start
        )
        self.fuettern_seite.btn_nachladen.clicked.connect(
            lambda: self.show_status("beladen")
        )

    def show_status(self, status):
        """Zentrale Navigation zwischen Seiten"""
        logger.info(f"Wechsel zu Status: {status}")

        if status == "start":
            self.stacked_widget.setCurrentWidget(self.start_screen)
        elif status == "auswahl":
            self.stacked_widget.setCurrentWidget(self.auswahl_seite)
        elif status == "beladen":
            self.stacked_widget.setCurrentWidget(self.beladen_seite)
        elif status == "fuettern":
            self.stacked_widget.setCurrentWidget(self.fuettern_seite)
        elif status == "einstellungen":
            self.stacked_widget.setCurrentWidget(self.einstellungen_seite)

    # Methoden für AuswahlSeite
    def zeige_heu_futter(self):
        self.show_status("fuettern")

    def zeige_heulage_futter(self):
        self.show_status("fuettern")

    def zeige_futter_laden(self):
        self.show_status("beladen")

    def zeige_einstellungen(self):
        self.show_status("einstellungen")
