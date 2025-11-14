#!/usr/bin/env python3
"""
Waagen-Kalibrierungs-Seite
Vollständige Kalibrierung der HX711 Wägezellen

Features:
- Live Gewichtsanzeige (Gesamt + 4 Einzelzellen)
- Schritt-für-Schritt Kalibrierung
- Tara (Nullpunkt setzen)
- Referenzgewicht-Kalibrierung
- Kalibrierungs-Test und -Validierung
- Persistente Speicherung der Kalibrierwerte
- Integration mit HX711 Hardware
"""

import sys
import logging
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox
import os

# Logger Setup
logger = logging.getLogger(__name__)
from pathlib import Path
from datetime import datetime

# Projekt-spezifische Imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.base_ui_widget import BaseViewWidget
from utils.settings_manager import get_settings_manager
# Hardware-Module mit Fallback
try:
    from hardware.hx711_real import (
        hx_sensors, HX711_AVAILABLE,
        lese_gewicht_hx711, lese_einzelzellwerte_hx711,
        nullpunkt_setzen_alle, kalibriere_einzelzelle
    )
except ImportError as e:
    logger.warning(f"HX711-Hardware nicht verfügbar: {e}")
    # Fallback-Werte für Entwicklung ohne Hardware
    hx_sensors = []
    HX711_AVAILABLE = False
    
    def lese_gewicht_hx711():
        import random
        return random.uniform(0, 50)
    
    def lese_einzelzellwerte_hx711():
        import random
        return [random.uniform(0, 15) for _ in range(4)]
    
    def nullpunkt_setzen_alle():
        logger.info("Simulation: Nullpunkt gesetzt")
        return True
    
    def kalibriere_einzelzelle(index, gewicht):
        logger.info(f"Simulation: Sensor {index} mit {gewicht}kg kalibriert")
        return True

logger = logging.getLogger(__name__)

