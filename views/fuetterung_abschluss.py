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
            
        # Feste Fenstergröße für Touchscreen
        self.setFixedSize(1024, 600)
        
        # Position: unter der Raspberry Pi Statusleiste (60px Abstand von oben)
        self.move(0, 60)
            
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
            # Gesamtmenge berechnen
            gefuetterte_pferde = fuetterung_daten.get('gefuetterte_pferde', 0)
            menge_pro_pferd = fuetterung_daten.get('menge_pro_pferd', 4.5)
            gesamtmenge = gefuetterte_pferde * menge_pro_pferd
            
            # Werte setzen
            if hasattr(self, 'label_gesamtmenge_wert'):
                self.label_gesamtmenge_wert.setText(f"{gesamtmenge:.1f} kg")
                
            if hasattr(self, 'label_futtertyp_wert'):
                futtertyp = fuetterung_daten.get('futtertyp', 'Heu eigen 2025')
                self.label_futtertyp_wert.setText(futtertyp)
                
            if hasattr(self, 'label_pferde_wert'):
                gesamte_boxen = fuetterung_daten.get('gesamte_boxen', 32)
                self.label_pferde_wert.setText(f"{gefuetterte_pferde} von {gesamte_boxen} Boxen")
                
            # Dauer berechnen
            if self.fuetterung_start_zeit:
                dauer = datetime.now() - self.fuetterung_start_zeit
                dauer_minuten = int(dauer.total_seconds() / 60)
                if hasattr(self, 'label_dauer_wert'):
                    self.label_dauer_wert.setText(f"{dauer_minuten} Minuten")
            
            # Nächste Fütterung (6 Stunden später)
            naechste_fuetterung = datetime.now() + timedelta(hours=6)
            if hasattr(self, 'label_naechste_wert'):
                self.label_naechste_wert.setText(naechste_fuetterung.strftime("%H:%M Uhr"))
                
            logger.info(f"Fütterung-Zusammenfassung angezeigt: {gesamtmenge:.1f}kg, {gefuetterte_pferde} Pferde")
            
        except Exception as e:
            logger.error(f"Fehler beim Anzeigen der Zusammenfassung: {e}")
            
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