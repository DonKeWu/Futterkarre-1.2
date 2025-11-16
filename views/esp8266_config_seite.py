#!/usr/bin/env python3
"""
ESP8266 Wireless Konfiguration für Futterkarre
Ermöglicht die Konfiguration der ESP8266 WiFi-Waage
"""

import logging
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from utils.base_ui_widget import BaseViewWidget
from utils.settings_manager import SettingsManager

# Wireless-Module optional laden
try:
    from wireless.wireless_weight_manager import WirelessWeightManager
    from wireless.esp8266_discovery import ESP8266Discovery
    WIRELESS_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Wireless-Module nicht verfügbar: {e}")
    WirelessWeightManager = None
    ESP8266Discovery = None
    WIRELESS_AVAILABLE = False

logger = logging.getLogger(__name__)

class ESP8266StatusThread(QThread):
    """Thread für periodischen ESP8266 Status-Check"""
    status_updated = pyqtSignal(dict)  # ESP8266 Status-Update
    connection_changed = pyqtSignal(bool, str)  # (connected, ip_address)
    
    def __init__(self, discovery_manager=None):
        super().__init__()
        self.discovery = discovery_manager
        self.running = False
        self.check_interval = 20  # 20 Sekunden für Stabilität
        
    def run(self):
        """Status-Check Loop"""
        self.running = True
        while self.running:
            try:
                if self.discovery:
                    # ESP8266 suchen
                    esp8266_ip = self.discovery.find_esp8266()
                    
                    if esp8266_ip:
                        # Status abrufen - nutze HTTP Status Funktion für dict
                        status_data = self.discovery.test_http_status(esp8266_ip)
                        if status_data and isinstance(status_data, dict):
                            self.status_updated.emit(status_data)
                            self.connection_changed.emit(True, esp8266_ip)
                        else:
                            self.connection_changed.emit(False, "")
                    else:
                        self.connection_changed.emit(False, "")
                else:
                    logger.warning("ESP8266Discovery nicht verfügbar")
                    
            except Exception as e:
                logger.error(f"Fehler im ESP8266 Status Thread: {e}")
                self.connection_changed.emit(False, "")
            
            # 15 Sekunden warten (weniger frequent updates für stabilität)
            for _ in range(150):  # 15s in 0.1s Schritten für responsive stop
                if not self.running:
                    break
                self.msleep(100)
    
    def stop(self):
        """Thread stoppen"""
        self.running = False
        self.quit()
        self.wait(3000)  # Max 3s warten


