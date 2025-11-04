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
from views.fuetterung_abschluss import FuetterungAbschluss

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

        # Futter-Listen initialisieren
        self.heu_liste = []
        self.heulage_liste = []
        self.pellet_liste = []
        
        # Standard-Futter-Daten laden
        self.lade_standard_futter_daten()

        logger.info("MainWindow wird initialisiert")
        self.init_ui()
        
    def lade_standard_futter_daten(self):
        """Lädt Standard-Futter-Daten beim Start"""
        try:
            from utils.futter_loader import lade_heu_als_dataclasses, lade_heulage_als_dataclasses
            
            # Standard-Heu laden
            self.heu_liste = lade_heu_als_dataclasses("heu_eigen_2025.csv")
            logger.info(f"Standard-Heu geladen: {len(self.heu_liste)} Einträge")
            
            # Standard-Heulage laden
            self.heulage_liste = lade_heulage_als_dataclasses("heulage_eigen_2025.csv")
            logger.info(f"Standard-Heulage geladen: {len(self.heulage_liste)} Einträge")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Standard-Futter-Daten: {e}")
            # Fallback: Leere Listen
            self.heu_liste = []
            self.heulage_liste = []

    def init_ui(self):
        from config.app_config import AppConfig
        
        self.setWindowTitle("Futterkarre 2.0")
        # Fenster-Größe und Position für 60px Y-Offset (Raspberry Logo sichtbar)
        self.setFixedSize(AppConfig.WINDOW_WIDTH, AppConfig.WINDOW_HEIGHT)
        
        # Responsive Sizing für unterschiedliche Bildschirmgrößen
        self.setMinimumSize(800, 480)  # Minimum für Touch-Displays

        self.stacked_widget = QStackedWidget()

        # Seiten anlegen
        self.start_screen = StartSeite()
        self.auswahl_seite = AuswahlSeite()
        self.beladen_seite = BeladenSeite(sensor_manager=self.sensor_manager)
        self.fuettern_seite = FuetternSeite()
        self.einstellungen_seite = EinstellungenSeite(sensor_manager=self.sensor_manager)

        # NEUE Seiten hinzufügen
        self.futter_konfiguration = FutterKonfiguration()
        self.fuetterung_abschluss = FuetterungAbschluss()

        # Navigation für alle Seiten setzen
        for seite in [self.start_screen, self.auswahl_seite, self.beladen_seite,
                      self.fuettern_seite, self.einstellungen_seite, self.futter_konfiguration, 
                      self.fuetterung_abschluss]:
            seite.navigation = self

        # Seiten zum Stack hinzufügen
        self.stacked_widget.addWidget(self.start_screen)
        self.stacked_widget.addWidget(self.auswahl_seite)
        self.stacked_widget.addWidget(self.beladen_seite)
        self.stacked_widget.addWidget(self.fuettern_seite)
        self.stacked_widget.addWidget(self.einstellungen_seite)
        self.stacked_widget.addWidget(self.futter_konfiguration)
        self.stacked_widget.addWidget(self.fuetterung_abschluss)

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
                
                # FUTTER-ANALYSEWERTE basierend auf Futtertyp setzen
                futtertyp = context.get('futtertyp', 'heu')
                aktuelles_pferd = self.get_aktuelles_pferd()
                
                if aktuelles_pferd:
                    self.fuettern_seite.zeige_pferd_daten(aktuelles_pferd)
                    
                    if futtertyp == 'heu' and self.heu_liste:
                        heu_daten = self.heu_liste[0]
                        self.fuettern_seite.zeige_futter_analysewerte(heu_daten, 4.5)
                        logger.info(f"Heu-Analysewerte angezeigt für: {heu_daten.name}")
                    elif futtertyp == 'heulage' and self.heulage_liste:
                        heulage_daten = self.heulage_liste[0]
                        self.fuettern_seite.zeige_futter_analysewerte(heulage_daten, 4.5)
                        logger.info(f"Heulage-Analysewerte angezeigt für: {heulage_daten.name}")
                    else:
                        logger.warning(f"Keine Futter-Daten für Typ: {futtertyp}")
        elif status == "einstellungen":
            self.stacked_widget.setCurrentWidget(self.einstellungen_seite)
            # Timer NACH der Navigation starten
            self.einstellungen_seite.start_timer()
        elif status == "futter_konfiguration":
            self.stacked_widget.setCurrentWidget(self.futter_konfiguration)
        elif status == "abschluss":
            self.stacked_widget.setCurrentWidget(self.fuetterung_abschluss)

    def stop_all_timers(self):
        """Stoppt alle Timer - verhindert Dauerschleifen"""
        if hasattr(self.beladen_seite, 'timer'):
            self.beladen_seite.timer.stop()
        if hasattr(self.einstellungen_seite, 'timer'):
            self.einstellungen_seite.timer.stop()

    # Einfache Navigation-Methoden (bleiben unverändert)
    # === NAVIGATION METHODEN ===
    def zeige_heu_futter(self):
        """Zeigt Heu-Fütterung mit echten Pferd- und Futter-Daten"""
        aktuelles_pferd = self.get_aktuelles_pferd()
        self.show_status("fuettern")

        # WICHTIG: Pferd-Daten explizit setzen
        if aktuelles_pferd:
            self.fuettern_seite.zeige_pferd_daten(aktuelles_pferd)
            
            # FUTTER-DATEN hinzufügen
            if self.heu_liste:
                heu_daten = self.heu_liste[0]  # Erstes Heu verwenden
                # Standard-Futtermenge: 4.5kg (entspricht Simulation)
                self.fuettern_seite.zeige_futter_analysewerte(heu_daten, 4.5)
                logger.info(f"Heu-Daten angezeigt: {heu_daten.name} für 4.5kg")
            else:
                logger.warning("Keine Heu-Daten verfügbar! Bitte Futter-Konfiguration laden.")
                
            self.fuettern_seite.start_timer()
            logger.info(f"Heu-Fütterung gestartet für: {aktuelles_pferd.name}")
        else:
            logger.warning("Kein Pferd verfügbar!")

    def zeige_heulage_futter(self):
        """Zeigt Heulage-Fütterung mit echten Pferd- und Futter-Daten"""
        aktuelles_pferd = self.get_aktuelles_pferd()
        self.show_status("fuettern")

        if aktuelles_pferd:
            self.fuettern_seite.zeige_pferd_daten(aktuelles_pferd)
            
            # HEULAGE-DATEN hinzufügen
            if self.heulage_liste:
                heulage_daten = self.heulage_liste[0]  # Erste Heulage verwenden
                # Standard-Futtermenge: 4.5kg (entspricht Simulation)
                self.fuettern_seite.zeige_futter_analysewerte(heulage_daten, 4.5)
                logger.info(f"Heulage-Daten angezeigt: {heulage_daten.name} für 4.5kg")
            else:
                logger.warning("Keine Heulage-Daten verfügbar! Bitte Futter-Konfiguration laden.")
                
            self.fuettern_seite.start_timer()
            logger.info(f"Heulage-Fütterung gestartet für: {aktuelles_pferd.name}")
        else:
            logger.warning("Kein Pferd verfügbar!")

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
    def lade_pferde_daten(self):
        """Lädt echte Pferde aus pferde.csv mit Box-System"""
        try:
            from utils.futter_loader import lade_pferde_als_dataclasses
            pferde = lade_pferde_als_dataclasses('pferde.csv')
            logger.info(f"{len(pferde)} Pferde aus CSV geladen")
            return pferde

        except FileNotFoundError:
            logger.error("Pferde-CSV nicht gefunden")
            from models.pferd import Pferd
            return [Pferd(name="Blitz", gewicht=500, alter=8, box=1)]
        except Exception as e:
            logger.error(f"Fehler beim Laden der Pferde-CSV: {e}")
            from models.pferd import Pferd
            return [Pferd(name="Blitz", gewicht=500, alter=8, box=1)]

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
            alter_index = self.aktueller_pferd_index
            self.aktueller_pferd_index = (self.aktueller_pferd_index + 1) % len(self.pferde_liste)
            
            # Prüfe ob wir am Ende angelangt sind (Rundlauf)
            if self.aktueller_pferd_index == 0 and alter_index > 0:
                # Fütterung beendet - zur Abschluss-Seite
                self.zeige_fuetterung_abschluss()
                return None
            
            aktuelles_pferd = self.get_aktuelles_pferd()
            if aktuelles_pferd:
                logger.info(f"Wechsel zu Box {aktuelles_pferd.box}: {aktuelles_pferd.name}")
                return aktuelles_pferd
        return None
        
    def zeige_fuetterung_abschluss(self):
        """Zeigt die Fütterung-Abschluss Seite"""
        fuetterung_daten = {
            'gefuetterte_pferde': len(self.pferde_liste),
            'menge_pro_pferd': 4.5,
            'futtertyp': getattr(self, 'aktueller_futtertyp', 'Heu eigen 2025'),
            'gesamte_boxen': 32
        }
        
        if hasattr(self, 'fuetterung_abschluss'):
            self.fuetterung_abschluss.zeige_zusammenfassung(fuetterung_daten)
            self.show_status("abschluss")
        else:
            logger.warning("Abschluss-Seite nicht initialisiert")
            # Fallback: Zurück zum Start
            self.show_status("start")
