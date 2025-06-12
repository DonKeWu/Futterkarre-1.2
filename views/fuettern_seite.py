# views/fuettern_seite.py - Erweiterte Gewichts-Simulation
import os
import logging
import views.icons.icons_rc
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer
import hardware.fu_sim as fu_sim

logger = logging.getLogger(__name__)


class FuetternSeite(QWidget):
    def __init__(self, pferd=None, parent=None):
        super().__init__(parent)
        self.navigation = None
        self.pferd = pferd

        # Gewichts-Variablen
        self.karre_gewicht = 0.0  # Aktuelles Karre-Gewicht
        self.entnommenes_gewicht = 0.0  # Letztes entnommenes Gewicht
        self.start_gewicht = 0.0  # Gewicht beim Beladen

        # Kontext-Variablen
        self.aktuelle_pferd_nummer = 1
        self.aktuelles_pferd = None
        self.letztes_gewicht = 0.0
        self.gewaehlter_futtertyp = "heu"

        # UI laden
        self.load_ui_or_fallback()
        self.connect_buttons()

        # Timer für Echtzeit-Updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_displays)

    def load_ui_or_fallback(self):
        """Lädt UI-Datei oder erstellt Fallback"""
        ui_path = os.path.join(os.path.dirname(__file__), "fuettern_seite.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
            logger.info("fuettern_seite.ui erfolgreich geladen")
        else:
            self.create_ui()

    def connect_buttons(self):
        """Verbindet alle Buttons"""
        # Fütterungs-Simulation Button
        if hasattr(self, 'btn_h_fu_sim'):
            self.btn_h_fu_sim.clicked.connect(self.simuliere_fuetterung)

        # Navigation Buttons
        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.zurueck_zur_auswahl)
        if hasattr(self, 'btn_settings'):
            self.btn_settings.clicked.connect(self.zu_einstellungen)
        if hasattr(self, 'btn_h_reload'):
            self.btn_h_reload.clicked.connect(self.nachladen_mit_kontext)
        if hasattr(self, 'btn_next_rgv'):
            self.btn_next_rgv.clicked.connect(self.naechstes_pferd)

    def create_ui(self):
        """Fallback UI wenn fuettern_seite.ui nicht existiert"""
        from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton
        layout = QVBoxLayout()

        # Wichtigste Labels erstellen
        self.label_rgv_name = QLabel("Kein Pferd gewählt")
        self.label_rgv_alter = QLabel("-- Jahre")
        self.label_rgv_gewicht = QLabel("-- kg")
        self.label_karre_gewicht_anzeigen = QLabel("0.00")
        self.label_h_gewichtanzeige = QLabel("0.00")

        # Buttons
        self.btn_h_fu_sim = QPushButton("Fütterung simulieren")
        self.btn_back = QPushButton("Zurück")

        layout.addWidget(self.label_rgv_name)
        layout.addWidget(self.label_karre_gewicht_anzeigen)
        layout.addWidget(self.btn_h_fu_sim)
        layout.addWidget(self.btn_back)

        self.setLayout(layout)

    def zeige_pferd_daten(self, pferd):
        """Zeigt echte Pferd-Daten aus Dataclass"""
        if not pferd:
            logger.warning("Kein Pferd-Objekt übergeben")
            return

        self.aktuelles_pferd = pferd

        try:
            # ECHTE Pferd-Daten anzeigen mit Null-Prüfung
            if hasattr(self, 'label_rgv_name') and hasattr(pferd, 'name'):
                self.label_rgv_name.setText(pferd.name)
            if hasattr(self, 'label_rgv_alter') and hasattr(pferd, 'alter'):
                self.label_rgv_alter.setText(f"{pferd.alter} Jahre")
            if hasattr(self, 'label_rgv_gewicht') and hasattr(pferd, 'gewicht'):
                self.label_rgv_gewicht.setText(f"{pferd.gewicht} kg")

            logger.info(f"Pferd-Daten angezeigt: {pferd.name}, {pferd.alter} Jahre, {pferd.gewicht} kg")

        except Exception as e:
            logger.error(f"Fehler beim Anzeigen der Pferd-Daten: {e}")

    def set_karre_gewicht(self, gewicht):
        """Setzt das Karre-Gewicht (von Beladen-Seite)"""
        self.karre_gewicht = gewicht
        self.start_gewicht = gewicht
        logger.info(f"Karre-Gewicht gesetzt: {gewicht:.2f} kg")
        self.update_gewichts_anzeigen()

    def simuliere_fuetterung(self):
        """Simuliert eine Fütterung - reduziert Karre-Gewicht"""
        if self.karre_gewicht <= 0:
            logger.warning("Karre ist leer - Nachladen erforderlich!")
            return

        # Fütterungsmenge simulieren (2-4 kg)
        import random
        fuetter_menge = random.uniform(2.0, 4.0)

        # Karre-Gewicht reduzieren
        if fuetter_menge > self.karre_gewicht:
            fuetter_menge = self.karre_gewicht  # Nicht mehr entnehmen als vorhanden

        self.karre_gewicht -= fuetter_menge
        self.entnommenes_gewicht = fuetter_menge

        logger.info(f"Fütterung simuliert: {fuetter_menge:.2f} kg entnommen, Karre-Rest: {self.karre_gewicht:.2f} kg")

        # Anzeigen aktualisieren
        self.update_gewichts_anzeigen()

        # Fütterungs-Simulation aktivieren
        fu_sim.setze_simulation(True)

    def update_gewichts_anzeigen(self):
        """Aktualisiert alle Gewichts-Anzeigen"""
        # Karre-Gewicht anzeigen
        if hasattr(self, 'label_karre_gewicht_anzeigen'):
            self.label_karre_gewicht_anzeigen.setText(f"{self.karre_gewicht:.2f}")

        # Entnommenes Gewicht anzeigen
        if hasattr(self, 'label_h_gewichtanzeige'):
            self.label_h_gewichtanzeige.setText(f"{self.entnommenes_gewicht:.2f}")

    def update_displays(self):
        """Echtzeit-Updates für alle Anzeigen"""
        try:
            # Gewichts-Anzeigen aktualisieren
            self.update_gewichts_anzeigen()

            # Zellen-Anzeigen (falls HX711 aktiv)
            if hasattr(self, 'navigation') and self.navigation:
                # Hier könnten Sie echte Sensor-Daten anzeigen
                pass

        except Exception as e:
            logger.error(f"Fehler beim Update der Anzeigen: {e}")

    def restore_context(self, context):
        """Stellt Kontext nach dem Beladen wieder her"""
        self.aktuelle_pferd_nummer = context.get('pferd_nummer', 1)
        self.aktuelles_pferd = context.get('pferd_objekt', None)
        futtertyp = context.get('futtertyp', 'heu')
        neues_gewicht = context.get('neues_gewicht', 0.0)

        # Titel aktualisieren
        self.update_titel(futtertyp)

        # Karre-Gewicht setzen
        if neues_gewicht > 0:
            self.set_karre_gewicht(neues_gewicht)

        # Pferd-Daten anzeigen
        if self.aktuelles_pferd:
            self.zeige_pferd_daten(self.aktuelles_pferd)

        logger.info(f"Kontext wiederhergestellt - Pferd {self.aktuelle_pferd_nummer}, Karre: {neues_gewicht:.2f} kg")

    def start_timer(self):
        """Startet Echtzeit-Updates"""
        self.timer.start(1000)  # Jede Sekunde

    def stop_timer(self):
        """Stoppt Echtzeit-Updates"""
        self.timer.stop()

    # Bestehende Methoden bleiben unverändert...
    def update_titel(self, futtertyp):
        if hasattr(self, 'b_heu_fuetterung'):
            if futtertyp == "heu":
                self.b_heu_fuetterung.setText("Heu Fütterung")
            elif futtertyp == "heulage":
                self.b_heu_fuetterung.setText("Heulage Fütterung")
            elif futtertyp == "pellets":
                self.b_heu_fuetterung.setText("Pellet Fütterung")
            elif futtertyp == "hafer":
                self.b_heu_fuetterung.setText("Hafer Fütterung")

    def nachladen_mit_kontext(self):
        context = {
            'pferd_nummer': self.aktuelle_pferd_nummer,
            'pferd_objekt': self.aktuelles_pferd,
            'restgewicht': self.karre_gewicht,  # Aktuelles Karre-Gewicht
            'futtertyp': self.gewaehlter_futtertyp,
            'von_seite': 'fuettern'
        }

        if self.navigation:
            self.navigation.show_status("beladen", context)

    def naechstes_pferd(self):
        """Wechselt zum nächsten Pferd"""
        if self.navigation:
            naechstes_pferd = self.navigation.naechstes_pferd()
            if naechstes_pferd:
                self.zeige_pferd_daten(naechstes_pferd)

    def zurueck_zur_auswahl(self):
        if self.navigation:
            self.navigation.go_back()

    def zu_einstellungen(self):
        if self.navigation:
            self.navigation.show_status("einstellungen")
