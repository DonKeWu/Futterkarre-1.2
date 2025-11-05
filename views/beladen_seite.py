# views/beladen_seite.py
import os
import logging

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QButtonGroup
from PyQt5.QtCore import QTimer

logger = logging.getLogger(__name__)


class BeladenSeite(QWidget):
    def __init__(self, sensor_manager):
        super().__init__()
        self.sensor_manager = sensor_manager
        self.navigation = None  # Wird von MainWindow gesetzt

        # Kontext-Variablen
        self.context = {}
        self.restgewicht = 0.0
        self.pferd_nummer = 1
        self.aktuelles_pferd = None
        self.gewaehlter_futtertyp = "heu"  # Standard

        # UI laden
        ui_path = os.path.join(os.path.dirname(__file__), "beladen_seite.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
            logger.info("beladen_seite.ui erfolgreich geladen")
        else:
            logger.warning("beladen_seite.ui nicht gefunden - verwende Fallback")
            self.create_ui_in_code()

        # Vollbild für PiTouch2 (1280x720) - komplette Display-Nutzung
        self.setFixedSize(1280, 720)
        
        # Position: oben links (0,0) - Display vollständig nutzen
        self.move(0, 0)

        # Timer erstellen
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_weight)

        # Button-Gruppe für HEU/HEULAGE einrichten
        self.setup_futter_buttons()

        # Andere Buttons verbinden
        self.connect_buttons()

    def setup_futter_buttons(self):
        """Richtet alle Futtertypen als Wechselschaltung ein"""
        futter_buttons = []

        # Alle verfügbaren Futter-Buttons sammeln
        if hasattr(self, 'btn_heu_laden'):
            futter_buttons.append((self.btn_heu_laden, 1, "heu"))
        if hasattr(self, 'btn_heulage_laden'):
            futter_buttons.append((self.btn_heulage_laden, 2, "heulage"))
        if hasattr(self, 'btn_pellets_laden'):
            futter_buttons.append((self.btn_pellets_laden, 3, "pellets"))
        if hasattr(self, 'btn_hafer_laden'):
            futter_buttons.append((self.btn_hafer_laden, 4, "hafer"))

        if futter_buttons:
            # Button-Gruppe erstellen
            self.futter_group = QButtonGroup(self)
            self.futter_group.setExclusive(True)

            # Alle Buttons zur Gruppe hinzufügen
            for button, button_id, futtertyp in futter_buttons:
                button.setCheckable(True)
                self.futter_group.addButton(button, button_id)

            # Standard: Erster Button ausgewählt
            futter_buttons[0][0].setChecked(True)
            self.gewaehlter_futtertyp = futter_buttons[0][2]

            # Signal verbinden
            self.futter_group.buttonClicked[int].connect(self.futter_typ_gewaehlt)

            logger.info(f"Futter-Button-Gruppe eingerichtet mit {len(futter_buttons)} Optionen")

    def futter_typ_gewaehlt(self, button_id):
        """Wird aufgerufen wenn ein Futtertyp gewählt wird"""
        futtertyp_mapping = {
            1: "heu",
            2: "heulage",
            3: "pellets",
            4: "hafer"
        }

        self.gewaehlter_futtertyp = futtertyp_mapping.get(button_id, "heu")
        logger.info(f"Futtertyp gewählt: {self.gewaehlter_futtertyp.upper()}")

    def connect_buttons(self):
        """Verbindet alle Buttons"""
        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.zurueck_geklickt)
            logger.info("Back-Button verbunden")

        # Andere Buttons...
        if hasattr(self, 'btn_settings'):
            self.btn_settings.clicked.connect(self.zu_einstellungen)
        if hasattr(self, 'btn_wa_nullen'):
            self.btn_wa_nullen.clicked.connect(self.waage_nullen)
        if hasattr(self, 'btn_w_bestaetigen'):
            self.btn_w_bestaetigen.clicked.connect(self.beladen_fertig)

    def zurueck_geklickt(self):
        """Back-Button - einfach und robust"""
        if self.navigation:
            logger.info("Back-Button geklickt")
            self.navigation.go_back()
        else:
            logger.warning("Navigation nicht verfügbar")

    def zu_einstellungen(self):
        """Zu Einstellungen"""
        if self.navigation:
            self.navigation.show_status("einstellungen")

    def waage_nullen(self):
        """Waage nullen (Tara)"""
        try:
            logger.info("Waage wird genullt (Tara)")
            # Hier würden Sie die echte Tara-Funktion aufrufen
        except Exception as e:
            logger.error(f"Fehler beim Nullen der Waage: {e}")

    def start_timer(self):
        """Startet Timer nur wenn Seite aktiv ist"""
        self.timer.start(500)

    def stop_timer(self):
        """Stoppt Timer"""
        self.timer.stop()

    def set_context(self, context):
        """Empfängt Kontext von der Füttern-Seite"""
        self.context = context
        self.restgewicht = context.get('restgewicht', 0.0)
        self.pferd_nummer = context.get('pferd_nummer', 1)
        self.aktuelles_pferd = context.get('pferd_objekt', None)

        logger.info(
            f"Beladen-Seite: Kontext erhalten - Pferd {self.pferd_nummer}, Restgewicht: {self.restgewicht:.2f} kg")

    def beladen_fertig(self):
        """Navigation zurück zur Füttern-Seite mit Simulation-Support"""
        if self.navigation:
            try:
                # Import hier um Zirkular-Import zu vermeiden
                import hardware.hx711_sim as hx711_sim
                
                # Simulation: Karre automatisch auf 35kg beladen
                if hx711_sim.ist_simulation_aktiv():
                    hx711_sim.karre_beladen()  # Automatisch auf 35kg
                    logger.info("Simulation: Karre automatisch auf 35kg beladen")
                
                # Aktuelles Gewicht lesen (Simulation oder Hardware)
                aktuelles_gewicht = self.sensor_manager.read_weight()

                # Für Simulation: Immer Neubeladung (35kg)
                # Für Hardware: Additive Beladung wie bisher
                if hx711_sim.ist_simulation_aktiv():
                    gesamtgewicht = aktuelles_gewicht  # Simulation: direkter Wert
                    nachgeladen = aktuelles_gewicht
                    logger.info(f"Simulation: Beladen auf {gesamtgewicht:.2f} kg")
                else:
                    # HARDWARE: Additive Beladung wie bisher
                    if self.restgewicht > 0:
                        gesamtgewicht = self.restgewicht + aktuelles_gewicht
                        nachgeladen = aktuelles_gewicht
                        logger.info(f"Hardware: Nachladen {self.restgewicht:.2f} + {aktuelles_gewicht:.2f} = {gesamtgewicht:.2f} kg")
                    else:
                        gesamtgewicht = aktuelles_gewicht
                        nachgeladen = aktuelles_gewicht
                        logger.info(f"Hardware: Erstmaliges Beladen {gesamtgewicht:.2f} kg")

                self.context['neues_gewicht'] = gesamtgewicht
                self.context['nachgeladen'] = nachgeladen
                self.context['futtertyp'] = self.gewaehlter_futtertyp

                logger.info(f"Beladen abgeschlossen: Gesamt {gesamtgewicht:.2f} kg")
                self.navigation.show_status("fuettern", self.context)

            except Exception as e:
                logger.error(f"Fehler beim Lesen des Gewichts: {e}")
                self.navigation.show_status("fuettern", self.context)

    def update_weight(self):
        """Aktualisiert Gewichtsanzeige mit Debug-Ausgabe"""
        try:
            # Debug: Simulation-Status prüfen
            import hardware.hx711_sim as hx711_sim
            print(f"HX711-Simulation aktiv: {hx711_sim.ist_simulation_aktiv()}")

            aktuelles_gewicht = self.sensor_manager.read_weight()
            print(f"Gewicht gelesen: {aktuelles_gewicht:.2f} kg")

            # Hauptgewichtsanzeige aktualisieren
            if hasattr(self, 'label_karre_gewicht'):
                self.label_karre_gewicht.setText(f"{aktuelles_gewicht:.2f}")
                print(f"Label aktualisiert: {aktuelles_gewicht:.2f}")
            else:
                print("FEHLER: label_karre_gewicht nicht gefunden!")

        except Exception as e:
            logger.error(f"Fehler beim Wiegen: {e}")
            print(f"FEHLER in update_weight: {e}")
            if hasattr(self, 'label_karre_gewicht'):
                self.label_karre_gewicht.setText("Error")

    def create_ui_in_code(self):
        """Fallback UI wenn beladen_seite.ui nicht existiert"""
        layout = QVBoxLayout()

        # Futter-Buttons
        self.btn_heu_laden = QPushButton("HEU")
        self.btn_heulage_laden = QPushButton("HEULAGE")

        # Gewichts-Label
        self.label_karre_gewicht = QLabel("0.00")
        self.label_karre_gewicht.setStyleSheet("font-size: 48px; font-weight: bold;")

        # Funktions-Buttons
        self.btn_wa_nullen = QPushButton("Waage Nullen")
        self.btn_w_bestaetigen = QPushButton("Beladung bestätigen")
        self.btn_back = QPushButton("Zurück")

        # Layout zusammenbauen
        layout.addWidget(self.btn_heu_laden)
        layout.addWidget(self.btn_heulage_laden)
        layout.addWidget(self.label_karre_gewicht)
        layout.addWidget(self.btn_wa_nullen)
        layout.addWidget(self.btn_w_bestaetigen)
        layout.addWidget(self.btn_back)

        self.setLayout(layout)

    def test_simulation(self):
        """Test-Methode für HX711-Simulation"""
        import hardware.hx711_sim as hx711_sim

        print(f"Simulation aktiv: {hx711_sim.ist_simulation_aktiv()}")

        for i in range(5):
            gewicht = self.sensor_manager.read_weight()
            print(f"Test {i + 1}: {gewicht:.2f} kg")

            if hasattr(self, 'label_karre_gewicht'):
                self.label_karre_gewicht.setText(f"{gewicht:.2f}")

    # simuliere_fuetterung entfernt - nicht mehr nötig mit vereinfachter Simulation