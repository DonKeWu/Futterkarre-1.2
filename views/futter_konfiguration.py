
import os
import logging
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QComboBox, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from utils.futter_loader import lade_heu_als_dataclasses, lade_heulage_als_dataclasses

logger = logging.getLogger(__name__)


#!/usr/bin/env python3
"""
Futter-Konfiguration - Erweiterte Futter-Daten Verwaltung
Verbesserte Benutzeroberfläche für Futter-Management

Features:
- CSV-Dateien verwalten und laden
- Futter-Parameter einstellen
- Live-Vorschau der Daten
- Integration mit SettingsManager
- Persistent Settings
"""

import sys
import os
import logging
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtWidgets import QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import pyqtSignal, QTimer
from datetime import datetime

# Projekt-spezifische Imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.futter_loader import load_futter_data, get_available_files
from utils.settings_manager import get_settings_manager
from utils.database_manager import get_database_manager
from utils.timer_manager import get_timer_manager

logger = logging.getLogger(__name__)

class FutterKonfiguration(QtWidgets.QWidget):
    """
    Erweiterte Futter-Konfiguration mit persistenten Einstellungen
    
    Funktionen:
    - CSV-Datei Auswahl und Verwaltung
    - Futter-Daten Vorschau
    - Standard-Parameter konfigurieren
    - Integration mit MainWindow
    """
    
    # Signale
    futter_daten_gewaehlt = pyqtSignal(str, dict)  # file_name, data
    konfiguration_geaendert = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Manager Instanzen
        self.settings_manager = get_settings_manager()
        self.db_manager = get_database_manager()
        self.timer_manager = get_timer_manager()
        
        # Daten
        self.verfuegbare_dateien = []
        self.aktuelle_daten = {}
        self.gewahlte_datei = ""
        
        # Navigation (für Kompatibilität)
        self.navigation = None
        
        # UI laden
        self.ui_file = Path(__file__).parent / "futter_konfiguration.ui"
        if self.ui_file.exists():
            uic.loadUi(str(self.ui_file), self)
            self.setup_existing_ui()
        else:
            self.init_manual_ui()
        
        # Vollbild für PiTouch2
        self.setFixedSize(1280, 720)
        self.move(0, 0)
        
        # UI initialisieren
        self.init_ui()
        self.lade_verfuegbare_dateien()
        self.load_saved_configuration()
        
        logger.info("FutterKonfiguration initialisiert")
    
    def setup_existing_ui(self):
        """Setup für bestehende UI-Komponenten"""
        # Bestehende UI erweitern falls möglich
        pass
    
    def init_manual_ui(self):
        """Manueller UI-Aufbau falls .ui-Datei fehlt"""
        self.setObjectName("FutterKonfiguration")
        self.resize(1280, 720)
        
        # Haupt-Layout
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Header
        header_layout = QtWidgets.QHBoxLayout()
        
        title_label = QtWidgets.QLabel("Futter-Konfiguration")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Header Buttons
        self.btn_refresh = QtWidgets.QPushButton("Aktualisieren")
        self.btn_save_config = QtWidgets.QPushButton("Speichern")
        self.btn_anwenden = QtWidgets.QPushButton("Anwenden")
        self.btn_zurueck = QtWidgets.QPushButton("Zurück")
        
        for btn in [self.btn_refresh, self.btn_save_config, self.btn_anwenden, self.btn_zurueck]:
            btn.setFixedSize(120, 40)
            header_layout.addWidget(btn)
        
        main_layout.addLayout(header_layout)
        
        # Content Area
        content_layout = QtWidgets.QHBoxLayout()
        
        # Linke Seite: Datei-Auswahl und Einstellungen
        left_panel = QtWidgets.QVBoxLayout()
        
        # Datei-Auswahl
        file_group = QtWidgets.QGroupBox("CSV-Datei Auswahl")
        file_layout = QtWidgets.QVBoxLayout(file_group)
        
        self.combo_dateien = QtWidgets.QComboBox()
        self.combo_dateien.setMinimumHeight(40)
        file_layout.addWidget(QtWidgets.QLabel("Verfügbare Futter-Dateien:"))
        file_layout.addWidget(self.combo_dateien)
        
        # Info zur gewählten Datei
        self.label_datei_info = QtWidgets.QLabel("Keine Datei gewählt")
        self.label_datei_info.setStyleSheet("color: gray; margin: 5px;")
        file_layout.addWidget(self.label_datei_info)
        
        left_panel.addWidget(file_group)
        
        # Futter-Parameter
        params_group = QtWidgets.QGroupBox("Futter-Parameter")
        params_layout = QtWidgets.QFormLayout(params_group)
        
        self.spin_standard_menge = QtWidgets.QDoubleSpinBox()
        self.spin_standard_menge.setRange(0.1, 50.0)
        self.spin_standard_menge.setDecimals(1)
        self.spin_standard_menge.setSuffix(" kg")
        params_layout.addRow("Standard-Menge:", self.spin_standard_menge)
        
        self.spin_max_menge = QtWidgets.QDoubleSpinBox()
        self.spin_max_menge.setRange(1.0, 100.0)
        self.spin_max_menge.setDecimals(1)
        self.spin_max_menge.setSuffix(" kg")
        params_layout.addRow("Max. Menge pro Pferd:", self.spin_max_menge)
        
        self.check_auto_apply = QtWidgets.QCheckBox("Automatisch anwenden")
        self.check_auto_apply.setChecked(True)
        params_layout.addRow("", self.check_auto_apply)
        
        left_panel.addWidget(params_group)
        
        # Status und Statistiken
        stats_group = QtWidgets.QGroupBox("Statistiken")
        stats_layout = QtWidgets.QFormLayout(stats_group)
        
        self.label_anzahl_eintraege = QtWidgets.QLabel("0")
        stats_layout.addRow("Anzahl Einträge:", self.label_anzahl_eintraege)
        
        self.label_letzte_aenderung = QtWidgets.QLabel("Noch nie")
        stats_layout.addRow("Letzte Änderung:", self.label_letzte_aenderung)
        
        left_panel.addWidget(stats_group)
        
        left_panel.addStretch()
        
        # Linke Panel in Widget wrappen
        left_widget = QtWidgets.QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setFixedWidth(400)
        
        content_layout.addWidget(left_widget)
        
        # Rechte Seite: Daten-Vorschau
        right_panel = QtWidgets.QVBoxLayout()
        
        preview_group = QtWidgets.QGroupBox("Daten-Vorschau")
        preview_layout = QtWidgets.QVBoxLayout(preview_group)
        
        # Vorschau-Tabelle
        self.table_vorschau = QTableWidget()
        self.table_vorschau.setAlternatingRowColors(True)
        self.table_vorschau.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_vorschau.horizontalHeader().setStretchLastSection(True)
        preview_layout.addWidget(self.table_vorschau)
        
        # Vorschau-Statistiken
        preview_stats_layout = QtWidgets.QHBoxLayout()
        
        self.label_zeilen_gesamt = QtWidgets.QLabel("Zeilen: 0")
        self.label_spalten_gesamt = QtWidgets.QLabel("Spalten: 0")
        self.label_datei_groesse = QtWidgets.QLabel("Größe: 0 KB")
        
        preview_stats_layout.addWidget(self.label_zeilen_gesamt)
        preview_stats_layout.addWidget(self.label_spalten_gesamt)
        preview_stats_layout.addWidget(self.label_datei_groesse)
        preview_stats_layout.addStretch()
        
        preview_layout.addLayout(preview_stats_layout)
        
        right_panel.addWidget(preview_group)
        
        content_layout.addLayout(right_panel)
        
        main_layout.addLayout(content_layout)
        
        # Status Bar
        status_layout = QtWidgets.QHBoxLayout()
        self.status_label = QtWidgets.QLabel("Bereit")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.label_current_file = QtWidgets.QLabel("Keine Datei aktiv")
        status_layout.addWidget(self.label_current_file)
        
        main_layout.addLayout(status_layout)
    
    def init_ui(self):
        """Initialisiert UI-Komponenten und Events"""
        # Button Events
        if hasattr(self, 'btn_refresh'):
            self.btn_refresh.clicked.connect(self.lade_verfuegbare_dateien)
        if hasattr(self, 'btn_save_config'):
            self.btn_save_config.clicked.connect(self.save_configuration)
        if hasattr(self, 'btn_anwenden'):
            self.btn_anwenden.clicked.connect(self.anwenden_geklickt)
        if hasattr(self, 'btn_zurueck'):
            self.btn_zurueck.clicked.connect(self.zurueck_geklickt)
        
        # ComboBox Events
        if hasattr(self, 'combo_dateien'):
            self.combo_dateien.currentTextChanged.connect(self.datei_gewaehlt)
        
        # Parameter Events
        if hasattr(self, 'spin_standard_menge'):
            self.spin_standard_menge.valueChanged.connect(self.parameter_geaendert)
        if hasattr(self, 'spin_max_menge'):
            self.spin_max_menge.valueChanged.connect(self.parameter_geaendert)
        
        # Auto-Apply
        if hasattr(self, 'check_auto_apply'):
            self.check_auto_apply.stateChanged.connect(self.auto_apply_changed)
    
    def lade_verfuegbare_dateien(self):
        """Lädt verfügbare CSV-Dateien"""
        try:
            self.verfuegbare_dateien = get_available_files()
            
            if hasattr(self, 'combo_dateien'):
                self.combo_dateien.clear()
                self.combo_dateien.addItem("-- Datei auswählen --")
                
                for datei in self.verfuegbare_dateien:
                    self.combo_dateien.addItem(datei)
            
            self.status_label.setText(f"Verfügbare Dateien geladen: {len(self.verfuegbare_dateien)}")
            logger.info(f"Verfügbare Futter-Dateien geladen: {self.verfuegbare_dateien}")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der verfügbaren Dateien: {e}")
            self.status_label.setText(f"Fehler: {e}")
    
    def datei_gewaehlt(self, datei_name: str):
        """Wird aufgerufen wenn eine Datei gewählt wird"""
        if datei_name == "-- Datei auswählen --" or not datei_name:
            self.clear_preview()
            return
        
        try:
            self.gewahlte_datei = datei_name
            self.aktuelle_daten = load_futter_data(datei_name)
            
            # Datei-Info aktualisieren
            if hasattr(self, 'label_datei_info'):
                datei_path = Path("data") / datei_name
                if datei_path.exists():
                    stat = datei_path.stat()
                    info_text = f"Größe: {stat.st_size // 1024} KB, Geändert: {datetime.fromtimestamp(stat.st_mtime).strftime('%d.%m.%Y %H:%M')}"
                    self.label_datei_info.setText(info_text)
                    
                    if hasattr(self, 'label_datei_groesse'):
                        self.label_datei_groesse.setText(f"Größe: {stat.st_size // 1024} KB")
            
            # Vorschau aktualisieren
            self.update_preview()
            
            # Auto-Apply wenn aktiviert
            if hasattr(self, 'check_auto_apply') and self.check_auto_apply.isChecked():
                self.anwenden_geklickt()
            
            self.status_label.setText(f"Datei geladen: {datei_name}")
            
            if hasattr(self, 'label_current_file'):
                self.label_current_file.setText(f"Aktiv: {datei_name}")
            
            logger.info(f"Futter-Datei gewählt: {datei_name}")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Datei {datei_name}: {e}")
            self.status_label.setText(f"Fehler beim Laden: {e}")
            QMessageBox.critical(self, "Fehler", f"Datei konnte nicht geladen werden:\n{e}")
    
    def update_preview(self):
        """Aktualisiert die Daten-Vorschau"""
        if not self.aktuelle_daten or not hasattr(self, 'table_vorschau'):
            return
        
        try:
            table = self.table_vorschau
            
            # Tabelle konfigurieren
            if self.aktuelle_daten:
                first_entry = next(iter(self.aktuelle_daten.values()))
                spalten = list(first_entry.keys())
                
                table.setColumnCount(len(spalten))
                table.setRowCount(len(self.aktuelle_daten))
                table.setHorizontalHeaderLabels(spalten)
                
                # Daten einfügen
                for row, (name, data) in enumerate(self.aktuelle_daten.items()):
                    table.setVerticalHeaderItem(row, QTableWidgetItem(name))
                    
                    for col, spalte in enumerate(spalten):
                        wert = data.get(spalte, "")
                        item = QTableWidgetItem(str(wert))
                        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Nur lesen
                        table.setItem(row, col, item)
                
                # Header anpassen
                header = table.horizontalHeader()
                header.setSectionResizeMode(QHeaderView.Stretch)
                
                # Statistiken aktualisieren
                if hasattr(self, 'label_zeilen_gesamt'):
                    self.label_zeilen_gesamt.setText(f"Zeilen: {len(self.aktuelle_daten)}")
                if hasattr(self, 'label_spalten_gesamt'):
                    self.label_spalten_gesamt.setText(f"Spalten: {len(spalten)}")
                if hasattr(self, 'label_anzahl_eintraege'):
                    self.label_anzahl_eintraege.setText(str(len(self.aktuelle_daten)))
            
            logger.debug(f"Vorschau aktualisiert: {len(self.aktuelle_daten)} Einträge")
            
        except Exception as e:
            logger.error(f"Fehler bei Vorschau-Update: {e}")
    
    def clear_preview(self):
        """Löscht die Vorschau"""
        if hasattr(self, 'table_vorschau'):
            self.table_vorschau.clear()
            self.table_vorschau.setRowCount(0)
            self.table_vorschau.setColumnCount(0)
        
        if hasattr(self, 'label_zeilen_gesamt'):
            self.label_zeilen_gesamt.setText("Zeilen: 0")
        if hasattr(self, 'label_spalten_gesamt'):
            self.label_spalten_gesamt.setText("Spalten: 0")
        if hasattr(self, 'label_anzahl_eintraege'):
            self.label_anzahl_eintraege.setText("0")
        if hasattr(self, 'label_datei_info'):
            self.label_datei_info.setText("Keine Datei gewählt")
        if hasattr(self, 'label_current_file'):
            self.label_current_file.setText("Keine Datei aktiv")
    
    def anwenden_geklickt(self):
        """Wendet die gewählte Konfiguration an"""
        if not self.gewahlte_datei or not self.aktuelle_daten:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie zuerst eine Datei aus!")
            return
        
        try:
            # Signal senden für MainWindow Integration
            self.futter_daten_gewaehlt.emit(self.gewahlte_datei, self.aktuelle_daten)
            
            # Konfiguration speichern
            self.save_configuration()
            
            # Navigation zurück wenn gewünscht
            if self.navigation:
                self.status_label.setText("Konfiguration angewendet - Navigation zurück...")
                QTimer.singleShot(1500, self.zurueck_geklickt)
            else:
                self.status_label.setText("Konfiguration erfolgreich angewendet!")
            
            # Event loggen
            self.db_manager.log_system_event(
                "futter_config",
                f"Futter-Konfiguration angewendet: {self.gewahlte_datei}",
                {
                    "file": self.gewahlte_datei,
                    "entries": len(self.aktuelle_daten),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Futter-Konfiguration angewendet: {self.gewahlte_datei}")
            
        except Exception as e:
            logger.error(f"Fehler beim Anwenden der Konfiguration: {e}")
            self.status_label.setText(f"Fehler: {e}")
            QMessageBox.critical(self, "Fehler", f"Konfiguration konnte nicht angewendet werden:\n{e}")
    
    def save_configuration(self):
        """Speichert die aktuelle Konfiguration persistent"""
        try:
            # Standard-Werte in Settings speichern
            if hasattr(self, 'spin_standard_menge'):
                self.settings_manager.feeding.default_feed_amount = self.spin_standard_menge.value()
            
            if hasattr(self, 'spin_max_menge'):
                self.settings_manager.feeding.max_feed_per_horse = self.spin_max_menge.value()
            
            # Aktuelle Datei speichern
            self.settings_manager.set_setting('feeding', 'last_feed_file', self.gewahlte_datei, save=False)
            
            # Auto-Apply Einstellung
            if hasattr(self, 'check_auto_apply'):
                self.settings_manager.set_setting('feeding', 'auto_apply_config', self.check_auto_apply.isChecked(), save=False)
            
            # Alles speichern
            if self.settings_manager.save_settings():
                if hasattr(self, 'label_letzte_aenderung'):
                    self.label_letzte_aenderung.setText(datetime.now().strftime('%d.%m.%Y %H:%M'))
                
                logger.info("Futter-Konfiguration gespeichert")
                return True
            else:
                logger.error("Fehler beim Speichern der Konfiguration")
                return False
                
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konfiguration: {e}")
            return False
    
    def load_saved_configuration(self):
        """Lädt gespeicherte Konfiguration"""
        try:
            # Standard-Werte laden
            if hasattr(self, 'spin_standard_menge'):
                self.spin_standard_menge.setValue(self.settings_manager.feeding.default_feed_amount)
            
            if hasattr(self, 'spin_max_menge'):
                self.spin_max_menge.setValue(self.settings_manager.feeding.max_feed_per_horse)
            
            # Letzte Datei laden
            last_file = self.settings_manager.get_setting('feeding', 'last_feed_file', '')
            if last_file and hasattr(self, 'combo_dateien'):
                index = self.combo_dateien.findText(last_file)
                if index >= 0:
                    self.combo_dateien.setCurrentIndex(index)
            
            # Auto-Apply laden
            auto_apply = self.settings_manager.get_setting('feeding', 'auto_apply_config', True)
            if hasattr(self, 'check_auto_apply'):
                self.check_auto_apply.setChecked(auto_apply)
            
            logger.debug("Gespeicherte Konfiguration geladen")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der gespeicherten Konfiguration: {e}")
    
    def parameter_geaendert(self):
        """Wird aufgerufen wenn Parameter geändert werden"""
        self.konfiguration_geaendert.emit()
        
        # Auto-Save wenn gewünscht
        if hasattr(self, 'check_auto_apply') and self.check_auto_apply.isChecked():
            self.save_configuration()
    
    def auto_apply_changed(self, state):
        """Auto-Apply Einstellung geändert"""
        self.save_configuration()
    
    def zurueck_geklickt(self):
        """Navigation zurück"""
        logger.info("Zurück-Button geklickt")
        if self.navigation:
            self.navigation.go_back()
        else:
            logger.warning("Navigation nicht verfügbar!")
    
    # Kompatibilität mit alter Schnittstelle
    def futter_daten_laden(self, datei_name: str):
        """Legacy Funktion für Kompatibilität"""
        if hasattr(self, 'combo_dateien'):
            index = self.combo_dateien.findText(datei_name)
            if index >= 0:
                self.combo_dateien.setCurrentIndex(index)
        return self.aktuelle_daten
    
    def get_futter_daten(self):
        """Legacy Funktion - gibt aktuelle Daten zurück"""
        return self.aktuelle_daten
    
    def get_gewahlte_datei(self):
        """Legacy Funktion - gibt gewählte Datei zurück"""
        return self.gewahlte_datei
    
    def showEvent(self, event):
        """Wird aufgerufen wenn Seite angezeigt wird"""
        super().showEvent(event)
        
        # Timer für diese Seite registrieren
        self.timer_manager.set_active_page("futter_konfiguration")
        
        # Daten aktualisieren
        self.lade_verfuegbare_dateien()
        self.load_saved_configuration()
        
        logger.debug("FutterKonfiguration angezeigt")
    
    def hideEvent(self, event):
        """Wird aufgerufen wenn Seite versteckt wird"""
        super().hideEvent(event)
        
        # Konfiguration beim Verlassen speichern
        self.save_configuration()
        
        logger.debug("FutterKonfiguration versteckt")

    def load_ui_or_fallback(self):
        """Lädt UI-Datei oder erstellt Fallback"""
        ui_path = os.path.join(os.path.dirname(__file__), "futter_konfiguration.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
            logger.info("futter_konfiguration.ui erfolgreich geladen")
        else:
            logger.warning("futter_konfiguration.ui nicht gefunden - verwende Fallback")
            self.init_ui()  # Fallback auf Code-basierte UI

    def connect_buttons(self):
        """Verbindet Buttons aus der UI"""
        # ComboBox-Signale verbinden
        if hasattr(self, 'combo_heu'):
            self.combo_heu.currentTextChanged.connect(self.heu_gewaehlt)
        if hasattr(self, 'combo_heulage'):
            self.combo_heulage.currentTextChanged.connect(self.heulage_gewaehlt)
        if hasattr(self, 'combo_pellets'):
            self.combo_pellets.currentTextChanged.connect(self.pellets_gewaehlt)

        # Button-Signale verbinden
        if hasattr(self, 'btn_laden'):
            self.btn_laden.clicked.connect(self.futter_daten_laden)
        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.zurueck_geklickt)

    def init_ui(self):
        """Erstellt die Konfigurationsoberfläche"""
        layout = QVBoxLayout()

        # Titel
        title = QLabel("Futter-Konfiguration")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)

        # Heu-Auswahl
        heu_layout = QHBoxLayout()
        heu_layout.addWidget(QLabel("Heu-Sorte:"))
        self.combo_heu = QComboBox()
        self.combo_heu.currentTextChanged.connect(self.heu_gewaehlt)
        heu_layout.addWidget(self.combo_heu)
        layout.addLayout(heu_layout)

        # Heulage-Auswahl
        heulage_layout = QHBoxLayout()
        heulage_layout.addWidget(QLabel("Heulage-Sorte:"))
        self.combo_heulage = QComboBox()
        self.combo_heulage.currentTextChanged.connect(self.heulage_gewaehlt)
        heulage_layout.addWidget(self.combo_heulage)
        layout.addLayout(heulage_layout)

        # Pellet-Auswahl
        pellet_layout = QHBoxLayout()
        pellet_layout.addWidget(QLabel("Pellet-Sorte:"))
        self.combo_pellets = QComboBox()
        self.combo_pellets.currentTextChanged.connect(self.pellets_gewaehlt)
        pellet_layout.addWidget(self.combo_pellets)
        layout.addLayout(pellet_layout)

        # Status-Anzeige
        self.label_status = QLabel("Keine Futter-Daten geladen")
        layout.addWidget(self.label_status)

        # Buttons
        button_layout = QHBoxLayout()
        self.btn_laden = QPushButton("Futter-Daten laden")
        self.btn_laden.clicked.connect(self.futter_daten_laden)
        self.btn_zurueck = QPushButton("Zurück")
        self.btn_zurueck.clicked.connect(self.zurueck_geklickt)

        button_layout.addWidget(self.btn_laden)
        button_layout.addWidget(self.btn_zurueck)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def lade_verfuegbare_dateien(self):
        """Scannt data/ Ordner nach verfügbaren CSV-Dateien"""
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

        if os.path.exists(data_dir):
            for datei in os.listdir(data_dir):
                if datei.endswith('.csv'):
                    if 'heu' in datei.lower() and 'heulage' not in datei.lower():
                        self.verfuegbare_heu_dateien.append(datei)
                        self.combo_heu.addItem(datei)
                    elif 'heulage' in datei.lower():
                        self.verfuegbare_heulage_dateien.append(datei)
                        self.combo_heulage.addItem(datei)
                    elif 'pellet' in datei.lower():
                        self.verfuegbare_pellet_dateien.append(datei)
                        self.combo_pellets.addItem(datei)

        logger.info(f"Verfügbare Dateien: {len(self.verfuegbare_heu_dateien)} Heu, "
                    f"{len(self.verfuegbare_heulage_dateien)} Heulage, "
                    f"{len(self.verfuegbare_pellet_dateien)} Pellets")

    def heu_gewaehlt(self, dateiname):
        """Wird aufgerufen wenn Heu-Datei gewählt wird"""
        if dateiname:
            logger.info(f"Heu-Datei gewählt: {dateiname}")

    def heulage_gewaehlt(self, dateiname):
        """Wird aufgerufen wenn Heulage-Datei gewählt wird"""
        if dateiname:
            logger.info(f"Heulage-Datei gewählt: {dateiname}")

    def pellets_gewaehlt(self, dateiname):
        """Wird aufgerufen wenn Pellet-Datei gewählt wird"""
        if dateiname:
            logger.info(f"Pellet-Datei gewählt: {dateiname}")

    def futter_daten_laden(self):
        """Lädt die ausgewählten Futter-Daten"""
        try:
            # Heu laden
            heu_datei = self.combo_heu.currentText()
            if heu_datei:
                self.aktuelles_heu = lade_heu_als_dataclasses(heu_datei)
                logger.info(f"{len(self.aktuelles_heu)} Heu-Einträge aus {heu_datei} geladen")

            # Heulage laden
            heulage_datei = self.combo_heulage.currentText()
            if heulage_datei:
                self.aktuelle_heulage = lade_heulage_als_dataclasses(heulage_datei)
                logger.info(f"{len(self.aktuelle_heulage)} Heulage-Einträge aus {heulage_datei} geladen")

            # Status aktualisieren
            self.label_status.setText(f"Geladen: {heu_datei}, {heulage_datei}")

            # Daten an MainWindow weitergeben
            if self.navigation:
                self.navigation.set_futter_daten(
                    heu_liste=self.aktuelles_heu,
                    heulage_liste=self.aktuelle_heulage,
                    pellet_liste=[]  # Später implementieren
                )

        except Exception as e:
            logger.error(f"Fehler beim Laden der Futter-Daten: {e}")
            self.label_status.setText(f"Fehler: {e}")

    def zurueck_geklickt(self):
        """Zurück zur Einstellungen"""
        if self.navigation:
            self.navigation.go_back()