class WaagenKalibrierung(BaseViewWidget):
    """
    Waagen-Kalibrierungs-Seite mit Live-Anzeige und schrittweiser Kalibrierung
    
    Kalibrierungs-Prozess:
    1. Tara: Nullpunkt setzen (leerer Karren)
    2. Referenzgewicht: Bekanntes Gewicht auflegen und kalibrieren
    3. Test: Verschiedene Gewichte zur Validierung
    4. Speichern: Kalibrierwerte persistent speichern
    """
    
    # Signale
    kalibrierung_abgeschlossen = pyqtSignal(bool)  # Erfolgreich ja/nein
    
    def __init__(self, parent=None):
        # BaseViewWidget mit UI-Datei initialisieren  
        super().__init__(parent, ui_filename="waagen_kalibrierung.ui", page_name="waagen_kalibrierung")
        
        # Manager
        self.settings_manager = get_settings_manager()
        
        # Kalibrierungs-Status
        self.kalibrierung_schritt = 0  # 0=Start, 1=Tara, 2=Kalibriert, 3=Getestet
        self.tara_werte = [0.0, 0.0, 0.0, 0.0]  # Nullpunkt-Werte für 4 Sensoren
        self.kalibrier_faktoren = [1.0, 1.0, 1.0, 1.0]  # Skalenfaktoren
        self.referenz_gewicht = 20.0  # Standard 20kg
        self.toleranz = 0.05  # ±50g Toleranz
        
        # Timer für Live-Updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_live_anzeige)
        
        # UI initialisieren
        self.init_ui()
        self.load_kalibrierungs_daten()
        
        # Live-Updates starten wenn aktiviert
        if hasattr(self, 'cb_live_update') and self.cb_live_update.isChecked():
            self.start_live_updates()
        
        logger.info("WaagenKalibrierung initialisiert")
    
    def init_ui(self):
        """Initialisiert UI-Komponenten und Button-Callbacks"""
        try:
            # Button-Callbacks
            if hasattr(self, 'btn_back'):
                self.btn_back.clicked.connect(self.zurueck_geklickt)
            
            if hasattr(self, 'btn_tara'):
                self.btn_tara.clicked.connect(self.tara_durchfuehren)
            
            if hasattr(self, 'btn_kalibrieren'):
                self.btn_kalibrieren.clicked.connect(self.kalibrierung_durchfuehren)
            
            if hasattr(self, 'btn_test'):
                self.btn_test.clicked.connect(self.kalibrierung_testen)
            
            if hasattr(self, 'btn_speichern'):
                self.btn_speichern.clicked.connect(self.kalibrierwerte_speichern)
            
            if hasattr(self, 'btn_reset'):
                self.btn_reset.clicked.connect(self.kalibrierung_zuruecksetzen)
            
            # Input-Field Callbacks
            if hasattr(self, 'input_referenzgewicht'):
                self.input_referenzgewicht.textChanged.connect(self.referenzgewicht_geaendert)
            
            if hasattr(self, 'input_toleranz'):
                self.input_toleranz.textChanged.connect(self.toleranz_geaendert)
            
            # Live-Update Checkbox
            if hasattr(self, 'cb_live_update'):
                self.cb_live_update.toggled.connect(self.live_update_toggled)
            
            # Status aktualisieren
            self.update_status("Bereit für Kalibrierung...")
            self.update_kalibrierungs_buttons()
            
        except Exception as e:
            logger.error(f"Fehler bei UI-Initialisierung: {e}")
            self.update_status(f"UI-Fehler: {e}")
    
    def load_kalibrierungs_daten(self):
        """Lädt gespeicherte Kalibrierungsdaten"""
        try:
            # Kalibrierwerte aus Settings laden
            if hasattr(self.settings_manager, 'calibration'):
                cal_data = self.settings_manager.calibration
                
                # Tara-Werte
                if hasattr(cal_data, 'tare_values') and cal_data.tare_values:
                    self.tara_werte = cal_data.tare_values[:4]  # Nur erste 4 Werte
                
                # Kalibrier-Faktoren  
                if hasattr(cal_data, 'scale_factors') and cal_data.scale_factors:
                    self.kalibrier_faktoren = cal_data.scale_factors[:4]
                
                # Letztes Referenzgewicht
                if hasattr(cal_data, 'last_reference_weight'):
                    self.referenz_gewicht = float(cal_data.last_reference_weight)
                    if hasattr(self, 'input_referenzgewicht'):
                        self.input_referenzgewicht.setText(str(self.referenz_gewicht))
                
                # Status bestimmen
                if any(f != 1.0 for f in self.kalibrier_faktoren):
                    self.kalibrierung_schritt = 2  # Bereits kalibriert
                    self.update_status("Vorherige Kalibrierung geladen - bereit für Test")
                else:
                    self.kalibrierung_schritt = 0
                    self.update_status("Keine Kalibrierung gefunden - bitte Tara durchführen")
            
            logger.info(f"Kalibrierungsdaten geladen: Schritt {self.kalibrierung_schritt}")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Kalibrierungsdaten: {e}")
            self.update_status(f"Lade-Fehler: {e}")
    
    def start_live_updates(self):
        """Startet Live-Gewichtsanzeige"""
        if HX711_AVAILABLE and hx_sensors:
            self.update_timer.start(1000)  # 1 Sekunde Intervall
            self.update_status("Live-Updates gestartet")
        else:
            self.update_status("⚠️ Hardware nicht verfügbar - Simulation aktiv")
            # Simulierte Werte für Entwicklung
            self.update_timer.start(1000)
    
    def stop_live_updates(self):
        """Stoppt Live-Updates"""
        self.update_timer.stop()
        self.update_status("Live-Updates gestoppt")
    
    def update_live_anzeige(self):
        """Aktualisiert Live-Gewichtsanzeige"""
        try:
            if HX711_AVAILABLE and hx_sensors:
                # Echte Hardware-Werte
                gesamtgewicht = lese_gewicht_hx711()
                einzelwerte = lese_einzelzellwerte_hx711()
            else:
                # Simulation für Entwicklung
                import random
                gesamtgewicht = random.uniform(0, 50)
                einzelwerte = [
                    random.uniform(0, 15),
                    random.uniform(0, 15), 
                    random.uniform(0, 15),
                    random.uniform(0, 15)
                ]
            
            # Gesamtgewicht anzeigen
            if hasattr(self, 'lbl_gesamtgewicht_wert'):
                self.lbl_gesamtgewicht_wert.setText(f"{gesamtgewicht:.2f} kg")
            
            # Einzelzellen anzeigen
            if hasattr(self, 'lbl_vl_wert'):
                self.lbl_vl_wert.setText(f"{einzelwerte[0]:.2f} kg")
            if hasattr(self, 'lbl_vr_wert'):
                self.lbl_vr_wert.setText(f"{einzelwerte[1]:.2f} kg")
            if hasattr(self, 'lbl_hl_wert'):
                self.lbl_hl_wert.setText(f"{einzelwerte[2]:.2f} kg")
            if hasattr(self, 'lbl_hr_wert'):
                self.lbl_hr_wert.setText(f"{einzelwerte[3]:.2f} kg")
            
        except Exception as e:
            logger.error(f"Fehler bei Live-Update: {e}")
            self.update_status(f"Live-Update Fehler: {e}")
    
    def tara_durchfuehren(self):
        """Führt Tara (Nullpunkt setzen) durch"""
        try:
            # Warnung anzeigen
            reply = QMessageBox.question(
                self, "Tara durchführen",
                "Bitte leeren Sie den Karren vollständig.\n\nFortfahren mit Tara?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            self.update_status("🔄 Tara wird durchgeführt...")
            
            # Live-Updates temporär stoppen
            was_running = self.update_timer.isActive()
            if was_running:
                self.stop_live_updates()
            
            if HX711_AVAILABLE and hx_sensors:
                # Echte Hardware-Tara
                nullpunkt_setzen_alle()
                
                # Tara-Werte aus Sensoren lesen
                import time
                time.sleep(1)  # Kurz warten
                self.tara_werte = lese_einzelzellwerte_hx711()
                
                success = True
            else:
                # Simulation
                self.tara_werte = [0.0, 0.0, 0.0, 0.0]
                success = True
            
            if success:
                self.kalibrierung_schritt = 1
                self.update_status("✅ Tara erfolgreich - bereit für Kalibrierung mit Referenzgewicht")
                QMessageBox.information(self, "Tara", "Nullpunkt erfolgreich gesetzt!")
            else:
                self.update_status("❌ Tara fehlgeschlagen")
                QMessageBox.critical(self, "Fehler", "Tara konnte nicht durchgeführt werden!")
            
            # Live-Updates wieder starten
            if was_running:
                self.start_live_updates()
            
            self.update_kalibrierungs_buttons()
            
        except Exception as e:
            logger.error(f"Tara-Fehler: {e}")
            self.update_status(f"Tara-Fehler: {e}")
            QMessageBox.critical(self, "Fehler", f"Tara-Fehler: {e}")
    
    def kalibrierung_durchfuehren(self):
        """Führt Kalibrierung mit Referenzgewicht durch"""
        try:
            if self.kalibrierung_schritt < 1:
                QMessageBox.warning(self, "Warnung", "Bitte führen Sie zuerst eine Tara durch!")
                return
            
            # Referenzgewicht validieren
            try:
                ref_gewicht = float(self.input_referenzgewicht.text())
                if ref_gewicht <= 0:
                    raise ValueError("Referenzgewicht muss positiv sein")
                self.referenz_gewicht = ref_gewicht
            except ValueError as e:
                QMessageBox.critical(self, "Fehler", f"Ungültiges Referenzgewicht: {e}")
                return
            
            # Bestätigung
            reply = QMessageBox.question(
                self, "Kalibrierung",
                f"Bitte legen Sie genau {self.referenz_gewicht} kg auf den Karren.\n\nFortfahren mit Kalibrierung?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            self.update_status(f"🔄 Kalibrierung mit {self.referenz_gewicht} kg...")
            
            # Live-Updates stoppen
            was_running = self.update_timer.isActive()
            if was_running:
                self.stop_live_updates()
            
            if HX711_AVAILABLE and hx_sensors:
                # Echte Hardware-Kalibrierung
                success_count = 0
                
                for i, sensor in enumerate(hx_sensors):
                    try:
                        # Rohwert lesen
                        import time
                        time.sleep(0.5)
                        rohwerte = []
                        for _ in range(10):  # 10 Messungen für Durchschnitt
                            rohwert = sensor.hx.read()
                            rohwerte.append(rohwert)
                            time.sleep(0.1)
                        
                        durchschnitt = sum(rohwerte) / len(rohwerte)
                        
                        # Kalibrierfaktor berechnen
                        if durchschnitt != self.tara_werte[i]:
                            # Pro Sensor 1/4 des Gesamtgewichts angenommen
                            erwarteter_wert = self.referenz_gewicht / 4.0
                            self.kalibrier_faktoren[i] = erwarteter_wert / (durchschnitt - self.tara_werte[i])
                            success_count += 1
                            
                            logger.info(f"Sensor {i}: Faktor = {self.kalibrier_faktoren[i]:.6f}")
                        
                    except Exception as sensor_err:
                        logger.error(f"Kalibrierung Sensor {i} fehlgeschlagen: {sensor_err}")
                
                success = success_count >= 3  # Mindestens 3 von 4 Sensoren erfolgreich
                
            else:
                # Simulation
                self.kalibrier_faktoren = [0.1, 0.1, 0.1, 0.1]  # Beispielwerte
                success = True
            
            if success:
                self.kalibrierung_schritt = 2
                self.update_status("✅ Kalibrierung erfolgreich - bereit für Test")
                QMessageBox.information(self, "Kalibrierung", "Kalibrierung erfolgreich abgeschlossen!")
            else:
                self.update_status("❌ Kalibrierung fehlgeschlagen")
                QMessageBox.critical(self, "Fehler", "Kalibrierung konnte nicht durchgeführt werden!")
            
            # Live-Updates wieder starten
            if was_running:
                self.start_live_updates()
            
            self.update_kalibrierungs_buttons()
            
        except Exception as e:
            logger.error(f"Kalibrierungs-Fehler: {e}")
            self.update_status(f"Kalibrierungs-Fehler: {e}")
            QMessageBox.critical(self, "Fehler", f"Kalibrierung fehlgeschlagen: {e}")
    
    def kalibrierung_testen(self):
        """Testet die aktuelle Kalibrierung"""
        try:
            if self.kalibrierung_schritt < 2:
                QMessageBox.warning(self, "Warnung", "Bitte führen Sie zuerst eine Kalibrierung durch!")
                return
            
            self.update_status("🧪 Kalibrierung wird getestet...")
            
            # Testgewicht eingeben lassen
            test_gewicht, ok = QtWidgets.QInputDialog.getDouble(
                self, "Kalibrierungs-Test",
                "Testgewicht eingeben (kg):",
                self.referenz_gewicht, 0.1, 1000.0, 2
            )
            
            if not ok:
                return
            
            QMessageBox.information(
                self, "Test-Vorbereitung",
                f"Bitte legen Sie {test_gewicht} kg auf den Karren und drücken Sie OK."
            )
            
            # Gewicht messen
            if HX711_AVAILABLE and hx_sensors:
                gemessenes_gewicht = lese_gewicht_hx711()
            else:
                # Simulation: Zufällige Abweichung
                import random
                abweichung = random.uniform(-0.1, 0.1)
                gemessenes_gewicht = test_gewicht + abweichung
            
            # Abweichung berechnen
            abweichung = abs(gemessenes_gewicht - test_gewicht)
            prozent_abweichung = (abweichung / test_gewicht) * 100
            
            # Toleranz prüfen
            toleranz_ok = abweichung <= self.toleranz
            
            # Ergebnis anzeigen
            result_text = f"""
Kalibrierungs-Test Ergebnis:

Soll-Gewicht: {test_gewicht:.2f} kg
Gemessen: {gemessenes_gewicht:.2f} kg
Abweichung: {abweichung:.3f} kg ({prozent_abweichung:.1f}%)
Toleranz: ±{self.toleranz:.2f} kg

Status: {'✅ BESTANDEN' if toleranz_ok else '❌ NICHT BESTANDEN'}
"""
            
            if toleranz_ok:
                self.kalibrierung_schritt = 3
                self.update_status("✅ Kalibrierung validiert - bereit zum Speichern")
                QMessageBox.information(self, "Test erfolgreich", result_text)
            else:
                self.update_status("⚠️ Test nicht bestanden - Kalibrierung überprüfen")
                QMessageBox.warning(self, "Test nicht bestanden", result_text + "\n\nBitte Kalibrierung wiederholen.")
            
            self.update_kalibrierungs_buttons()
            
        except Exception as e:
            logger.error(f"Test-Fehler: {e}")
            self.update_status(f"Test-Fehler: {e}")
            QMessageBox.critical(self, "Fehler", f"Kalibrierungs-Test fehlgeschlagen: {e}")
    
    def kalibrierwerte_speichern(self):
        """Speichert Kalibrierungswerte persistent"""
        try:
            if self.kalibrierung_schritt < 2:
                QMessageBox.warning(self, "Warnung", "Keine Kalibrierungswerte zum Speichern vorhanden!")
                return
            
            # In Settings speichern
            if hasattr(self.settings_manager, 'calibration'):
                cal_data = self.settings_manager.calibration
                
                # Werte setzen
                cal_data.tare_values = self.tara_werte
                cal_data.scale_factors = self.kalibrier_faktoren
                cal_data.last_reference_weight = self.referenz_gewicht
                cal_data.calibration_date = datetime.now().isoformat()
                cal_data.is_valid = True
                
                # Speichern
                if self.settings_manager.save_settings():
                    self.update_status("💾 Kalibrierungswerte erfolgreich gespeichert")
                    QMessageBox.information(self, "Gespeichert", "Kalibrierungswerte wurden erfolgreich gespeichert!")
                    
                    # Signal senden
                    self.kalibrierung_abgeschlossen.emit(True)
                else:
                    raise Exception("Settings konnten nicht gespeichert werden")
            
        except Exception as e:
            logger.error(f"Speichern-Fehler: {e}")
            self.update_status(f"Speichern-Fehler: {e}")
            QMessageBox.critical(self, "Fehler", f"Speichern fehlgeschlagen: {e}")
    
    def kalibrierung_zuruecksetzen(self):
        """Setzt Kalibrierung auf Standardwerte zurück"""
        try:
            reply = QMessageBox.question(
                self, "Zurücksetzen",
                "Alle Kalibrierungswerte werden zurückgesetzt!\n\nFortfahren?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Werte zurücksetzen
                self.kalibrierung_schritt = 0
                self.tara_werte = [0.0, 0.0, 0.0, 0.0]
                self.kalibrier_faktoren = [1.0, 1.0, 1.0, 1.0]
                
                # UI aktualisieren
                self.update_status("🔄 Kalibrierung zurückgesetzt - bitte neu durchführen")
                self.update_kalibrierungs_buttons()
                
                QMessageBox.information(self, "Zurückgesetzt", "Kalibrierung wurde zurückgesetzt!")
            
        except Exception as e:
            logger.error(f"Reset-Fehler: {e}")
            QMessageBox.critical(self, "Fehler", f"Reset fehlgeschlagen: {e}")
    
    def update_kalibrierungs_buttons(self):
        """Aktualisiert Button-Status basierend auf Kalibrierungs-Schritt"""
        try:
            if hasattr(self, 'btn_tara'):
                self.btn_tara.setEnabled(True)  # Tara immer möglich
            
            if hasattr(self, 'btn_kalibrieren'):
                self.btn_kalibrieren.setEnabled(self.kalibrierung_schritt >= 1)
            
            if hasattr(self, 'btn_test'):
                self.btn_test.setEnabled(self.kalibrierung_schritt >= 2)
            
            if hasattr(self, 'btn_speichern'):
                self.btn_speichern.setEnabled(self.kalibrierung_schritt >= 2)
            
        except Exception as e:
            logger.error(f"Button-Update Fehler: {e}")
    
    def update_status(self, status_text):
        """Aktualisiert Status-Anzeige"""
        if hasattr(self, 'lbl_status'):
            self.lbl_status.setText(status_text)
        logger.info(f"Kalibrierungs-Status: {status_text}")
    
    def referenzgewicht_geaendert(self):
        """Referenzgewicht Input geändert"""
        try:
            text = self.input_referenzgewicht.text()
            if text:
                self.referenz_gewicht = float(text)
        except ValueError:
            pass  # Ignoriere ungültige Eingaben
    
    def toleranz_geaendert(self):
        """Toleranz Input geändert"""
        try:
            text = self.input_toleranz.text()
            if text:
                self.toleranz = float(text)
        except ValueError:
            pass  # Ignoriere ungültige Eingaben
    
    def live_update_toggled(self, checked):
        """Live-Update Checkbox geändert"""
        if checked:
            self.start_live_updates()
        else:
            self.stop_live_updates()
    
    def zurueck_geklickt(self):
        """Zurück-Button geklickt"""
        try:
            # Live-Updates stoppen
            self.stop_live_updates()
            
            # Zurück zur Einstellungsseite
            if self.navigation:
                self.navigation.show_status("einstellungen")
            
            logger.info("Zurück zur Einstellungsseite")
            
        except Exception as e:
            logger.error(f"Navigation-Fehler: {e}")
    
    def showEvent(self, event):
        """Wird aufgerufen wenn Seite angezeigt wird"""
        super().showEvent(event)
        
        # Live-Updates starten wenn aktiviert
        if hasattr(self, 'cb_live_update') and self.cb_live_update.isChecked():
            self.start_live_updates()
        
        logger.debug("WaagenKalibrierung angezeigt")
    
    def hideEvent(self, event):
        """Wird aufgerufen wenn Seite versteckt wird"""
        super().hideEvent(event)
        
        # Live-Updates stoppen
        self.stop_live_updates()
        
        logger.debug("WaagenKalibrierung versteckt")