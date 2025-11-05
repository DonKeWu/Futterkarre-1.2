# views/fuettern_seite.py - Vereinfachte Version ohne separate Simulation
import os
import logging
import views.icons.icons_rc
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer
import hardware.hx711_sim as hx711_sim

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
        
        # Futter-Daten Variablen (HINZUGEFÜGT)
        self.aktuelle_futter_daten = None

        # UI laden
        self.load_ui_or_fallback()
        
        # Feste Fenstergröße für PiTouch2 (1280x720, minus 60px Statusleiste)
        self.setFixedSize(1280, 660)
        
        # Position: unter der Raspberry Pi Statusleiste (60px Abstand von oben)
        self.move(0, 60)
        
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
        # Navigation Buttons (Fütterungs-Simulation entfernt)
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
        self.label_fu_entnommen = QLabel("0.00")

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
            # ECHTE Pferd-Daten anzeigen - Box-Nummer getrennt vom Namen
            if hasattr(self, 'label_box') and hasattr(pferd, 'box'):
                # Box-Nummer in separates Label
                self.label_box.setText(f"Box {pferd.box}")
                
            if hasattr(self, 'label_rgv_name') and hasattr(pferd, 'name'):
                # Nur noch der Name ohne Box-Nummer
                self.label_rgv_name.setText(pferd.name)
                
            if hasattr(self, 'label_rgv_alter') and hasattr(pferd, 'alter'):
                self.label_rgv_alter.setText(f"{pferd.alter} Jahre")
            if hasattr(self, 'label_rgv_gewicht') and hasattr(pferd, 'gewicht'):
                self.label_rgv_gewicht.setText(f"{pferd.gewicht} kg")

            logger.info(f"Pferd-Daten angezeigt: Box {getattr(pferd, 'box', '?')} - {pferd.name}, {pferd.alter} Jahre, {pferd.gewicht} kg")

        except Exception as e:
            logger.error(f"Fehler beim Anzeigen der Pferd-Daten: {e}")

    def zeige_futter_analysewerte(self, futter_daten, gefuetterte_menge_kg=5.0):
        """Zeigt Futter-Analysewerte als absolute Mengen basierend auf gefütterter Menge"""
        if not futter_daten:
            logger.warning("Keine Futter-Daten übergeben")
            return
            
        self.aktuelle_futter_daten = futter_daten
        
        try:
            # ABSOLUTE MENGEN berechnen (Prozent * gefütterte Menge)
            trockensubstanz_g = (futter_daten.trockenmasse / 100.0) * gefuetterte_menge_kg * 1000
            rohprotein_g = (futter_daten.rohprotein / 100.0) * gefuetterte_menge_kg * 1000
            rohfaser_g = (futter_daten.rohfaser / 100.0) * gefuetterte_menge_kg * 1000
            gesamtzucker_g = (futter_daten.gesamtzucker / 100.0) * gefuetterte_menge_kg * 1000
            fruktan_g = (futter_daten.fruktan / 100.0) * gefuetterte_menge_kg * 1000
            me_pferd_total = (futter_daten.me_pferd / 100.0) * gefuetterte_menge_kg * 100  # MJ
            pcv_xp_g = (futter_daten.pcv_xp / 100.0) * gefuetterte_menge_kg * 1000
            feuchte_g = ((100.0 - futter_daten.trockenmasse) / 100.0) * gefuetterte_menge_kg * 1000
            
            # ERNÄHRUNGSPHYSIOLOGISCHE Kontrolle (nur die 3 wichtigsten Werte)
            pferd_gewicht = getattr(self.aktuelles_pferd, 'gewicht', 500) if hasattr(self, 'aktuelles_pferd') else 500
            self.update_naehrwert_labels_mit_kontrolle(rohprotein_g, rohfaser_g, fruktan_g, pferd_gewicht)
                
            logger.info(f"Futter-Analysewerte für {gefuetterte_menge_kg:.1f}kg {futter_daten.name} berechnet")
            logger.info(f"Beispiel: Rohprotein {rohprotein_g:.0f}g ({futter_daten.rohprotein:.1f}% von {gefuetterte_menge_kg:.1f}kg)")
            
        except Exception as e:
            logger.error(f"Fehler beim Berechnen der Futter-Analysewerte: {e}")
            
    def update_naehrwert_labels_mit_kontrolle(self, rohprotein_g, rohfaser_g, fruktan_g, pferd_gewicht_kg):
        """Aktualisiert Nährwert-Labels mit ernährungsphysiologischer Farbkontrolle (reduziert auf 3 Werte)"""
        
        # ERNÄHRUNGSPHYSIOLOGISCHE RICHTWERTE pro 100kg Körpergewicht/Tag
        # Reduziert auf die 3 wichtigsten Werte: Rohprotein, Rohfaser, Fruktan
        richtwerte_pro_100kg = {
            'rohfaser_min': 1000,    # 1.0kg Rohfaser (Mindestbedarf)
            'rohfaser_max': 1500,    # 1.5kg Rohfaser (Obergrenze)
            'rohprotein_min': 500,   # 0.5kg Eiweiß (Mindestbedarf Ruhepferd)  
            'rohprotein_max': 800,   # 0.8kg Eiweiß (Obergrenze Arbeitspferd)
            'fruktan_max': 50        # 0.05kg Fruktan (max. empfohlen - Hufrehe-Risiko)
        }
        
        # Berechne Richtwerte für das spezifische Pferd
        gewicht_faktor = pferd_gewicht_kg / 100.0
        richtwerte = {k: v * gewicht_faktor for k, v in richtwerte_pro_100kg.items()}
        
        # Futter-Analysewerte mit Farbkontrolle anzeigen (nur die 3 wichtigsten)
        if hasattr(self, 'label_h_rohprotein'):
            farbe = self.get_naehrwert_farbe(rohprotein_g, 
                                           richtwerte['rohprotein_min'], 
                                           richtwerte['rohprotein_max'])
            self.label_h_rohprotein.setText(f"{rohprotein_g:.0f}g")
            self.label_h_rohprotein.setStyleSheet(f"color: {farbe}; font-weight: bold;")
            
        if hasattr(self, 'label_h_rohfaser'):
            farbe = self.get_naehrwert_farbe(rohfaser_g, 
                                           richtwerte['rohfaser_min'], 
                                           richtwerte['rohfaser_max'])
            self.label_h_rohfaser.setText(f"{rohfaser_g:.0f}g")
            self.label_h_rohfaser.setStyleSheet(f"color: {farbe}; font-weight: bold;")
            
        # FRUKTAN - nur Obergrenze prüfen (viel = gefährlich bei Hufrehe)
        if hasattr(self, 'label_h_fruktan'):
            if fruktan_g > richtwerte['fruktan_max']:
                farbe = "red"  # Zu viel Fruktan = Hufrehe-Risiko
            elif fruktan_g > richtwerte['fruktan_max'] * 0.7:
                farbe = "orange"  # Vorsicht bei hohem Fruktan
            else:
                farbe = "green"  # Fruktan OK
            self.label_h_fruktan.setText(f"{fruktan_g:.0f}g")
            self.label_h_fruktan.setStyleSheet(f"color: {farbe}; font-weight: bold;")
            
    def get_naehrwert_farbe(self, ist_wert, min_wert, max_wert):
        """Gibt Farbe basierend auf ernährungsphysiologischen Richtwerten zurück"""
        if ist_wert < min_wert:
            return "#FFA500"  # Orange - zu wenig
        elif ist_wert > max_wert:  
            return "#FF0000"  # Rot - zu viel (kritisch!)
        else:
            return "#00FF00"  # Grün - optimal

    def set_karre_gewicht(self, gewicht):
        """Setzt das Karre-Gewicht (von Beladen-Seite)"""
        self.karre_gewicht = gewicht
        self.start_gewicht = gewicht
        logger.info(f"Karre-Gewicht von Beladen-Seite übernommen: {gewicht:.2f} kg")
        self.update_gewichts_anzeigen()

    # Simuliere_fuetterung entfernt - wird jetzt automatisch über btn_next_rgv gehandhabt

    def update_gewichts_anzeigen(self):
        """Aktualisiert alle Gewichts-Anzeigen - verwendet sensor_manager"""
        try:
            # Einheitliche Gewichtsquelle: sensor_manager
            # Im Simulation-Modus: hx711_sim workflow simulation
            # Im Produktiv-Modus: echte Hardware
            if hasattr(self, 'navigation') and hasattr(self.navigation, 'sensor_manager'):
                aktuelles_gewicht = self.navigation.sensor_manager.read_weight()
                self.karre_gewicht = aktuelles_gewicht
            
            # Karre-Gewicht anzeigen
            if hasattr(self, 'label_karre_gewicht_anzeigen'):
                self.label_karre_gewicht_anzeigen.setText(f"{self.karre_gewicht:.2f}")

            # Entnommenes Gewicht anzeigen
            if hasattr(self, 'label_fu_entnommen'):
                self.label_fu_entnommen.setText(f"{self.entnommenes_gewicht:.2f}")

            # Debug-Ausgabe
            print(f"DEBUG: Karre-Gewicht: {self.karre_gewicht:.2f} kg")
            print(f"DEBUG: Entnommen: {self.entnommenes_gewicht:.2f} kg")
            
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren der Gewichtsanzeige: {e}")
        print(f"DEBUG: Label 'label_fu_entnommen' aktualisiert")

    def update_displays(self):
        """Echtzeit-Updates für alle Anzeigen INKLUSIVE Ernährungscontrolling"""
        try:
            # Gewichts-Anzeigen aktualisieren
            self.update_gewichts_anzeigen()

            # ECHTZEIT-ERNÄHRUNGSCONTROLLING: Analysewerte mit aktueller Entnahme neu berechnen
            if hasattr(self, 'aktuelle_futter_daten') and self.aktuelle_futter_daten and self.entnommenes_gewicht > 0:
                self.zeige_futter_analysewerte(self.aktuelle_futter_daten, self.entnommenes_gewicht)

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
        """Wechselt zum nächsten Pferd und triggert automatische Simulation"""
        # Simulation: 4.5kg automatisch entnehmen
        if hx711_sim.ist_simulation_aktiv():
            hx711_sim.pferd_gefuettert()  # Automatische 4.5kg Entnahme
            self.entnommenes_gewicht = 4.5  # Für Anzeige
            logger.info("Simulation: 4.5kg automatisch entnommen")
            
            # Futter-Analysewerte mit tatsächlicher Menge aktualisieren
            if self.aktuelle_futter_daten:
                self.zeige_futter_analysewerte(self.aktuelle_futter_daten, self.entnommenes_gewicht)
        
        # Zum nächsten Pferd wechseln
        if self.navigation:
            naechstes_pferd = self.navigation.naechstes_pferd()
            if naechstes_pferd:
                self.zeige_pferd_daten(naechstes_pferd)
        
        # Anzeigen aktualisieren
        self.update_gewichts_anzeigen()

    def zurueck_zur_auswahl(self):
        if self.navigation:
            self.navigation.go_back()

    def zu_einstellungen(self):
        if self.navigation:
            self.navigation.show_status("einstellungen")
