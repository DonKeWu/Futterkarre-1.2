# views/start.py
import os
import views.icons.icons_rc
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class StartSeite(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.navigation = None  # Wird von MainWindow gesetzt

        # Ermittle den absoluten Pfad zur start.ui relativ zu diesem Skript
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, 'start.ui')
        uic.loadUi(ui_path, self)

        # Vollbild für PiTouch2 (1280x720) - komplette Display-Nutzung
        self.setFixedSize(1280, 720)
        
        # Position: oben links (0,0) - Display vollständig nutzen
        self.move(0, 0)

        # Button verbinden
        self.btn_start.clicked.connect(self.zu_auswahl)
        
        # Version anzeigen
        self.load_and_display_version()

    def load_and_display_version(self):
        """Lädt und zeigt die aktuelle Version auf der Startseite"""
        try:
            # Pfad zur VERSION-Datei (relativ zum Projekt-Root)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            version_path = os.path.join(project_root, 'VERSION')
            
            # Version aus Datei lesen
            if os.path.exists(version_path):
                with open(version_path, 'r', encoding='utf-8') as f:
                    version = f.read().strip()
                
                # Version-Label suchen und setzen
                if hasattr(self, 'label_version'):
                    self.label_version.setText(f"Version {version}")
                elif hasattr(self, 'lblVersion'):
                    self.lblVersion.setText(f"Version {version}")
                else:
                    # Fallback: Version im Window-Titel anzeigen
                    self.setWindowTitle(f"Futterkarre 2.0 - Version {version}")
            else:
                # Fallback wenn VERSION-Datei nicht existiert
                if hasattr(self, 'label_version'):
                    self.label_version.setText("Version unbekannt")
                    
        except Exception as e:
            print(f"Fehler beim Laden der Version: {e}")
            # Stumm weitermachen wenn Version nicht geladen werden kann

    def zu_auswahl(self):
        if self.navigation:
            self.navigation.show_status("auswahl")

