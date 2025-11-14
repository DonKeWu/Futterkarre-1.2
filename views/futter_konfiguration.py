#!/usr/bin/env python3
"""
Futter-Konfiguration - MINIMAL VERSION
NUR Original UI-Datei laden - KEINE programmatische UI-Erstellung!
"""

import os
import logging
from pathlib import Path
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal

logger = logging.getLogger(__name__)

class FutterKonfiguration(QtWidgets.QWidget):
    """
    Minimal Futter-Konfiguration - verwendet NUR die Original UI-Datei
    
    KEINE programmatische UI-Erstellung mehr!
    Alle Formatierungen kommen aus der UI-Datei und dem Theme-System
    """
    
    # Signale
    futter_daten_gewaehlt = pyqtSignal(str, dict)
    konfiguration_geaendert = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Navigation (für Kompatibilität)
        self.navigation = None
        
        # Daten-Speicher
        self.verfuegbare_dateien = []
        self.aktuelle_daten = {}
        self.gewahlte_datei = ""
        
        # NUR UI-Datei laden - KEIN programmatisches UI!
        self.ui_file = Path(__file__).parent / "futter_konfiguration.ui"
        if self.ui_file.exists():
            uic.loadUi(str(self.ui_file), self)
            logger.info("Original UI-Datei geladen - Original Design erhalten")
        else:
            logger.error("futter_konfiguration.ui nicht gefunden!")
            raise FileNotFoundError("UI-Datei fehlt!")
        
        # Vollbild für PiTouch2
        self.setFixedSize(1280, 720)
        self.move(0, 0)
        
        # Button-Verbindungen für Original UI
        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.zurueck_geklickt)
        if hasattr(self, 'btn_laden'):
            self.btn_laden.clicked.connect(self.futter_daten_laden)
        if hasattr(self, 'btn_aktualisieren'):
            self.btn_aktualisieren.clicked.connect(self.lade_verfuegbare_dateien)
            
        # ComboBox-Verbindungen für Original UI
        if hasattr(self, 'combo_heu'):
            self.combo_heu.currentTextChanged.connect(self.heu_gewaehlt)
        if hasattr(self, 'combo_heulage'):
            self.combo_heulage.currentTextChanged.connect(self.heulage_gewaehlt)
        if hasattr(self, 'combo_pellets'):
            self.combo_pellets.currentTextChanged.connect(self.pellets_gewaehlt)
        if hasattr(self, 'combo_hafer'):
            self.combo_hafer.currentTextChanged.connect(self.hafer_gewaehlt)
        
        # Daten laden
        self.lade_verfuegbare_dateien()
        
        logger.info("Minimal FutterKonfiguration initialisiert - Original UI erhalten")
    
    def set_navigation(self, navigation):
        """Navigation setzen"""
        self.navigation = navigation
    
    def lade_verfuegbare_dateien(self):
        """Lädt verfügbare CSV-Dateien"""
        try:
            # Einfache Dateierkennung
            data_dir = Path(__file__).parent.parent / "data"
            if not data_dir.exists():
                logger.warning(f"Data-Verzeichnis nicht gefunden: {data_dir}")
                return
                
            csv_files = list(data_dir.glob("*.csv"))
            self.verfuegbare_dateien = [f.name for f in csv_files]
            
            # ComboBoxen füllen
            for combo_name in ['combo_heu', 'combo_heulage', 'combo_pellets', 'combo_hafer']:
                if hasattr(self, combo_name):
                    combo = getattr(self, combo_name)
                    combo.clear()
                    combo.addItem("-- Datei auswählen --")
                    for datei in self.verfuegbare_dateien:
                        combo.addItem(datei)
            
            # Status aktualisieren
            if hasattr(self, 'label_status'):
                self.label_status.setText(f"{len(self.verfuegbare_dateien)} Dateien gefunden")
            
            logger.info(f"Verfügbare Dateien: {self.verfuegbare_dateien}")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Dateien: {e}")
            if hasattr(self, 'label_status'):
                self.label_status.setText("Fehler beim Laden")
    
    def heu_gewaehlt(self, dateiname):
        """Heu-Datei gewählt"""
        if dateiname != "-- Datei auswählen --":
            logger.info(f"Heu gewählt: {dateiname}")
            if hasattr(self, 'label_info'):
                self.label_info.setText(f"Heu: {dateiname}")
    
    def heulage_gewaehlt(self, dateiname):
        """Heulage-Datei gewählt"""
        if dateiname != "-- Datei auswählen --":
            logger.info(f"Heulage gewählt: {dateiname}")
            if hasattr(self, 'label_info'):
                self.label_info.setText(f"Heulage: {dateiname}")
    
    def pellets_gewaehlt(self, dateiname):
        """Pellets-Datei gewählt"""
        if dateiname != "-- Datei auswählen --":
            logger.info(f"Pellets gewählt: {dateiname}")
            if hasattr(self, 'label_info'):
                self.label_info.setText(f"Pellets: {dateiname}")
    
    def hafer_gewaehlt(self, dateiname):
        """Hafer-Datei gewählt"""
        if dateiname != "-- Datei auswählen --":
            logger.info(f"Hafer gewählt: {dateiname}")
            if hasattr(self, 'label_info'):
                self.label_info.setText(f"Hafer: {dateiname}")
    
    def futter_daten_laden(self):
        """Futter-Daten laden"""
        try:
            # Einfaches Feedback
            if hasattr(self, 'label_status'):
                self.label_status.setText("Daten geladen")
            logger.info("Futter-Daten laden durchgeführt")
        except Exception as e:
            logger.error(f"Fehler beim Laden der Futter-Daten: {e}")
            if hasattr(self, 'label_status'):
                self.label_status.setText("Fehler beim Laden")
    
    def zurueck_geklickt(self):
        """Navigation zurück"""
        if self.navigation:
            self.navigation.show_status("einstellungen")
        else:
            logger.warning("Navigation nicht verfügbar")
    
    def showEvent(self, event):
        """Wird aufgerufen wenn Seite angezeigt wird"""
        super().showEvent(event)
        self.lade_verfuegbare_dateien()
        logger.debug("FutterKonfiguration angezeigt")
    
    def hideEvent(self, event):
        """Wird aufgerufen wenn Seite versteckt wird"""
        super().hideEvent(event)
        logger.debug("FutterKonfiguration versteckt")