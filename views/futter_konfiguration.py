
import os
import logging
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QComboBox, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from utils.futter_loader import lade_heu_als_dataclasses, lade_heulage_als_dataclasses

logger = logging.getLogger(__name__)


class FutterKonfiguration(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.navigation = None

        # Verfügbare Futter-Dateien
        self.verfuegbare_heu_dateien = []
        self.verfuegbare_heulage_dateien = []
        self.verfuegbare_pellet_dateien = []

        # Aktuell ausgewählte Futter
        self.aktuelles_heu = None
        self.aktuelle_heulage = None
        self.aktuelle_pellets = None

        # UI AUS DATEI LADEN (statt init_ui)
        self.load_ui_or_fallback()
        
        # Vollbild für PiTouch2 (1280x720) - komplette Display-Nutzung
        self.setFixedSize(1280, 720)
        
        # Position: oben links (0,0) - Display vollständig nutzen
        self.move(0, 0)
        
        self.lade_verfuegbare_dateien()
        self.connect_buttons()

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
