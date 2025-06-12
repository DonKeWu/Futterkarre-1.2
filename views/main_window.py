# views/main_window.py
import logging
logger = logging.getLogger(__name__)
import views.icons.icons_rc
from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore import QTimer

from views.start import StartSeite  # DIESER IMPORT FEHLT!
from views.fuettern_seite import FuetternSeite
from views.auswahl_seite import AuswahlSeite
from views.einstellungen_seite import EinstellungenSeite
from views.beladen_seite import BeladenSeite
from views.futter_konfiguration import FutterKonfiguration

class MainWindow(QMainWindow):
    def __init__(self, sensor_manager):  # OHNE heu_namen!
        super().__init__()
        self.sensor_manager = sensor_manager

        self.pferde_liste = []
        self.aktueller_pferd_index = 0
        self.pferde_liste = self.lade_pferde_daten()

        # Navigation
        self.previous_page = "auswahl"
        self.previous_context = {}
        self.current_status = "start"
        self.current_context = {}

        logger.info("MainWindow wird initialisiert")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Futterkarre 2.0")
        self.setFixedSize(1024, 600)

        self.stacked_widget = QStackedWidget()

        # Seiten anlegen
        self.start_screen = StartSeite()
        self.auswahl_seite = AuswahlSeite()
        self.beladen_seite = BeladenSeite(sensor_manager=self.sensor_manager)
        self.fuettern_seite = FuetternSeite()
        self.einstellungen_seite = EinstellungenSeite(sensor_manager=self.sensor_manager)

        # NEUE Seite hinzufügen
        self.futter_konfiguration = FutterKonfiguration()

        # Navigation für alle Seiten setzen
        for seite in [self.start_screen, self.auswahl_seite, self.beladen_seite,
                      self.fuettern_seite, self.einstellungen_seite, self.futter_konfiguration]:
            seite.navigation = self

        # Seiten zum Stack hinzufügen
        self.stacked_widget.addWidget(self.start_screen)
        self.stacked_widget.addWidget(self.auswahl_seite)
        self.stacked_widget.addWidget(self.beladen_seite)
        self.stacked_widget.addWidget(self.fuettern_seite)
        self.stacked_widget.addWidget(self.einstellungen_seite)
        self.stacked_widget.addWidget(self.futter_konfiguration)

        self.setCentralWidget(self.stacked_widget)
        self.show_status("start")
        self.connect_navigation()

    def set_futter_daten(self, heu_liste=None, heulage_liste=None, pellet_liste=None):
        """Empfängt Futter-Daten von der Konfigurationsseite"""
        if heu_liste:
            self.heu_liste = heu_liste
        if heulage_liste:
            self.heulage_liste = heulage_liste
        if pellet_liste:
            self.pellet_liste = pellet_liste

        logger.info(f"Futter-Daten gesetzt: {len(self.heu_liste)} Heu, "
                    f"{len(self.heulage_liste)} Heulage, {len(self.pellet_liste)} Pellets")

    def connect_navigation(self):
        """Alle Seiten verwenden jetzt self.navigation - KEINE manuelle Verbindung nötig!"""
        pass

    def show_status(self, status, context=None, from_back=False):
        """Navigation mit Back-Button Unterstützung"""
        logger.info(f"Wechsel zu Status: {status}")

        # Timer stoppen bei Seitenwechsel
        self.stop_all_timers()

        # Vorherige Seite merken (außer bei Back-Navigation) - NACH Timer-Stop!
        if not from_back and self.current_status != status:
            self.previous_page = self.current_status
            self.previous_context = self.current_context.copy()
            logger.info(f"Vorherige Seite gespeichert: {self.previous_page}")

        # Aktuellen Status setzen - NACH dem Speichern der vorherigen Seite!
        self.current_status = status
        self.current_context = context or {}

        if status == "start":
            self.stacked_widget.setCurrentWidget(self.start_screen)
        elif status == "auswahl":
            self.stacked_widget.setCurrentWidget(self.auswahl_seite)
        elif status == "beladen":
            self.stacked_widget.setCurrentWidget(self.beladen_seite)
            if context:
                self.beladen_seite.set_context(context)
            self.beladen_seite.start_timer()
        elif status == "fuettern":
            self.stacked_widget.setCurrentWidget(self.fuettern_seite)
            if context:
                self.fuettern_seite.restore_context(context)
        elif status == "einstellungen":
            self.stacked_widget.setCurrentWidget(self.einstellungen_seite)
            # Timer NACH der Navigation starten
            self.einstellungen_seite.start_timer()
        elif status == "futter_konfiguration":
            self.stacked_widget.setCurrentWidget(self.futter_konfiguration)

    def stop_all_timers(self):
        """Stoppt alle Timer - verhindert Dauerschleifen"""
        if hasattr(self.beladen_seite, 'timer'):
            self.beladen_seite.timer.stop()
        if hasattr(self.einstellungen_seite, 'timer'):
            self.einstellungen_seite.timer.stop()

    # Einfache Navigation-Methoden (bleiben unverändert)
    # === NAVIGATION METHODEN ===
    def zeige_heu_futter(self):
        """Zeigt Heu-Fütterung mit echten Pferd-Daten"""
        aktuelles_pferd = self.get_aktuelles_pferd()
        self.show_status("fuettern")

        if aktuelles_pferd:
            self.fuettern_seite.zeige_pferd_daten(aktuelles_pferd)
            self.fuettern_seite.start_timer()

    def zeige_heulage_futter(self):
        """Zeigt Heulage-Fütterung mit echten Daten"""
        aktuelles_pferd = self.get_aktuelles_pferd()  # KORRIGIERT
        self.show_status("fuettern")

        if aktuelles_pferd:
            self.fuettern_seite.zeige_pferd_daten(aktuelles_pferd)  # KORRIGIERT
            self.fuettern_seite.start_timer()

    def zeige_futter_laden(self):
        self.show_status("beladen")

    def zeige_einstellungen(self):
        self.show_status("einstellungen")

    def go_back(self):
        """Intelligenter Back-Button - geht zur vorherigen Seite"""
        logger.info(f"Back-Button: Aktuell={self.current_status}, Zurück zu={self.previous_page}")
        logger.info(f"Navigation-History: {self.previous_page} → {self.current_status}")

        if self.previous_page and self.previous_page != self.current_status:
            self.show_status(self.previous_page, self.previous_context, from_back=True)
        else:
            logger.warning(f"Ungültige Navigation: previous_page={self.previous_page}, current={self.current_status}")
            # Fallback zur Auswahl
            self.show_status("auswahl", from_back=True)

    # === PFERDE-MANAGEMENT ===


    def get_aktuelles_pferd(self):
        """Gibt das aktuelle Pferd zurück"""
        if not hasattr(self, 'pferde_liste'):
            self.pferde_liste = self.lade_pferde_daten()
            self.aktueller_pferd_index = 0

        if self.pferde_liste and 0 <= self.aktueller_pferd_index < len(self.pferde_liste):
            return self.pferde_liste[self.aktueller_pferd_index]
        return None

    def naechstes_pferd(self):
        """Wechselt zum nächsten Pferd in der Liste"""
        if self.pferde_liste:
            self.aktueller_pferd_index = (self.aktueller_pferd_index + 1) % len(self.pferde_liste)
            logger.info(f"Wechsel zu Pferd {self.aktueller_pferd_index + 1}: {self.get_aktuelles_pferd().name}")
            return self.get_aktuelles_pferd()
        return None