class ESP8266ConfigSeite(BaseViewWidget):
    """ESP8266 Wireless Konfigurationsseite"""
    
    def __init__(self, parent=None):
        super().__init__(parent, ui_filename="esp8266_config_seite.ui", page_name="esp8266_config")
        
        # Settings Manager
        self.settings_manager = SettingsManager()
        
        # Wireless Manager
        self.wireless_manager = None
        
        # Discovery Manager
        self.discovery = None
        if WIRELESS_AVAILABLE and ESP8266Discovery:
            try:
                self.discovery = ESP8266Discovery()
            except Exception as e:
                logger.warning(f"ESP8266Discovery Initialisierung fehlgeschlagen: {e}")
        else:
            logger.warning("ESP8266Discovery nicht verfügbar - Wireless-Module fehlen")
        
        # Status Thread
        self.status_thread = None
        
        # Aktueller ESP8266 Status
        self.current_esp_ip = None
        self.current_status = {}
        
        # UI Setup
        self.setup_ui()
        self.load_current_config()
        
        # Auto-Update starten wenn aktiviert
        if hasattr(self, 'cb_auto_update') and self.cb_auto_update.isChecked():
            self.start_status_monitoring()
    
    def setup_ui(self):
        """UI-Elemente konfigurieren und Signale verbinden"""
        try:
            # Zurück Button
            if hasattr(self, 'btn_back'):
                self.btn_back.clicked.connect(self.zurueck_zu_einstellungen)
            
            # WiFi-Konfiguration Buttons
            if hasattr(self, 'btn_show_password'):
                self.btn_show_password.clicked.connect(self.toggle_password_visibility)
            
            # ESP8266 Aktions-Buttons
            if hasattr(self, 'btn_test_connection'):
                self.btn_test_connection.clicked.connect(self.test_connection)
            
            if hasattr(self, 'btn_tare_scale'):
                self.btn_tare_scale.clicked.connect(self.tare_scale)
            
            if hasattr(self, 'btn_get_status'):
                self.btn_get_status.clicked.connect(self.get_esp8266_status)
            
            if hasattr(self, 'btn_deep_sleep'):
                self.btn_deep_sleep.clicked.connect(self.activate_deep_sleep)
            
            if hasattr(self, 'btn_calibrate'):
                self.btn_calibrate.clicked.connect(self.calibrate_scale)
            
            # Konfigurations-Buttons
            if hasattr(self, 'btn_save_config'):
                self.btn_save_config.clicked.connect(self.save_configuration)
            
            if hasattr(self, 'btn_reset_config'):
                self.btn_reset_config.clicked.connect(self.reset_configuration)
            
            # Auto-Update Checkbox
            if hasattr(self, 'cb_auto_update'):
                self.cb_auto_update.stateChanged.connect(self.toggle_auto_update)
            
            # Status initialisieren
            self.update_connection_status(False, "")
            self.log_message("ESP8266 Konfiguration bereit")
            
        except Exception as e:
            logger.error(f"Fehler beim UI-Setup: {e}")
    
    def load_current_config(self):
        """Lädt aktuelle Konfiguration in UI-Felder"""
        try:
            # WiFi-Konfiguration aus ESP8266 Code lesen
            esp8266_file = Path(__file__).parent.parent / "wireless" / "esp8266" / "futterkarre_wireless_waage_esp8266" / "futterkarre_wireless_waage_esp8266.ino"
            
            if esp8266_file.exists():
                with open(esp8266_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # SSID und Passwort extrahieren
                import re
                
                # Heimnetz SSID
                home_ssid_match = re.search(r'const char\* HOME_WIFI_SSID = "([^"]*)"', content)
                if home_ssid_match and hasattr(self, 'input_home_ssid'):
                    self.input_home_ssid.setText(home_ssid_match.group(1))
                
                # Heimnetz Passwort
                home_pw_match = re.search(r'const char\* HOME_WIFI_PASSWORD = "([^"]*)"', content)
                if home_pw_match and hasattr(self, 'input_home_password'):
                    self.input_home_password.setText(home_pw_match.group(1))
                
                # AP SSID
                ap_ssid_match = re.search(r'const char\* AP_SSID = "([^"]*)"', content)
                if ap_ssid_match and hasattr(self, 'input_ap_ssid'):
                    self.input_ap_ssid.setText(ap_ssid_match.group(1))
                
                # AP Passwort
                ap_pw_match = re.search(r'const char\* AP_PASSWORD = "([^"]*)"', content)
                if ap_pw_match and hasattr(self, 'input_ap_password'):
                    self.input_ap_password.setText(ap_pw_match.group(1))
                
                self.log_message("Konfiguration aus ESP8266 Code geladen")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Konfiguration: {e}")
            self.log_message(f"Fehler beim Laden: {e}")
    
    def zurueck_zu_einstellungen(self):
        """Zurück zur Einstellungsseite"""
        try:
            self.stop_status_monitoring()
            self.parent().navigate_to_page("einstellungen")
        except Exception as e:
            logger.error(f"Navigation Fehler: {e}")
    
    def toggle_password_visibility(self):
        """Passwort-Sichtbarkeit umschalten"""
        try:
            if hasattr(self, 'input_home_password'):
                if self.input_home_password.echoMode() == QLineEdit.Password:
                    self.input_home_password.setEchoMode(QLineEdit.Normal)
                    self.btn_show_password.setText("🙈")
                else:
                    self.input_home_password.setEchoMode(QLineEdit.Password) 
                    self.btn_show_password.setText("👁")
        except Exception as e:
            logger.error(f"Fehler beim Passwort Toggle: {e}")
    
    def test_connection(self):
        """ESP8266 Verbindung testen"""
        try:
            self.log_message("🔍 Scanne Netzwerk nach ESP8266...")
            
            if not self.discovery:
                self.log_message("❌ ESP8266Discovery nicht verfügbar")
                return
            
            # ESP8266 testen (bekannte IP zuerst)
            esp_ip = None
            known_ips = ["192.168.2.17", "192.168.4.1"]  # Bekannte IPs zuerst
            
            for test_ip in known_ips:
                if self.discovery.test_http_status(test_ip):
                    esp_ip = test_ip
                    break
            
            if esp_ip:
                self.log_message(f"🔗 Verbindung zu ESP8266 {esp_ip} hergestellt")
                self.current_esp_ip = esp_ip
                self.update_connection_status(True, esp_ip)
                
                # Status abrufen
                self.get_esp8266_status()
            else:
                self.log_message("❌ ESP8266 nicht im Netzwerk gefunden - Gerät eingeschaltet?")
                self.update_connection_status(False, "")
                
        except Exception as e:
            logger.error(f"Fehler beim Verbindungstest: {e}")
            self.log_message(f"❌ Verbindungstest fehlgeschlagen: {e}")
    
    def tare_scale(self):
        """Waage taren (nullen)"""
        try:
            if not self.current_esp_ip:
                self.log_message("❌ Keine ESP8266 Verbindung")
                return
            
            self.log_message("🔄 Tare Kommando senden...")
            
            if self.discovery:
                result = self.discovery.send_tare_command(self.current_esp_ip)
                if result:
                    self.log_message("✅ Waage erfolgreich getart")
                else:
                    self.log_message("❌ Tare fehlgeschlagen")
            
        except Exception as e:
            logger.error(f"Fehler beim Taren: {e}")
            self.log_message(f"❌ Tare Fehler: {e}")
    
    def get_esp8266_status(self):
        """ESP8266 Status abrufen"""
        try:
            if not self.current_esp_ip:
                self.log_message("❌ Keine ESP8266 Verbindung")
                return
            
            # Kein separates "Status abrufen" Log - wird durch das Ergebnis ersetzt
            
            if self.discovery:
                status = self.discovery.test_http_status(self.current_esp_ip)
                if status and isinstance(status, dict):
                    self.update_status_display(status)
                    # Aussagekräftige Status-Info
                    signal = status.get('signal_strength', 'N/A')
                    battery = status.get('battery_voltage', 0)
                    uptime = status.get('uptime', 0) // 1000  # ms zu s
                    self.log_message(f"✅ ESP8266: Signal {signal}dBm, Akku {battery:.1f}V, Laufzeit {uptime}s")
                else:
                    self.log_message(f"❌ ESP8266 ({self.current_esp_ip}) nicht erreichbar")
            
        except Exception as e:
            logger.error(f"Fehler beim Status-Abruf: {e}")
            self.log_message(f"❌ Status Fehler: {e}")
    
    def calibrate_scale(self):
        """Waage kalibrieren"""
        try:
            if not self.current_esp_ip:
                self.log_message("❌ Keine ESP8266 Verbindung")
                return
            
            # Referenzgewicht aus UI holen
            if hasattr(self, 'input_cal_weight'):
                try:
                    cal_weight = float(self.input_cal_weight.text())
                except ValueError:
                    self.log_message("❌ Ungültiges Kalibriergewicht")
                    return
            else:
                cal_weight = 20.0
            
            self.log_message(f"🎯 Kalibriere mit {cal_weight} kg...")
            
            if self.discovery:
                result = self.discovery.send_calibrate_command(self.current_esp_ip, cal_weight)
                if result:
                    self.log_message(f"✅ Kalibrierung mit {cal_weight} kg erfolgreich")
                else:
                    self.log_message("❌ Kalibrierung fehlgeschlagen")
            
        except Exception as e:
            logger.error(f"Fehler bei Kalibrierung: {e}")
            self.log_message(f"❌ Kalibrierungs-Fehler: {e}")
    
    def activate_deep_sleep(self):
        """ESP8266 Deep Sleep aktivieren"""
        try:
            if not self.current_esp_ip:
                self.log_message("❌ Keine ESP8266 Verbindung")
                return
            
            # Sicherheitsabfrage
            reply = QMessageBox.question(self, 
                                       "Deep Sleep aktivieren",
                                       "ESP8266 wird für 1 Stunde in Deep Sleep gehen.\n"
                                       "Während dieser Zeit ist keine Kommunikation möglich.\n\n"
                                       "Fortfahren?",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.log_message("😴 Deep Sleep aktivieren...")
                
                if self.discovery:
                    result = self.discovery.send_deep_sleep_command(self.current_esp_ip)
                    if result:
                        self.log_message("✅ Deep Sleep aktiviert - ESP8266 schläft 1h")
                        self.update_connection_status(False, "")
                    else:
                        self.log_message("❌ Deep Sleep Aktivierung fehlgeschlagen")
            
        except Exception as e:
            logger.error(f"Fehler bei Deep Sleep: {e}")
            self.log_message(f"❌ Deep Sleep Fehler: {e}")
    
    def save_configuration(self):
        """WiFi-Konfiguration in ESP8266 Code speichern"""
        try:
            # Werte aus UI lesen
            home_ssid = self.input_home_ssid.text() if hasattr(self, 'input_home_ssid') else ""
            home_password = self.input_home_password.text() if hasattr(self, 'input_home_password') else ""
            ap_ssid = self.input_ap_ssid.text() if hasattr(self, 'input_ap_ssid') else ""
            ap_password = self.input_ap_password.text() if hasattr(self, 'input_ap_password') else ""
            
            if not home_ssid or not home_password:
                self.log_message("❌ SSID und Passwort sind erforderlich")
                return
            
            # ESP8266 Code-Datei bearbeiten
            esp8266_file = Path(__file__).parent.parent / "wireless" / "esp8266" / "futterkarre_wireless_waage_esp8266" / "futterkarre_wireless_waage_esp8266.ino"
            
            if not esp8266_file.exists():
                self.log_message("❌ ESP8266 Code-Datei nicht gefunden")
                return
            
            # Datei lesen
            with open(esp8266_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # WiFi-Konfiguration ersetzen
            import re
            
            # HOME_WIFI_SSID ersetzen
            content = re.sub(
                r'const char\* HOME_WIFI_SSID = "[^"]*"',
                f'const char* HOME_WIFI_SSID = "{home_ssid}"',
                content
            )
            
            # HOME_WIFI_PASSWORD ersetzen
            content = re.sub(
                r'const char\* HOME_WIFI_PASSWORD = "[^"]*"',
                f'const char* HOME_WIFI_PASSWORD = "{home_password}"',
                content
            )
            
            # AP_SSID ersetzen
            content = re.sub(
                r'const char\* AP_SSID = "[^"]*"',
                f'const char* AP_SSID = "{ap_ssid}"',
                content
            )
            
            # AP_PASSWORD ersetzen
            content = re.sub(
                r'const char\* AP_PASSWORD = "[^"]*"',
                f'const char* AP_PASSWORD = "{ap_password}"',
                content
            )
            
            # Datei zurückschreiben
            with open(esp8266_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log_message("✅ Konfiguration gespeichert!")
            self.log_message("🔧 ESP8266 Code muss neu kompiliert und geflasht werden")
            
            # Optional: Backup in Settings
            wifi_config = {
                'home_ssid': home_ssid,
                'home_password': home_password,
                'ap_ssid': ap_ssid,
                'ap_password': ap_password,
                'last_updated': datetime.now().isoformat()
            }
            
            # TODO: In SettingsManager ESP8266 Konfiguration hinzufügen
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konfiguration: {e}")
            self.log_message(f"❌ Speichern fehlgeschlagen: {e}")
    
    def reset_configuration(self):
        """Konfiguration auf Standardwerte zurücksetzen"""
        try:
            reply = QMessageBox.question(self,
                                       "Konfiguration zurücksetzen",
                                       "Alle WiFi-Einstellungen auf Standardwerte zurücksetzen?",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Standardwerte setzen
                if hasattr(self, 'input_home_ssid'):
                    self.input_home_ssid.setText("IBIMSNOCH1MAL")
                if hasattr(self, 'input_home_password'):
                    self.input_home_password.setText("G8pY4B8K56vF")
                if hasattr(self, 'input_ap_ssid'):
                    self.input_ap_ssid.setText("Futterkarre_WiFi")
                if hasattr(self, 'input_ap_password'):
                    self.input_ap_password.setText("FutterWaage2025")
                
                self.log_message("🔄 Konfiguration zurückgesetzt")
        
        except Exception as e:
            logger.error(f"Fehler beim Reset: {e}")
    
    def toggle_auto_update(self, state):
        """Auto-Update ein-/ausschalten"""
        try:
            if state == Qt.Checked:
                self.start_status_monitoring()
                self.log_message("🔄 Auto-Update aktiviert (5s)")
            else:
                self.stop_status_monitoring()
                self.log_message("⏸️ Auto-Update deaktiviert")
        except Exception as e:
            logger.error(f"Fehler beim Auto-Update Toggle: {e}")
    
    def start_status_monitoring(self):
        """Status-Monitoring starten - QTimer statt QThread für bessere Signal-Stabilität"""
        try:
            if not hasattr(self, 'status_timer'):
                from PyQt5.QtCore import QTimer
                self.status_timer = QTimer()
                self.status_timer.timeout.connect(self.check_esp8266_status)
                self.status_timer.start(10000)  # 10 Sekunden
                logger.info("📡 ESP8266 Auto-Monitor gestartet (QTimer-basiert)")
            
        except Exception as e:
            logger.error(f"Fehler beim Starten des Status-Monitoring: {e}")
    
    def check_esp8266_status(self):
        """ESP8266 Status prüfen - läuft im Main-Thread"""
        try:
            if self.discovery:
                # Direkt bekannte IPs testen statt async find_esp8266()
                test_ips = ["192.168.2.17", "192.168.4.1"]  # Bekannte ESP8266 IPs
                
                for test_ip in test_ips:
                    logger.info(f"🔍 Testing ESP8266 IP: {test_ip}")
                    status_data = self.discovery.test_http_status(test_ip)
                    
                    if status_data and isinstance(status_data, dict):
                        logger.info(f"📊 SUCCESS - Status Data: {status_data}")
                        logger.info("✅ Calling update_status_display directly")
                        self.update_status_display(status_data)
                        self.update_connection_status(True, test_ip)
                        return  # Success - stop testing other IPs
                    else:
                        logger.info(f"❌ No response from {test_ip}")
                
                # If we get here, no IP responded
                logger.warning("❌ No ESP8266 responded")
                self.update_connection_status(False, "")
        except Exception as e:
            logger.error(f"Fehler bei ESP8266 Status Check: {e}")
    
    def stop_status_monitoring(self):
        """Status-Monitoring stoppen"""
        try:
            if self.status_thread and self.status_thread.isRunning():
                self.status_thread.stop()
                self.status_thread = None
        except Exception as e:
            logger.error(f"Fehler beim Stoppen des Status-Monitoring: {e}")
    
    def update_connection_status(self, connected: bool, ip_address: str):
        """Verbindungsstatus in UI aktualisieren"""
        try:
            if connected:
                # Verbunden
                if hasattr(self, 'lbl_wifi_status'):
                    self.lbl_wifi_status.setText("🟢 VERBUNDEN")
                    self.lbl_wifi_status.setStyleSheet("border: 2px solid #4CAF50; padding: 10px; background-color: #E8F5E8; color: #2E7D32;")
                
                if hasattr(self, 'lbl_ip_wert'):
                    self.lbl_ip_wert.setText(ip_address)
                
                self.current_esp_ip = ip_address
            else:
                # Getrennt
                if hasattr(self, 'lbl_wifi_status'):
                    self.lbl_wifi_status.setText("⚫ GETRENNT")
                    self.lbl_wifi_status.setStyleSheet("border: 2px solid #f44336; padding: 10px; background-color: #FFEBEE; color: #C62828;")
                
                if hasattr(self, 'lbl_ip_wert'):
                    self.lbl_ip_wert.setText("---.---.---.---")
                
                if hasattr(self, 'lbl_rssi_wert'):
                    self.lbl_rssi_wert.setText("--- dBm")
                
                if hasattr(self, 'lbl_akku_wert'):
                    self.lbl_akku_wert.setText("-.-- V")
                
                self.current_esp_ip = None
        
        except Exception as e:
            logger.error(f"Fehler beim Verbindungsstatus-Update: {e}")
    
    def update_status_display(self, status_data: dict):
        """ESP8266 Status in UI anzeigen"""
        try:
            logger.info(f"🎯 UPDATE_STATUS_DISPLAY called with: {status_data}")
            self.current_status = status_data
            
            # RSSI Signal (HTTP API verwendet 'signal_strength')
            if 'signal_strength' in status_data and hasattr(self, 'lbl_rssi_wert'):
                rssi = status_data['signal_strength']
                self.lbl_rssi_wert.setText(f"{rssi} dBm")
                
                # Farbe je nach Signalstärke (dBm - negativer Wert!)
                if rssi <= -80:
                    signal_color = "#f44336"  # Rot - sehr schwach
                elif rssi <= -70:
                    signal_color = "#FF9800"  # Orange - schwach  
                elif rssi <= -60:
                    signal_color = "#FFC107"  # Gelb - mäßig
                elif rssi <= -50:
                    signal_color = "#8BC34A"  # Hellgrün - gut
                else:
                    signal_color = "#4CAF50"  # Grün - ausgezeichnet
                
                self.lbl_rssi_wert.setStyleSheet(f"color: {signal_color}; font-weight: bold;")
            
            # Akku-Spannung (HTTP API verwendet 'battery_voltage')
            if 'battery_voltage' in status_data and hasattr(self, 'lbl_akku_wert'):
                battery = status_data['battery_voltage']
                self.lbl_akku_wert.setText(f"{battery:.2f} V")
                
                # Farbe je nach Spannung
                if battery < 3.2:
                    color = "#f44336"  # Rot - kritisch
                elif battery < 3.6:
                    color = "#FF9800"  # Orange - niedrig
                else:
                    color = "#4CAF50"  # Grün - gut
                
                self.lbl_akku_wert.setStyleSheet(f"color: {color}; font-weight: bold;")
            
            # Status-Log erweitern
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_message(f"📊 Status Update - RSSI: {status_data.get('signal_strength', 'N/A')} dBm, "
                           f"Akku: {status_data.get('battery_voltage', 0):.2f} V")
            
        except Exception as e:
            logger.error(f"Fehler beim Status-Display Update: {e}")
    
    def log_message(self, message: str):
        """Nachricht im Status-Log anzeigen"""
        try:
            if hasattr(self, 'text_log'):
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_entry = f"[{timestamp}] {message}"
                
                # Log erweitern
                current_text = self.text_log.toPlainText()
                if current_text:
                    new_text = current_text + "\n" + log_entry
                else:
                    new_text = log_entry
                
                # Nur letzte 50 Zeilen behalten
                lines = new_text.split('\n')
                if len(lines) > 50:
                    lines = lines[-50:]
                    new_text = '\n'.join(lines)
                
                self.text_log.setPlainText(new_text)
                
                # Zum Ende scrollen
                scrollbar = self.text_log.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
        
        except Exception as e:
            logger.error(f"Fehler beim Logging: {e}")
    
    def showEvent(self, event):
        """Wird aufgerufen wenn Seite angezeigt wird"""
        super().showEvent(event)
        try:
            # Auto-Update starten wenn aktiviert
            if hasattr(self, 'cb_auto_update') and self.cb_auto_update.isChecked():
                self.start_status_monitoring()
        except Exception as e:
            logger.error(f"Fehler beim ShowEvent: {e}")
    
    def hideEvent(self, event):
        """Wird aufgerufen wenn Seite verlassen wird"""
        super().hideEvent(event)
        try:
            # Status-Monitoring stoppen
            self.stop_status_monitoring()
        except Exception as e:
            logger.error(f"Fehler beim HideEvent: {e}")
    
    def closeEvent(self, event):
        """Beim Schließen aufräumen"""
        try:
            self.stop_status_monitoring()
        except Exception as e:
            logger.error(f"Fehler beim CloseEvent: {e}")
        
        super().closeEvent(event)


if __name__ == "__main__":
    """Test der ESP8266 Konfigurationsseite"""
    import sys
    
    app = QApplication(sys.argv)
    
    # Test-Fenster erstellen
    window = ESP8266ConfigSeite()
    window.show()
    
    sys.exit(app.exec_())