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
        """Navigation zurück zur Füttern-Seite mit Simulation-Support und HEU-Zwischenstopp"""
        if self.navigation:
            try:
                # Import hier um Zirkular-Import zu vermeiden
                import hardware.hx711_sim as hx711_sim
                
                # Simulation: Karre automatisch beladen über WeightManager
                if self.weight_manager.get_status()['is_simulation']:
                    self.weight_manager.simulate_weight_change(35.0)  # 35kg hinzufügen
                    logger.info("WeightManager: Karre automatisch beladen")
                
                # Aktuelles Gewicht lesen (WeightManager - einheitlich)
                aktuelles_gewicht = self.weight_manager.read_weight(use_cache=False)

                # HEU-ZWISCHENSTOPP: Rückkehr zur Füttern-Seite
                if getattr(self, 'zwischenstopp_modus', False):
                    logger.info("HEU-Zwischenstopp beendet - Rückkehr zur Füttern-Seite")
                    
                    # HEU-Context für Füttern-Seite vorbereiten
                    rueckkehr_context = {
                        'pferd_objekt': self.context.get('rueckkehr_pferd'),
                        'pferd_name': self.context.get('pferd_name', 'Unbekannt'),
                        'futtertyp': self.gewaehlter_futtertyp,  # Dynamisch: heu oder heulage
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

                # NORMALER MODUS: Wie bisher
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
        """Aktualisiert Gewichtsanzeige mit WeightManager - Enhanced Debugging"""
        try:
            # SIMULATION HACK: Simuliere "Material-auf-Waage" für Live-Demo  
            import hardware.hx711_sim as hx711_sim
            if self.weight_manager.get_status()['is_simulation']:
                # Simuliere dass Material auf die Waage gelegt wird (für BeladenSeite)
                workflow_sim = hx711_sim.get_workflow_simulation()
                if not workflow_sim.ist_beladen:
                    # Simuliere dass 15-25kg Material bereits auf der Waage liegen
                    import random
                    basis_gewicht = random.uniform(15.0, 25.0)
                    workflow_sim.karre_gewicht = basis_gewicht
                    workflow_sim.ist_beladen = True
                    print(f"🎯 SIMULATION: Basis-Material simuliert: {basis_gewicht:.1f}kg")

            # WeightManager für einheitliche Gewichtsquelle
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

    def test_simulation(self):
        """Test-Methode für HX711-Simulation"""
        import hardware.hx711_sim as hx711_sim

        print(f"Simulation aktiv: {hx711_sim.ist_simulation_aktiv()}")

        for i in range(5):
            gewicht = self.weight_manager.read_weight()
            print(f"Test {i + 1}: {gewicht:.2f} kg")

            if hasattr(self, 'label_karre_gewicht'):
                self.label_karre_gewicht.setText(f"{gewicht:.2f}")

    # simuliere_fuetterung entfernt - nicht mehr nötig mit vereinfachter Simulation