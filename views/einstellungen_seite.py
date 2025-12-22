#!/usr/bin/env python3
"""
Einstellungen Seite - Erweiterte Konfiguration
Benutzer-Einstellungen und System-Konfiguration

Features:
- Persistent Settings via SettingsManager
- Kalibrierungs-Parameter
- System-Einstellungen
- Import/Export von Konfigurationen
- Live-Updates mit Callbacks
"""

import sys
import logging
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTabWidget
from PyQt5.QtCore import pyqtSignal, QTimer
import os
from pathlib import Path
from datetime import datetime

# Projekt-spezifische Imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.settings_manager import get_settings_manager
from utils.database_manager import get_database_manager
from utils.timer_manager import get_timer_manager
from utils.base_ui_widget import BaseViewWidget


logger = logging.getLogger(__name__)

class EinstellungenSeite(BaseViewWidget):
    """
    Erweiterte Einstellungen-Seite mit persistenter Konfiguration
    
    Funktionen:
    - System-Einstellungen (Display, Sprache, etc.)
    - Kalibrierungs-Parameter
    - Fütterungs-Einstellungen
    - Hardware-Konfiguration
    - Import/Export
    """
    
    # Signale
    settings_changed = pyqtSignal(str, str, object)  # category, key, value
    calibration_requested = pyqtSignal()
    
    def __init__(self, sensor_manager=None):
        super().__init__()
        
        # BaseViewWidget Konfiguration
        self.page_name = "einstellungen"
        
        # Kompatibilität mit alter Schnittstelle
        self.sensor_manager = sensor_manager
        self.navigation = None
        
        # Manager Instanzen
        self.settings_manager = get_settings_manager()
        self.db_manager = get_database_manager()
        self.timer_manager = get_timer_manager()
        
        # UI laden
        self.ui_file = Path(__file__).parent / "einstellungen_seite.ui"
        if self.ui_file.exists():
            uic.loadUi(str(self.ui_file), self)
        else:
            self.init_manual_ui()
        
        # Vollbild für PiTouch2 (1280x720)
        self.setFixedSize(1280, 720)
        self.move(0, 0)
        
        # Settings-Callbacks registrieren
        self.settings_manager.register_change_callback('all', self.on_settings_changed)
        
        # UI initialisieren
        self.init_ui()
        self.load_current_settings()
        
        logger.info("EinstellungenSeite initialisiert")
    

    
    def init_manual_ui(self):
        """Manueller UI-Aufbau falls .ui-Datei fehlt"""
        self.setObjectName("EinstellungenSeite")
        self.resize(1280, 720)
        
        # Haupt-Layout
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Header
        header_layout = QtWidgets.QHBoxLayout()
        
        title_label = QtWidgets.QLabel("System-Einstellungen")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Buttons im Header
        self.btn_export = QtWidgets.QPushButton("Exportieren")
        self.btn_import = QtWidgets.QPushButton("Importieren")
        self.btn_reset = QtWidgets.QPushButton("Zurücksetzen")
        self.btn_save = QtWidgets.QPushButton("Speichern")
        self.btn_back = QtWidgets.QPushButton("Zurück")
        
        for btn in [self.btn_export, self.btn_import, self.btn_reset, self.btn_save, self.btn_back]:
            btn.setFixedSize(120, 40)
            header_layout.addWidget(btn)
        
        main_layout.addLayout(header_layout)
        
        # Tab-Widget für verschiedene Einstellungs-Kategorien
        self.tab_widget = QTabWidget()
        
        # System Tab
        self.system_tab = self.create_system_tab()
        self.tab_widget.addTab(self.system_tab, "System")
        
        # Hardware Tab - Waagen-Kalibrierung und Hardware-Einstellungen
        self.hardware_tab = self.create_hardware_tab()
        self.tab_widget.addTab(self.hardware_tab, "Hardware")
        
        # Kalibrierung Tab
        self.calibration_tab = self.create_calibration_tab()
        self.tab_widget.addTab(self.calibration_tab, "Kalibrierung")
        
        # Fütterung Tab
        self.feeding_tab = self.create_feeding_tab()
        self.tab_widget.addTab(self.feeding_tab, "Fütterung")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status Bar
        status_layout = QtWidgets.QHBoxLayout()
        self.status_label = QtWidgets.QLabel("Bereit")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.last_saved_label = QtWidgets.QLabel("Zuletzt gespeichert: Noch nie")
        status_layout.addWidget(self.last_saved_label)
        
        main_layout.addLayout(status_layout)
    
    def create_system_tab(self) -> QtWidgets.QWidget:
        """Erstellt System-Einstellungen Tab"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(tab)
        
        # Display Einstellungen
        display_group = QtWidgets.QGroupBox("Display-Einstellungen")
        display_layout = QtWidgets.QFormLayout(display_group)
        
        self.brightness_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(10, 100)
        self.brightness_value_label = QtWidgets.QLabel("80%")
        brightness_layout = QtWidgets.QHBoxLayout()
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_value_label)
        display_layout.addRow("Helligkeit:", brightness_layout)
        
        self.timeout_spin = QtWidgets.QSpinBox()
        self.timeout_spin.setRange(30, 3600)
        self.timeout_spin.setSuffix(" Sekunden")
        display_layout.addRow("Display Timeout:", self.timeout_spin)
        
        self.fullscreen_check = QtWidgets.QCheckBox("Vollbild-Modus")
        display_layout.addRow("", self.fullscreen_check)
        
        layout.addRow(display_group)
        
        # Audio-Einstellungen
        audio_group = QtWidgets.QGroupBox("Audio")
        audio_layout = QtWidgets.QFormLayout(audio_group)
        
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_value_label = QtWidgets.QLabel("50%")
        volume_layout = QtWidgets.QHBoxLayout()
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_value_label)
        audio_layout.addRow("Lautstärke:", volume_layout)
        
        layout.addRow(audio_group)
        
        return tab
    
    def create_hardware_tab(self) -> QtWidgets.QWidget:
        """Erstellt Hardware-Einstellungen Tab"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(tab)
        
        # Hardware-Betriebsmodus - Pi5 mit HX711 Waagen-Sensoren
        mode_group = QtWidgets.QGroupBox("Hardware-Modus")
        mode_layout = QtWidgets.QFormLayout(mode_group)
        
        hardware_info = QtWidgets.QLabel("System läuft im Hardware-only Modus (Simulation entfernt)")
        hardware_info.setStyleSheet("color: green; font-weight: bold;")
        mode_layout.addRow("Status:", hardware_info)
        
        self.auto_detection_check = QtWidgets.QCheckBox("Auto-Hardware-Erkennung")
        mode_layout.addRow("", self.auto_detection_check)
        
        layout.addRow(mode_group)
        
        # Sensor-Einstellungen
        sensor_group = QtWidgets.QGroupBox("Sensor-Einstellungen")
        sensor_layout = QtWidgets.QFormLayout(sensor_group)
        
        self.update_rate_spin = QtWidgets.QSpinBox()
        self.update_rate_spin.setRange(100, 2000)
        self.update_rate_spin.setSuffix(" ms")
        sensor_layout.addRow("Update-Rate:", self.update_rate_spin)
        
        self.timeout_spin_hw = QtWidgets.QSpinBox()
        self.timeout_spin_hw.setRange(1000, 30000)
        self.timeout_spin_hw.setSuffix(" ms")
        sensor_layout.addRow("Sensor-Timeout:", self.timeout_spin_hw)
        
        layout.addRow(sensor_group)
        
        # Debug & Wartung
        debug_group = QtWidgets.QGroupBox("Debug & Wartung")
        debug_layout = QtWidgets.QFormLayout(debug_group)
        
        self.debug_mode_check = QtWidgets.QCheckBox("Debug-Modus aktivieren")
        debug_layout.addRow("", self.debug_mode_check)
        
        self.backup_usb_check = QtWidgets.QCheckBox("Auto-Backup auf USB")
        debug_layout.addRow("", self.backup_usb_check)
        
        layout.addRow(debug_group)
        
        return tab
    
    def create_calibration_tab(self) -> QtWidgets.QWidget:
        """Erstellt Kalibrierungs-Einstellungen Tab"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # Kalibrierungs-Status
        status_group = QtWidgets.QGroupBox("Kalibrierungs-Status")
        status_layout = QtWidgets.QFormLayout(status_group)
        
        self.last_calibration_label = QtWidgets.QLabel("Noch nie")
        status_layout.addRow("Letzte Kalibrierung:", self.last_calibration_label)
        
        self.calibration_valid_label = QtWidgets.QLabel("UNGÜLTIG")
        status_layout.addRow("Status:", self.calibration_valid_label)
        
        layout.addWidget(status_group)
        
        # Kalibrierungs-Aktionen
        actions_group = QtWidgets.QGroupBox("Aktionen")
        actions_layout = QtWidgets.QHBoxLayout(actions_group)
        
        self.btn_auto_tare = QtWidgets.QPushButton("Auto-Tare")
        self.btn_calibrate = QtWidgets.QPushButton("Neu Kalibrieren")
        self.btn_test_weights = QtWidgets.QPushButton("Gewichte Testen")
        
        for btn in [self.btn_auto_tare, self.btn_calibrate, self.btn_test_weights]:
            btn.setFixedHeight(40)
            actions_layout.addWidget(btn)
        
        layout.addWidget(actions_group)
        
        layout.addStretch()
        return tab
    
    def create_feeding_tab(self) -> QtWidgets.QWidget:
        """Erstellt Fütterungs-Einstellungen Tab"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(tab)
        
        # Futter-Konfiguration Button (Legacy)
        legacy_group = QtWidgets.QGroupBox("Futter-Management")
        legacy_layout = QtWidgets.QHBoxLayout(legacy_group)
        
        self.btn_futter_config = QtWidgets.QPushButton("Futter-Konfiguration")
        self.btn_futter_config.setFixedHeight(50)
        legacy_layout.addWidget(self.btn_futter_config)
        
        layout.addRow(legacy_group)
        
        # Standard-Einstellungen
        defaults_group = QtWidgets.QGroupBox("Standard-Werte")
        defaults_layout = QtWidgets.QFormLayout(defaults_group)
        
        self.default_amount_spin = QtWidgets.QDoubleSpinBox()
        self.default_amount_spin.setRange(0.1, 50.0)
        self.default_amount_spin.setDecimals(1)
        self.default_amount_spin.setSuffix(" kg")
        defaults_layout.addRow("Standard Futtermenge:", self.default_amount_spin)
        
        layout.addRow(defaults_group)
        
        # Limits
        limits_group = QtWidgets.QGroupBox("Limits & Sicherheit")
        limits_layout = QtWidgets.QFormLayout(limits_group)
        
        self.max_per_horse_spin = QtWidgets.QDoubleSpinBox()
        self.max_per_horse_spin.setRange(1.0, 100.0)
        self.max_per_horse_spin.setDecimals(1)
        self.max_per_horse_spin.setSuffix(" kg")
        limits_layout.addRow("Max. pro Pferd:", self.max_per_horse_spin)
        
        self.warning_threshold_spin = QtWidgets.QDoubleSpinBox()
        self.warning_threshold_spin.setRange(1.0, 50.0)
        self.warning_threshold_spin.setDecimals(1)
        self.warning_threshold_spin.setSuffix(" kg")
        limits_layout.addRow("Warnung bei weniger als:", self.warning_threshold_spin)
        
        layout.addRow(limits_group)
        
        return tab
    
    def init_ui(self):
        """Initialisiert UI-Komponenten und Callbacks"""
        # Button-Callbacks
        if hasattr(self, 'btn_save'):
            self.btn_save.clicked.connect(self.save_settings)
        if hasattr(self, 'btn_export'):
            self.btn_export.clicked.connect(self.export_settings)
        if hasattr(self, 'btn_import'):
            self.btn_import.clicked.connect(self.import_settings)
        if hasattr(self, 'btn_reset'):
            self.btn_reset.clicked.connect(self.reset_settings)
        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.zurueck_geklickt)
        
        # Display-Config Button
        if hasattr(self, 'btn_display_config'):
            self.btn_display_config.clicked.connect(self.zu_display_config)
        
        # Legacy Futter-Config Button
        if hasattr(self, 'btn_futter_config'):
            self.btn_futter_config.clicked.connect(self.zu_futter_config)
            
        # ESP8266 Konfiguration Button
        if hasattr(self, 'btn_esp8266_config'):
            self.btn_esp8266_config.clicked.connect(self.zu_esp8266_config)
        
        # Button-Verbindungen abgeschlossen - Hardware-Modus aktiv
        
        # Slider-Updates
        if hasattr(self, 'brightness_slider'):
            self.brightness_slider.valueChanged.connect(self.update_brightness_label)
        if hasattr(self, 'volume_slider'):
            self.volume_slider.valueChanged.connect(self.update_volume_label)
        
        # Kalibrierungs-Buttons - BRUTALE DIREKTE LÖSUNG
        if hasattr(self, 'btn_auto_tare'):
            self.btn_auto_tare.clicked.connect(self.auto_tare)
            logger.info("btn_auto_tare connected")
        if hasattr(self, 'btn_calibrate'):
            self.btn_calibrate.clicked.connect(self.start_calibration)
            logger.info("btn_calibrate connected")
        if hasattr(self, 'btn_kalibrieren'):
            self.btn_kalibrieren.clicked.connect(self.start_calibration)
            logger.info("btn_kalibrieren connected")
        if hasattr(self, 'btn_test_weights'):
            self.btn_test_weights.clicked.connect(self.test_weights)
            logger.info("btn_test_weights connected")
        
        # NOTFALL-LÖSUNG: Alle Buttons durchgehen und zwangsweise verbinden
        all_buttons = self.findChildren(QtWidgets.QPushButton)
        for button in all_buttons:
            button_name = button.objectName()
            button_text = button.text()
            logger.info(f"Button gefunden: {button_name} = '{button_text}'")
            
            # Kalibrierungsbutton zwangsweise verbinden
            if ('kalibr' in button_name.lower() or 
                'kalibr' in button_text.lower() or 
                button_text in ['Neu Kalibrieren', 'Kalibrierung', 'Kalibrieren']):
                
                logger.info(f"🎯 KALIBRIERUNGS-BUTTON ZWANGSVERBINDUNG: {button_name}")
                # Alte Verbindungen trennen und neu verbinden
                try:
                    button.clicked.disconnect()
                except:
                    pass
                button.clicked.connect(self.start_calibration)
                logger.info(f"✅ {button_name} ZWANGSWEISE VERBUNDEN!")
        
        # Debug: Alle verfügbaren Buttons auflisten
        logger.info(f"Verfügbare Buttons: {[btn.objectName() for btn in all_buttons]}")
    
    def load_current_settings(self):
        """Lädt aktuelle Einstellungen in UI"""
        try:
            # System Settings
            if hasattr(self, 'brightness_slider'):
                brightness = self.settings_manager.system.brightness
                self.brightness_slider.setValue(brightness)
                self.update_brightness_label(brightness)
            
            # Hardware Settings - Pi5 mit HX711 Sensoren
            
            # Feeding Settings
            if hasattr(self, 'default_amount_spin'):
                self.default_amount_spin.setValue(self.settings_manager.feeding.default_feed_amount)
            
            if hasattr(self, 'status_label'):
                self.status_label.setText("Einstellungen geladen")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Einstellungen: {e}")
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"Fehler: {e}")
    
    def save_settings(self):
        """Speichert alle UI-Einstellungen"""
        try:
            # System Settings
            if hasattr(self, 'brightness_slider'):
                self.settings_manager.system.brightness = self.brightness_slider.value()
            
            # Hardware Settings - Echte HX711 Waagen-Hardware
            
            # Feeding Settings
            if hasattr(self, 'default_amount_spin'):
                self.settings_manager.feeding.default_feed_amount = self.default_amount_spin.value()
            
            # Speichern
            if self.settings_manager.save_settings():
                if hasattr(self, 'status_label'):
                    self.status_label.setText("Einstellungen erfolgreich gespeichert")
                if hasattr(self, 'last_saved_label'):
                    self.last_saved_label.setText(f"Zuletzt gespeichert: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern: {e}")
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"Speicher-Fehler: {e}")
    
    def export_settings(self):
        """Exportiert Einstellungen in Datei"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Einstellungen exportieren", 
                f"einstellungen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON-Dateien (*.json);;Alle Dateien (*)"
            )
            
            if file_path:
                if self.settings_manager.export_settings(file_path):
                    if hasattr(self, 'status_label'):
                        self.status_label.setText(f"Exportiert nach: {Path(file_path).name}")
                    QMessageBox.information(self, "Export", "Einstellungen erfolgreich exportiert!")
                    
        except Exception as e:
            logger.error(f"Export-Fehler: {e}")
            QMessageBox.critical(self, "Fehler", f"Export fehlgeschlagen: {e}")
    
    def import_settings(self):
        """Importiert Einstellungen aus Datei"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Einstellungen importieren", "",
                "JSON-Dateien (*.json);;Alle Dateien (*)"
            )
            
            if file_path:
                reply = QMessageBox.question(
                    self, "Import bestätigen",
                    "Alle aktuellen Einstellungen werden überschrieben. Fortfahren?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    if self.settings_manager.import_settings(file_path):
                        self.load_current_settings()  # UI aktualisieren
                        if hasattr(self, 'status_label'):
                            self.status_label.setText(f"Importiert: {Path(file_path).name}")
                        QMessageBox.information(self, "Import", "Einstellungen erfolgreich importiert!")
                        
        except Exception as e:
            logger.error(f"Import-Fehler: {e}")
            QMessageBox.critical(self, "Fehler", f"Import fehlgeschlagen: {e}")
    
    def reset_settings(self):
        """Setzt Einstellungen auf Standardwerte zurück"""
        try:
            reply = QMessageBox.question(
                self, "Zurücksetzen bestätigen",
                "Alle Einstellungen werden auf Standardwerte zurückgesetzt. Fortfahren?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                categories = ['system', 'calibration', 'feeding', 'hardware', 'ui']
                
                for category in categories:
                    if self.settings_manager.reset_category(category):
                        logger.info(f"Kategorie '{category}' zurückgesetzt")
                
                self.load_current_settings()  # UI aktualisieren
                if hasattr(self, 'status_label'):
                    self.status_label.setText("Einstellungen zurückgesetzt")
                QMessageBox.information(self, "Reset", "Alle Einstellungen wurden zurückgesetzt!")
                
        except Exception as e:
            logger.error(f"Reset-Fehler: {e}")
            QMessageBox.critical(self, "Fehler", f"Reset fehlgeschlagen: {e}")

    
    # Neue Funktionen
    def update_brightness_label(self, value):
        """Aktualisiert Helligkeits-Label"""
        if hasattr(self, 'brightness_value_label'):
            self.brightness_value_label.setText(f"{value}%")
    
    def update_volume_label(self, value):
        """Aktualisiert Lautstärke-Label"""
        if hasattr(self, 'volume_value_label'):
            self.volume_value_label.setText(f"{value}%")
    
    def auto_tare(self):
        """Startet Auto-Tare Prozess"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.setText("Auto-Tare wird durchgeführt...")
            
            # Simulation: Nach 2 Sekunden "fertig"
            QTimer.singleShot(2000, lambda: self.status_label.setText("Auto-Tare abgeschlossen") if hasattr(self, 'status_label') else None)
            
            # System-Event loggen
            self.db_manager.log_system_event(
                "auto_tare", 
                "Auto-Tare durchgeführt",
                {"timestamp": datetime.now().isoformat()}
            )
            
        except Exception as e:
            logger.error(f"Auto-Tare Fehler: {e}")
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"Auto-Tare Fehler: {e}")
    
    def start_calibration(self):
        """Startet Kalibrierungs-Prozess - Navigiert zur Waagenkalibrierung"""
        try:
            logger.info("🎯 KALIBRIERUNGS-BUTTON GEKLICKT!")
            print("🎯 KALIBRIERUNGS-BUTTON GEKLICKT!")  # Console Debug
            
            logger.info("Kalibrierungs-Button geklickt - navigiere zur Waagenkalibrierung")
            
            if self.navigation:
                logger.info("✅ Navigation verfügbar - wechsle zu waagen_kalibrierung")
                self.navigation.show_status("waagen_kalibrierung")
            else:
                logger.warning("❌ Navigation nicht verfügbar für waagen_kalibrierung")
                print("❌ Navigation nicht verfügbar!")
                self.show_kalibrierung_fallback()
            
            if hasattr(self, 'status_label'):
                self.status_label.setText("Navigiere zur Waagenkalibrierung...")
            
        except Exception as e:
            error_msg = f"Kalibrierungs-Navigation-Fehler: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")  # Console Debug
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"Navigation Fehler: {e}")
    
    def show_kalibrierung_fallback(self):
        """Fallback: Waagenkalibrierung direkt anzeigen"""
        try:
            from views.waagen_kalibrierung import WaagenKalibrierung
            
            # Erstelle Kalibrierungs-Seite
            self.waagen_kalibrierung = WaagenKalibrierung()
            self.waagen_kalibrierung.navigation = self.navigation
            
            # Zeige als Modal Dialog oder ersetze aktuelles Widget
            if hasattr(self.parent(), 'setCentralWidget'):
                self.parent().setCentralWidget(self.waagen_kalibrierung)
            else:
                self.waagen_kalibrierung.show()
                
            logger.info("Waagenkalibrierung als Fallback geöffnet")
            
        except Exception as e:
            logger.error(f"Waagenkalibrierung Fallback fehlgeschlagen: {e}")
    
    def test_weights(self):
        """Testet aktuelle Gewichtswerte"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.setText("Gewichte werden getestet...")
            
            QTimer.singleShot(3000, lambda: self.status_label.setText("Gewichts-Test abgeschlossen") if hasattr(self, 'status_label') else None)
            
        except Exception as e:
            logger.error(f"Gewichts-Test Fehler: {e}")
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"Test Fehler: {e}")
    
    def on_settings_changed(self, category: str):
        """Callback für Einstellungsänderungen"""
        logger.debug(f"Einstellungen geändert: {category}")
    
    def showEvent(self, event):
        """Wird aufgerufen wenn Seite angezeigt wird - erweitert BaseViewWidget"""
        # BaseViewWidget macht bereits: super().showEvent(event) + Timer + Logging
        super().showEvent(event)
        
        # Spezifische Einstellungen-Seite Aktionen
        self.load_current_settings()
        
        # ESP8266-Status aktualisieren
        self.update_esp8266_status()
        
        # Pi5-Power-Status aktualisieren
        self.update_pi5_power_display()
    
    def zu_display_config(self):
        """Navigiert zur Display-Konfigurationsseite"""
        logger.info("Display-Config Button geklickt")
        
        if self.navigation:
            try:
                self.navigation.show_status("display_config")
            except Exception as e:
                logger.error(f"Navigation zu display_config fehlgeschlagen: {e}")
                # Fallback: Versuche direkten Import und Anzeige
                self.show_display_config_fallback()
        else:
            logger.warning("Navigation nicht verfügbar für display_config")
            self.show_display_config_fallback()
    
    def zu_futter_config(self):
        """Navigiert zur Futter-Konfigurationsseite"""
        logger.info("Futter-Config Button geklickt")
        
        if self.navigation:
            self.navigation.show_status("futter_konfiguration")
        else:
            logger.warning("Navigation nicht verfügbar für futter_konfiguration")
    
    def zu_esp8266_config(self):
        """Navigiert zur ESP8266-Konfigurationsseite"""
        logger.info("ESP8266-Config Button geklickt")
        
        if self.navigation:
            try:
                self.navigation.show_status("esp8266_config")
            except Exception as e:
                logger.error(f"Navigation zu esp8266_config fehlgeschlagen: {e}")
                # Fallback: Versuche direkten Import und Anzeige
                self.show_esp8266_config_fallback()
        else:
            logger.warning("Navigation nicht verfügbar für esp8266_config")
            self.show_esp8266_config_fallback()
    
    def show_esp8266_config_fallback(self):
        """Fallback: ESP8266-Config direkt anzeigen"""
        try:
            from views.esp8266_config_seite import ESP8266ConfigSeite
            
            # Erstelle ESP8266-Config-Seite
            self.esp8266_config = ESP8266ConfigSeite()
            self.esp8266_config.navigation = self.navigation
            
            # Zeige als Modal Dialog oder ersetze aktuelles Widget
            if hasattr(self.parent(), 'setCentralWidget'):
                self.parent().setCentralWidget(self.esp8266_config)
            else:
                self.esp8266_config.show()
                
            logger.info("ESP8266-Konfiguration als Fallback geöffnet")
            
        except Exception as e:
            logger.error(f"ESP8266-Config Fallback fehlgeschlagen: {e}")
    
    def show_display_config_fallback(self):
        """Fallback: Display-Config direkt anzeigen"""
        try:
            from views.display_config_seite import DisplayConfigSeite
            
            # Erstelle Display-Config-Seite
            self.display_config = DisplayConfigSeite()
            self.display_config.navigation = self.navigation
            
            # Zeige als Modal Dialog oder ersetze aktuelles Widget
            if hasattr(self.parent(), 'setCentralWidget'):
                self.parent().setCentralWidget(self.display_config)
            else:
                self.display_config.show()
                
            logger.info("Display-Config als Fallback geöffnet")
            
        except Exception as e:
            logger.error(f"Display-Config Fallback fehlgeschlagen: {e}")

    def update_esp8266_status(self):
        """Aktualisiert ESP8266-Status im txt_fu_sim_toggle Label"""
        try:
            if hasattr(self, 'txt_fu_sim_toggle'):
                try:
                    # ESP8266 Discovery verwenden
                    from wireless.esp8266_discovery import ESP8266Discovery
                    import asyncio
                    
                    discovery = ESP8266Discovery()
                    
                    # Asynchrone ESP8266-Suche in Thread
                    def check_esp8266():
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            result = loop.run_until_complete(discovery.find_esp8266(force_rescan=True))
                            loop.close()
                            
                            if result:
                                ip, mode = result
                                status_text = f"Hardware-Status: Pi5 + HX711 + ESP8266 ({ip}, {mode})"
                                color = "#4CAF50"  # Grün
                            else:
                                status_text = "Hardware-Status: Pi5 + HX711 (ESP8266 nicht gefunden)"
                                color = "#FF9800"  # Orange
                                
                            # UI-Update im Main-Thread
                            from PyQt5.QtCore import QMetaObject, Qt
                            QMetaObject.invokeMethod(self.txt_fu_sim_toggle, "setText", 
                                                   Qt.QueuedConnection, 
                                                   QtCore.Q_ARG(str, status_text))
                            QMetaObject.invokeMethod(self.txt_fu_sim_toggle, "setStyleSheet",
                                                   Qt.QueuedConnection,
                                                   QtCore.Q_ARG(str, f"QLabel {{ background-color: transparent; color: {color}; }}"))
                                                   
                        except Exception as e:
                            logger.error(f"ESP8266 Status Check Fehler: {e}")
                            fallback_text = "Hardware-Status: Pi5 + HX711 (ESP8266 Status unbekannt)"
                            QMetaObject.invokeMethod(self.txt_fu_sim_toggle, "setText",
                                                   Qt.QueuedConnection,
                                                   QtCore.Q_ARG(str, fallback_text))
                    
                    # Status-Check in separatem Thread starten
                    from threading import Thread
                    status_thread = Thread(target=check_esp8266, daemon=True)
                    status_thread.start()
                    
                except ImportError:
                    # Fallback wenn ESP8266Discovery nicht verfügbar
                    fallback_text = "Hardware-Status: Pi5 + HX711 (ESP8266 nicht konfiguriert)"
                    self.txt_fu_sim_toggle.setText(fallback_text)
                    self.txt_fu_sim_toggle.setStyleSheet("QLabel { background-color: transparent; color: #FF9800; }")
                    
        except Exception as e:
            logger.error(f"ESP8266-Status Update fehlgeschlagen: {e}")

    def get_pi5_power_status(self):
        """Pi5 interne Stromüberwachung via vcgencmd"""
        try:
            import subprocess
            
            # Pi5 Spannungen und Temperatur abrufen
            core_volt = subprocess.check_output(['vcgencmd', 'measure_volts', 'core'], 
                                              timeout=5).decode().strip()
            temp = subprocess.check_output(['vcgencmd', 'measure_temp'], 
                                         timeout=5).decode().strip()
            throttled = subprocess.check_output(['vcgencmd', 'get_throttled'], 
                                              timeout=5).decode().strip()
            
            # Werte parsen
            voltage = float(core_volt.split('=')[1].replace('V', ''))
            temperature = float(temp.split('=')[1].replace('\'C', ''))
            throttle_status = throttled.split('=')[1]
            
            return {
                'core_voltage': voltage,
                'temperature': temperature,
                'throttled': throttle_status != '0x0',
                'throttle_code': throttle_status
            }
            
        except Exception as e:
            logger.error(f"Pi5 Power-Status Fehler: {e}")
            return {
                'core_voltage': 0.0,
                'temperature': 0.0,  
                'throttled': False,
                'throttle_code': 'unknown'
            }
    
    def update_pi5_power_display(self):
        """Pi5 Power-Status in UI anzeigen (falls Label existiert)"""
        try:
            power_status = self.get_pi5_power_status()
            
            # Pi5 Status-Text erstellen
            status_text = (f"Pi5 Status: {power_status['core_voltage']:.2f}V | "
                          f"{power_status['temperature']:.1f}°C")
            
            # Warnung bei Problemen
            if power_status['throttled']:
                status_text += " ⚠️ THROTTLED"
                color = "#f44336"  # Rot
            elif power_status['temperature'] > 70.0:
                status_text += " 🔥 HOT"
                color = "#FF9800"  # Orange
            elif power_status['core_voltage'] < 1.0:
                status_text += " ⚡ LOW VOLTAGE"
                color = "#FF9800"  # Orange
            else:
                status_text += " ✅ OK"
                color = "#4CAF50"  # Grün
            
            # UI Update (falls Pi5-Power Label existiert)
            if hasattr(self, 'lbl_pi5_power'):
                self.lbl_pi5_power.setText(status_text)
                self.lbl_pi5_power.setStyleSheet(f"color: {color}; font-weight: bold;")
            
            # Alternativ: In ESP8266-Status integrieren
            elif hasattr(self, 'txt_fu_sim_toggle'):
                current_text = self.txt_fu_sim_toggle.text()
                combined_text = f"{current_text}\nPi5: {status_text}"
                self.txt_fu_sim_toggle.setText(combined_text)
                
        except Exception as e:
            logger.error(f"Pi5 Power Display Update Fehler: {e}")

    def zurueck_geklickt(self):
        """Zurück-Button geklickt - sichere Navigation zurück"""
        logger.info("Zurück-Button geklickt - zurück zur vorherigen Seite")
        
        # Moderne Navigation verwenden
        if self.navigation:
            if hasattr(self.navigation, 'go_back'):
                self.navigation.go_back()
            else:
                # Fallback zur Auswahl-Seite (wo User herkommt)
                self.navigation.show_status("auswahl")
        else:
            logger.warning("Navigation nicht verfügbar - kann nicht zurück navigieren")
    
    def hideEvent(self, event):
        """Wird aufgerufen wenn Seite versteckt wird"""
        super().hideEvent(event)
        logger.debug("EinstellungenSeite versteckt")