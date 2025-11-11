# views/beladen_seite.py - Mit WeightManager Integration
import os
import logging

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QButtonGroup
from PyQt5.QtCore import QTimer
from hardware.weight_manager import get_weight_manager

logger = logging.getLogger(__name__)


class BeladenSeite(QWidget):
    def __init__(self, sensor_manager):
        super().__init__()
        self.sensor_manager = sensor_manager
        self.navigation = None  # Wird von MainWindow gesetzt
        
        # WeightManager Integration
        self.weight_manager = get_weight_manager()
        self._weight_observer_registered = False
        
        # TimerManager Integration
        from utils.timer_manager import get_timer_manager
        self.timer_manager = get_timer_manager()
        self._timer_registered = False

        # Kontext-Variablen
        self.context = {}
        self.restgewicht = 0.0
        self.pferd_nummer = 1
        self.aktuelles_pferd = None
        self.gewaehlter_futtertyp = "heu"  # Standard
        self.zwischenstopp_modus = False   # HEU-Zwischenstopp Flag

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

        # Timer über TimerManager registrieren
        if not self._timer_registered:
            self.timer_manager.register_timer(
                "beladen_weight_update",
                "BeladenSeite", 
                500,  # 500ms
                self.update_weight
            )
            self._timer_registered = True
            logger.info("🎯 TimerManager Timer für BeladenSeite registriert")
            print(f"🎯 BeladenSeite: Timer registriert - ID: beladen_weight_update")

        # Legacy Timer erstellen (für Fallback)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_weight)

        # Button-Gruppe für HEU/HEULAGE einrichten
        self.setup_futter_buttons()

        # Andere Buttons verbinden
        self.connect_buttons()

    def setup_futter_buttons(self):
        """Richtet alle Futtertypen als Wechselschaltung ein"""
        # Standard-Futtertyp setzen
        self.gewaehlter_futtertyp = "heu"
        
        # Initiales Highlighting setzen
        self.update_futter_highlighting()

    def select_futter_type(self, futter_type):
        """Wählt Futtertyp und aktualisiert Button-Highlighting"""
        self.gewaehlter_futtertyp = futter_type
        logger.info(f"Futtertyp gewählt: {self.gewaehlter_futtertyp.upper()}")
        
        # Button-Highlighting aktualisieren
        self.update_futter_highlighting()
        
    def update_futter_highlighting(self):
        """Aktualisiert das Highlighting der Futter-Buttons"""
        # Hellblaues Highlighting für ausgewählten Button
        selected_style = """
            QPushButton {
                background-color: #87CEEB;
                color: #000000;
                border: 2px solid #4682B4;
                border-radius: 8px;
            }
        """
        
        # Standard-Style (vom Theme-Manager kontrolliert)
        default_style = ""
        
        # Alle Buttons zurücksetzen
        if hasattr(self, 'btn_heu'):
            self.btn_heu.setStyleSheet(default_style)
        if hasattr(self, 'btn_heulage'):
            self.btn_heulage.setStyleSheet(default_style)
            
        # Ausgewählten Button highlighten
        if self.gewaehlter_futtertyp == 'heu' and hasattr(self, 'btn_heu'):
            self.btn_heu.setStyleSheet(selected_style)
        elif self.gewaehlter_futtertyp == 'heulage' and hasattr(self, 'btn_heulage'):
            self.btn_heulage.setStyleSheet(selected_style)

    def futter_typ_gewaehlt(self, button_id):
        """Wird aufgerufen wenn ein Futtertyp gewählt wird (Legacy)"""
        futtertyp_mapping = {
            1: "heu",
            2: "heulage",
            3: "pellets",
            4: "hafer"
        }

        self.gewaehlter_futtertyp = futtertyp_mapping.get(button_id, "heu")
        logger.info(f"Futtertyp gewählt: {self.gewaehlter_futtertyp.upper()}")
        self.update_futter_highlighting()

    def connect_buttons(self):
        """Verbindet alle Buttons"""
        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.zurueck_geklickt)
            logger.info("Back-Button verbunden")

        # Futter-Auswahl Buttons mit Highlighting
        if hasattr(self, 'btn_heu'):
            self.btn_heu.clicked.connect(lambda: self.select_futter_type('heu'))
        if hasattr(self, 'btn_heulage'):
            self.btn_heulage.clicked.connect(lambda: self.select_futter_type('heulage'))

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
        """Legacy-Methode - jetzt über TimerManager"""
        # Timer wird automatisch über MainWindow.timer_manager.set_active_page() gestartet
        logger.debug("BeladenSeite: Timer über TimerManager aktiviert")

    def stop_timer(self):
        """Legacy-Methode - jetzt über TimerManager"""
        # Timer wird automatisch über TimerManager gestoppt
        logger.debug("BeladenSeite: Timer über TimerManager deaktiviert")

    def set_context(self, context):
        """Empfängt Kontext von der Füttern-Seite oder HEU-Zwischenstopp"""
        self.context = context
        self.restgewicht = context.get('restgewicht', 0.0)
        self.pferd_nummer = context.get('pferd_nummer', 1)
        self.aktuelles_pferd = context.get('pferd_objekt', None)

        # HEU-ZWISCHENSTOPP MODUS
        if context.get('zwischenstopp', False):
            self.zwischenstopp_modus = True
            futtertyp = context.get('futtertyp', 'heu')
            logger.info(f"HEU-Zwischenstopp Modus aktiviert - Futtertyp: {futtertyp}")
            
            # HEU automatisch vorwählen (falls UI-Element existiert)
            if hasattr(self, 'radio_heu') and futtertyp == 'heu':
                self.radio_heu.setChecked(True)
                logger.info("HEU automatisch vorgewählt")
        else:
            self.zwischenstopp_modus = False

        logger.info(
            f"Beladen-Seite: Kontext erhalten - Pferd {self.pferd_nummer}, Restgewicht: {self.restgewicht:.2f} kg")

    def beladen_fertig(self):
        """Navigation zurück zur Füttern-Seite"""
        if self.navigation:
            try:
                
                # Aktuelles Gewicht lesen (WeightManager - einheitlich)
                aktuelles_gewicht = self.weight_manager.read_weight(use_cache=False)

                # HEU-ZWISCHENSTOPP: Rückkehr zur Füttern-Seite
                if getattr(self, 'zwischenstopp_modus', False):
                    logger.info("HEU-Zwischenstopp beendet - Rückkehr zur Füttern-Seite")
                    
                    # HEU-Context für Füttern-Seite vorbereiten
                    original_futtertyp = self.context.get('original_futtertyp', 'heulage')  # Fallback
                    rueckkehr_context = {
                        'pferd_objekt': self.context.get('rueckkehr_pferd'),
                        'pferd_name': self.context.get('pferd_name', 'Unbekannt'),
                        'futtertyp': original_futtertyp,  # URSPRÜNGLICHEN Futtertyp verwenden!
                        'heu_gewicht': aktuelles_gewicht,
                        'zwischenstopp_beendet': True
                    }
                    
                    # STATISTIK: HEU-Zwischenstopp registrieren
                    if self.navigation and hasattr(self.navigation, 'registriere_fuetterung'):
                        self.navigation.registriere_fuetterung(self.gewaehlter_futtertyp, aktuelles_gewicht)
                    
                    logger.info(f"Rückkehr zu Pferd: {rueckkehr_context['pferd_name']} mit {aktuelles_gewicht:.2f}kg {self.gewaehlter_futtertyp.upper()}")
                    
                    # Direkt zurück zur Füttern-Seite
                    self.navigation.show_status("fuettern", rueckkehr_context)
                    return

                # HARDWARE: Additive Beladung
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
        """Aktualisiert Gewichtsanzeige mit WeightManager"""
        try:
            # WeightManager für Gewichtsquelle
            aktuelles_gewicht = self.weight_manager.read_weight()
            print(f"🔄 UPDATE_WEIGHT AUFGERUFEN: {aktuelles_gewicht:.2f} kg")

            # Hauptgewichtsanzeige aktualisieren
            if hasattr(self, 'label_karre_gewicht'):
                old_text = self.label_karre_gewicht.text()
                self.label_karre_gewicht.setText(f"{aktuelles_gewicht:.2f}")
                print(f"📝 LABEL UPDATE: {old_text} -> {aktuelles_gewicht:.2f}")
                
                # Force UI refresh
                self.label_karre_gewicht.update()
                self.label_karre_gewicht.repaint()
                print(f"🖼️ UI REFRESH erzwungen")
            else:
                print("❌ FEHLER: label_karre_gewicht nicht gefunden!")
                # Debug: Alle verfügbaren Attribute anzeigen
                print(f"📋 Verfügbare Label-Attribute: {[attr for attr in dir(self) if 'label' in attr.lower()]}")

        except Exception as e:
            logger.error(f"Fehler beim Wiegen: {e}")
            print(f"💥 FEHLER in update_weight: {e}")
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

    def test_hardware(self):
        """Test-Methode für Hardware-Sensoren"""
        print("Hardware-Test gestartet...")

        for i in range(5):
            gewicht = self.weight_manager.read_weight()
            print(f"Test {i + 1}: {gewicht:.2f} kg")

            if hasattr(self, 'label_karre_gewicht'):
                self.label_karre_gewicht.setText(f"{gewicht:.2f}")