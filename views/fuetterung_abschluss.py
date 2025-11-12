from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FuetterungAbschluss(QWidget):
    def __init__(self, navigation=None):
        super().__init__()
        self.navigation = navigation
        self.fuetterung_start_zeit = None
        
        # UI laden
        try:
            uic.loadUi('views/fuetterung_abschluss.ui', self)
            logger.info("fuetterung_abschluss.ui erfolgreich geladen")
        except Exception as e:
            logger.error(f"Fehler beim Laden der UI: {e}")
            
        # Vollbild für PiTouch2 (1280x720) - komplette Display-Nutzung
        self.setFixedSize(1280, 720)
        
        # Position: oben links (0,0) - Display vollständig nutzen
        self.move(0, 0)
            
        self.connect_buttons()
        
    def connect_buttons(self):
        """Verbindet alle Buttons"""
        if hasattr(self, 'btn_neue_fuetterung'):
            self.btn_neue_fuetterung.clicked.connect(self.neue_fuetterung)
        if hasattr(self, 'btn_zum_start'):
            self.btn_zum_start.clicked.connect(self.zum_start)
            
    def zeige_zusammenfassung(self, fuetterung_daten):
        """Zeigt die Fütterung-Zusammenfassung"""
        try:
            # Erweiterte Daten extrahieren
            heu_gesamt = fuetterung_daten.get('heu_gesamt', 0)
            heulage_gesamt = fuetterung_daten.get('heulage_gesamt', 0)
            heu_pferde = fuetterung_daten.get('heu_pferde', 0)
            heulage_pferde = fuetterung_daten.get('heulage_pferde', 0)
            gesamtmenge = fuetterung_daten.get('gesamtmenge', heu_gesamt + heulage_gesamt)
            gefuetterte_pferde_gesamt = heu_pferde + heulage_pferde
            
            # 1. GESAMTMENGE
            if hasattr(self, 'label_gesamtmenge_wert'):
                self.label_gesamtmenge_wert.setText(f"{gesamtmenge:.1f} kg")
            
            # 2. HEU AUFSPALTUNG  
            if hasattr(self, 'label_heu_wert'):
                if heu_gesamt > 0:
                    self.label_heu_wert.setText(f"{heu_gesamt:.1f} kg ({heu_pferde} Pferde)")
                else:
                    self.label_heu_wert.setText("0 kg (kein Heu)")
            
            # 3. HEULAGE AUFSPALTUNG
            if hasattr(self, 'label_heulage_wert'):
                if heulage_gesamt > 0:
                    self.label_heulage_wert.setText(f"{heulage_gesamt:.1f} kg ({heulage_pferde} Pferde)")
                else:
                    self.label_heulage_wert.setText("0 kg (keine Heulage)")
            
            # 4. PFERDE KORREKT (echte Anzahl statt 32 fest)
            if hasattr(self, 'label_pferde_wert'):
                # Annahme: Wir haben so viele Boxen wie gefütterte Pferde (realistische Anzeige)
                self.label_pferde_wert.setText(f"{gefuetterte_pferde_gesamt} von {gefuetterte_pferde_gesamt} Boxen")
                
            # 5. ECHTE DAUER berechnen
            if self.fuetterung_start_zeit:
                dauer = datetime.now() - self.fuetterung_start_zeit
                dauer_minuten = int(dauer.total_seconds() / 60)
                if hasattr(self, 'label_dauer_wert'):
                    self.label_dauer_wert.setText(f"{dauer_minuten} Minuten")
            else:
                if hasattr(self, 'label_dauer_wert'):
                    self.label_dauer_wert.setText("Unbekannt")
            
            # 6. INTELLIGENTE NÄCHSTE FÜTTERUNG
            naechste_zeit, naechste_art = self.berechne_naechste_fuetterung()
            if hasattr(self, 'label_naechste_wert'):
                self.label_naechste_wert.setText(f"{naechste_zeit} ({naechste_art})")
                
            logger.info(f"📊 Fütterung-Zusammenfassung: Gesamt={gesamtmenge:.1f}kg, Heu={heu_gesamt:.1f}kg ({heu_pferde}P), Heulage={heulage_gesamt:.1f}kg ({heulage_pferde}P)")
            
        except Exception as e:
            logger.error(f"Fehler beim Anzeigen der Zusammenfassung: {e}")
    
    def berechne_naechste_fuetterung(self):
        """Berechnet intelligente nächste Fütterungszeit basierend auf Tageszeit"""
        try:
            jetzt = datetime.now()
            stunde = jetzt.hour
            
            # Fütterungszeiten: 05:45 Heulage, 16:30 Heu
            if stunde < 5 or (stunde == 5 and jetzt.minute < 45):
                # Vor 05:45 - nächste ist Heulage um 05:45
                naechste = jetzt.replace(hour=5, minute=45, second=0, microsecond=0)
                return naechste.strftime("%H:%M Uhr"), "Heulage"
            elif stunde < 16 or (stunde == 16 and jetzt.minute < 30):
                # Nach 05:45 aber vor 16:30 - nächste ist Heu um 16:30
                naechste = jetzt.replace(hour=16, minute=30, second=0, microsecond=0)
                return naechste.strftime("%H:%M Uhr"), "Heu"
            else:
                # Nach 16:30 - nächste ist Heulage am nächsten Tag um 05:45
                naechste = (jetzt + timedelta(days=1)).replace(hour=5, minute=45, second=0, microsecond=0)
                return naechste.strftime("%H:%M Uhr"), "Heulage"
                
        except Exception as e:
            logger.error(f"Fehler bei nächster Fütterung-Berechnung: {e}")
            # Fallback: +6 Stunden
            naechste_fuetterung = datetime.now() + timedelta(hours=6)
            return naechste_fuetterung.strftime("%H:%M Uhr"), "Unbekannt"
            
    def set_start_zeit(self, start_zeit):
        """Setzt die Fütterung-Startzeit"""
        self.fuetterung_start_zeit = start_zeit
        
    def neue_fuetterung(self):
        """Startet eine neue Fütterung"""
        if self.navigation:
            # Zurück zur Auswahl-Seite für neue Fütterung
            self.navigation.show_status("auswahl")
            logger.info("Neue Fütterung gestartet")
            
    def zum_start(self):
        """Geht zum Start-Screen zurück"""
        if self.navigation:
            self.navigation.show_status("start")
            logger.info("Zurück zum Start-Screen")