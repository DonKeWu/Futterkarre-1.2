# views/main_window.py - Mit erweiterten Manager-Integrationen
import logging
logger = logging.getLogger(__name__)
import views.icons.icons_rc
from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore
from utils.timer_manager import get_timer_manager
from utils.settings_manager import get_settings_manager
from utils.database_manager import get_database_manager, FeedingRecord
from datetime import datetime

from views.start import StartSeite
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
        
        # Manager-Instanzen
        self.timer_manager = get_timer_manager()
        self.settings_manager = get_settings_manager()
        self.database_manager = get_database_manager()

        self.pferde_liste = []
        self.aktueller_pferd_index = 0
        self.pferde_liste = self.lade_pferde_daten()

        # Navigation - Smart Stack System
        self.previous_page = "auswahl"
        self.previous_context = {}
        self.current_status = "start"
        self.current_context = {}
        
        # Smart Navigation: Hauptseiten vs. Unterseiten
        self.main_pages = {"auswahl", "fuettern", "einstellungen", "beladen", "start"}
        self.sub_pages = {"futter_konfiguration", "abschluss"}
        self.main_page_stack = []  # Stack der Hauptseiten
        self.current_main_page = None

        # Futter-Listen initialisieren
        self.heu_liste = []
        self.heulage_liste = []
        self.pellet_liste = []
        
        # SEPARATE STATISTIKEN für Heu und Heulage
        self.heu_gesamt_kg = 0.0      # Gesamtmenge Heu gefüttert
        self.heulage_gesamt_kg = 0.0  # Gesamtmenge Heulage gefüttert
        self.heu_pferde_anzahl = 0    # Anzahl Pferde mit Heu gefüttert
        self.heulage_pferde_anzahl = 0 # Anzahl Pferde mit Heulage gefüttert
        
        # Standard-Futter-Daten laden
        self.lade_standard_futter_daten()

        logger.info("MainWindow wird initialisiert mit erweiterten Managern")
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
        # Fullscreen wird in main.py mit showFullScreen() aktiviert
        
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

        # Seiten-Mapping für Navigation
        self.page_widgets = {
            "start": self.start_screen,
            "auswahl": self.auswahl_seite,
            "beladen": self.beladen_seite,
            "fuettern": self.fuettern_seite,
            "einstellungen": self.einstellungen_seite,
            "futter_konfiguration": self.futter_konfiguration,
            "abschluss": self.fuetterung_abschluss
        }

        # Signal-Verbindungen für erweiterte Funktionen
        self.setup_signal_connections()

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

    def setup_signal_connections(self):
        """Setup für erweiterte Signal-Verbindungen"""
        try:
            # FutterKonfiguration Signale
            self.futter_konfiguration.futter_daten_gewaehlt.connect(self.on_futter_daten_gewaehlt)
            
            # EinstellungenSeite Signale
            self.einstellungen_seite.calibration_requested.connect(self.on_calibration_requested)
            
            logger.info("Signal-Verbindungen erfolgreich eingerichtet")
            
        except Exception as e:
            logger.error(f"Fehler bei Signal-Setup: {e}")

    def on_futter_daten_gewaehlt(self, datei_name: str, futter_daten: dict):
        """Callback für gewählte Futter-Daten"""
        try:
            logger.info(f"Futter-Daten gewählt: {datei_name} mit {len(futter_daten)} Einträgen")
            
            # Hier könnte eine spezifische Verarbeitung erfolgen
            # basierend auf dem Datei-Typ (Heu, Heulage, etc.)
            
            # Datenbank-Event loggen
            self.database_manager.log_system_event(
                "futter_selection",
                f"Futter-Daten gewählt: {datei_name}",
                {
                    "file_name": datei_name,
                    "entry_count": len(futter_daten),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Fehler bei Futter-Daten Verarbeitung: {e}")

    def on_calibration_requested(self):
        """Callback für Kalibrierungs-Anfrage"""
        try:
            logger.info("Kalibrierung angefordert")
            
            # Hier würde der Kalibrierungs-Prozess gestartet
            # Vorerst nur Event loggen
            self.database_manager.log_system_event(
                "calibration_requested",
                "Kalibrierung über UI angefordert",
                {"timestamp": datetime.now().isoformat()}
            )
            
        except Exception as e:
            logger.error(f"Fehler bei Kalibrierungs-Anfrage: {e}")

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

    def show_status(self, page, context=None):
        """Zentrale Navigation mit Smart Stack System"""
        logger.info(f"Navigation: {page} mit Kontext: {context}")

        # Timer der vorherigen Seite über TimerManager stoppen
        self.timer_manager.stop_all_timers()

        # Smart Navigation: Hauptseiten vs. Unterseiten verwalten
        if page != "back" and self.current_status != page:
            # Wenn wir zu einer Hauptseite wechseln
            if page in self.main_pages:
                # Aktuelle Hauptseite auf Stack legen (falls sie existiert)
                if self.current_main_page and self.current_main_page != page:
                    if self.current_main_page not in self.main_page_stack:
                        self.main_page_stack.append(self.current_main_page)
                        logger.info(f"Hauptseite auf Stack: {self.current_main_page}")
                
                self.current_main_page = page
                self.previous_page = self.current_status
                self.previous_context = self.current_context.copy() if self.current_context else {}
                
            # Wenn wir zu einer Unterseite wechseln
            elif page in self.sub_pages:
                # Hauptseite bleibt gleich, nur vorherige Seite merken
                self.previous_page = self.current_status
                self.previous_context = self.current_context.copy() if self.current_context else {}
                logger.info(f"Unterseite {page}, Hauptseite bleibt: {self.current_main_page}")

        # Seite tatsächlich wechseln
        if page in self.page_widgets:
            self.stacked_widget.setCurrentWidget(self.page_widgets[page])
            self.current_status = page
            self.current_context = context or {}
            
            # Timer für aktuelle Seite aktivieren UND Kontext übertragen
            if page == "beladen":
                self.timer_manager.set_active_page("BeladenSeite")
                # BeladenSeite: Kontext setzen (falls vorhanden)
                if context and hasattr(self.page_widgets[page], 'set_context'):
                    self.page_widgets[page].set_context(context)
                logger.info("Timer für BeladenSeite aktiviert")
            elif page == "fuettern":
                self.timer_manager.set_active_page("FuetternSeite")
                # FütternSeite: Kontext wiederherstellen (WICHTIG für Beladungswerte!)
                if context and hasattr(self.page_widgets[page], 'restore_context'):
                    self.page_widgets[page].restore_context(context)
                    logger.info(f"FütternSeite: Kontext wiederhergestellt - {context.get('neues_gewicht', 0):.2f}kg")
                logger.info("Timer für FuetternSeite aktiviert")
            # Andere Seiten haben keine Timer
            
            logger.info(f"Seite gewechselt zu: {page}")
        else:
            logger.error(f"Unbekannte Seite: {page}")

    # Legacy-Methode entfernt - TimerManager übernimmt Timer-Verwaltung
    # stop_all_timers() -> self.timer_manager.stop_all_timers()

    # Einfache Navigation-Methoden (bleiben unverändert)
    # === NAVIGATION METHODEN ===
    def zeige_heu_futter(self):
        """Zeigt Heu-Fütterung mit echten Pferd- und Futter-Daten"""
        # STATISTIK: Bei erster Pferd-Fütterung zurücksetzen
        if self.aktueller_pferd_index == 0:
            self.reset_statistiken()
            
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
                
            # Navigation zu Füttern-Seite über TimerManager
            self.timer_manager.set_active_page("FuetternSeite")
            logger.info(f"Heu-Fütterung gestartet für: {aktuelles_pferd.name}")
        else:
            logger.warning("Kein Pferd verfügbar!")

    def zeige_heulage_futter(self):
        """Zeigt Heulage-Fütterung mit echten Pferd- und Futter-Daten"""
        # STATISTIK: Bei erster Pferd-Fütterung zurücksetzen
        if self.aktueller_pferd_index == 0:
            self.reset_statistiken()
            
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
                
            # Navigation zu Füttern-Seite über TimerManager
            self.timer_manager.set_active_page("FuetternSeite")
            logger.info(f"Heulage-Fütterung gestartet für: {aktuelles_pferd.name}")
        else:
            logger.warning("Kein Pferd verfügbar!")

    def zeige_futter_laden(self):
        self.show_status("beladen")

    def zeige_einstellungen(self):
        self.show_status("einstellungen")

    def go_back(self):
        """Smart Back-Button - intelligente Hauptseiten-Navigation"""
        logger.info(f"Smart Back: Aktuell={self.current_status}, Hauptseite={self.current_main_page}")
        logger.info(f"Stack: {self.main_page_stack}, Previous: {self.previous_page}")
        
        # Fall 1: Von Unterseite zurück zur aktuellen Hauptseite
        if self.current_status in self.sub_pages and self.current_main_page:
            logger.info(f"Unterseite → Hauptseite: {self.current_status} → {self.current_main_page}")
            self.show_status(self.current_main_page)
            return
        
        # Fall 2: Von Hauptseite zu vorheriger Hauptseite (vom Stack)
        if self.current_status in self.main_pages and self.main_page_stack:
            previous_main = self.main_page_stack.pop()
            logger.info(f"Hauptseite → vorherige Hauptseite: {self.current_status} → {previous_main}")
            self.show_status(previous_main)
            return
        
        # Fall 3: Standard-Rücksprung (wie bisher)
        if self.previous_page and self.previous_page != self.current_status:
            logger.info(f"Standard-Rücksprung: {self.current_status} → {self.previous_page}")
            self.show_status(self.previous_page, self.previous_context)
            return
        
        # Fall 4: Fallback zur Auswahl
        logger.warning(f"Fallback zur Auswahl - keine gültige Rücksprung-Option")
        self.show_status("auswahl")

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
        
    def registriere_fuetterung(self, futtertyp, menge_kg):
        """Registriert eine Fütterung für separate Statistiken UND Datenbank"""
        aktuelles_pferd = self.get_aktuelles_pferd()
        
        # Lokale Statistiken (bestehend)
        if futtertyp.lower() in ['heu', 'heu_eigen', 'heu_frd']:
            self.heu_gesamt_kg += menge_kg
            self.heu_pferde_anzahl += 1
            logger.info(f"Heu-Fütterung registriert: +{menge_kg:.1f}kg (Gesamt: {self.heu_gesamt_kg:.1f}kg, {self.heu_pferde_anzahl} Pferde)")
        elif futtertyp.lower() in ['heulage', 'heulage_eigen']:
            self.heulage_gesamt_kg += menge_kg
            self.heulage_pferde_anzahl += 1
            logger.info(f"Heulage-Fütterung registriert: +{menge_kg:.1f}kg (Gesamt: {self.heulage_gesamt_kg:.1f}kg, {self.heulage_pferde_anzahl} Pferde)")
        
        # Datenbank-Integration (NEU)
        try:
            if aktuelles_pferd:
                # Gewichtswerte von Sensor Manager holen
                from hardware.weight_manager import get_weight_manager
                weight_manager = get_weight_manager()
                
                current_weight = weight_manager.read_weight()
                last_weight = getattr(self, '_last_recorded_weight', current_weight)
                
                # FeedingRecord erstellen
                feeding_record = FeedingRecord(
                    timestamp=datetime.now().isoformat(),
                    horse_name=aktuelles_pferd.name,
                    feed_type=futtertyp,
                    planned_amount=menge_kg,  # Geplante Menge
                    actual_amount=menge_kg,   # Tatsächliche Menge (hier gleich)
                    duration_seconds=getattr(self, '_feeding_duration', 120),  # Default 2 min
                    notes=f"Box {aktuelles_pferd.box}",
                    load_weight_before=last_weight,
                    load_weight_after=current_weight
                )
                
                # In Datenbank speichern
                record_id = self.database_manager.add_feeding_record(feeding_record)
                if record_id > 0:
                    logger.info(f"Fütterung in Datenbank gespeichert: ID {record_id}")
                else:
                    logger.error("Fehler beim Speichern in Datenbank")
                
                # Aktuelles Gewicht für nächste Fütterung merken
                self._last_recorded_weight = current_weight
                
        except Exception as e:
            logger.error(f"Fehler bei Datenbank-Integration: {e}")
            # Fütterung trotzdem erfolgreich (lokale Statistiken funktionieren)
        else:
            logger.warning(f"Unbekannter Futtertyp für Statistik: {futtertyp}")
    
    def reset_statistiken(self):
        """Setzt alle Fütterungsstatistiken zurück"""
        self.heu_gesamt_kg = 0.0
        self.heulage_gesamt_kg = 0.0
        self.heu_pferde_anzahl = 0
        self.heulage_pferde_anzahl = 0
        logger.info("Fütterungsstatistiken zurückgesetzt")
        
    def zeige_fuetterung_abschluss(self):
        """Zeigt die Fütterung-Abschluss Seite mit separaten Heu/Heulage Statistiken"""
        # NEUE: Separate Statistiken für Heu und Heulage
        gesamtmenge_kg = self.heu_gesamt_kg + self.heulage_gesamt_kg
        gefuetterte_pferde_gesamt = self.heu_pferde_anzahl + self.heulage_pferde_anzahl
        
        fuetterung_daten = {
            'gefuetterte_pferde': gefuetterte_pferde_gesamt,
            'menge_pro_pferd': 4.5,  # Durchschnitt
            'futtertyp': f"Heu: {self.heu_gesamt_kg:.1f}kg ({self.heu_pferde_anzahl}P) | Heulage: {self.heulage_gesamt_kg:.1f}kg ({self.heulage_pferde_anzahl}P)",
            'gesamte_boxen': 32,
            # ERWEITERTE Statistiken
            'heu_gesamt': self.heu_gesamt_kg,
            'heulage_gesamt': self.heulage_gesamt_kg,
            'heu_pferde': self.heu_pferde_anzahl,
            'heulage_pferde': self.heulage_pferde_anzahl,
            'gesamtmenge': gesamtmenge_kg
        }
        
        logger.info(f"Fütterung abgeschlossen - Heu: {self.heu_gesamt_kg:.1f}kg ({self.heu_pferde_anzahl}P), Heulage: {self.heulage_gesamt_kg:.1f}kg ({self.heulage_pferde_anzahl}P)")
        
        if hasattr(self, 'fuetterung_abschluss'):
            self.fuetterung_abschluss.zeige_zusammenfassung(fuetterung_daten)
            self.show_status("abschluss")
        else:
            logger.warning("Abschluss-Seite nicht initialisiert")
            # Fallback: Zurück zum Start
            self.show_status("start")
