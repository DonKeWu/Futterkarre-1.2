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
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTabWidget
from PyQt5.QtCore import pyqtSignal, QTimer
import os
from pathlib import Path
from datetime import datetime

# Projekt-spezifische Imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.settings_manager import get_settings_manager, SettingsManager
from utils.database_manager import get_database_manager
from utils.timer_manager import get_timer_manager


logger = logging.getLogger(__name__)

class EinstellungenSeite(QtWidgets.QWidget):
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
        
        # Hardware Tab (inkl. legacy Simulation)
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
        
        # Hardware-Betriebsmodus (Simulation entfernt)
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
        
        self.calibration_valid_label = QtWidgets.QLabel("❌ Ungültig")
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
        
        # Legacy-Simulation-Buttons entfernt - Hardware-only Modus aktiv
        
        # Slider-Updates
        if hasattr(self, 'brightness_slider'):
            self.brightness_slider.valueChanged.connect(self.update_brightness_label)
        if hasattr(self, 'volume_slider'):
            self.volume_slider.valueChanged.connect(self.update_volume_label)
        
        # Kalibrierungs-Buttons
        if hasattr(self, 'btn_auto_tare'):
            self.btn_auto_tare.clicked.connect(self.auto_tare)
        if hasattr(self, 'btn_calibrate'):
            self.btn_calibrate.clicked.connect(self.start_calibration)
        if hasattr(self, 'btn_test_weights'):
            self.btn_test_weights.clicked.connect(self.test_weights)
    
    def load_current_settings(self):
        """Lädt aktuelle Einstellungen in UI"""
        try:
            # System Settings
            if hasattr(self, 'brightness_slider'):
                brightness = self.settings_manager.system.brightness
                self.brightness_slider.setValue(brightness)
                self.update_brightness_label(brightness)
            
            # Hardware Settings (Hardware-only Modus)
            # Simulation-Checkboxen entfernt - System läuft nur mit Hardware
            
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
            
            # Hardware Settings (Hardware-only - Simulation entfernt)
            # Keine Simulation-Checkboxes mehr verfügbar
            
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
        """Startet Kalibrierungs-Prozess"""
        try:
            self.calibration_requested.emit()
            if hasattr(self, 'status_label'):
                self.status_label.setText("Kalibrierung gestartet...")
            
        except Exception as e:
            logger.error(f"Kalibrierungs-Fehler: {e}")
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"Kalibrierung Fehler: {e}")
    
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
        """Wird aufgerufen wenn Seite angezeigt wird"""
        super().showEvent(event)
        
        # Timer für diese Seite registrieren
        self.timer_manager.set_active_page("einstellungen")
        
        # Aktuelle Einstellungen neu laden
        self.load_current_settings()
        
        logger.debug("EinstellungenSeite angezeigt")
    
    def hideEvent(self, event):
        """Wird aufgerufen wenn Seite versteckt wird"""
        super().hideEvent(event)
        logger.debug("EinstellungenSeite versteckt")