# views/start.py
import os
import sys
import views.icons.icons_rc

# Basis-Widget importieren
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.base_ui_widget import BaseViewWidget


class StartSeite(BaseViewWidget):
    def __init__(self, parent=None):
        # BaseViewWidget mit UI-Datei initialisieren
        super().__init__(parent, ui_filename="start.ui", page_name="start")
        
        # Spezielle Buttons verbinden
        self.connect_buttons_safe({
            "btn_start": self.zu_auswahl
        })
        
        # Version anzeigen
        self.load_and_display_version()

    def load_and_display_version(self):
        """Lädt und zeigt die aktuelle Version auf der Startseite"""
        try:
            # Pfad zur VERSION-Datei (relativ zum Projekt-Root)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            version_path = os.path.join(project_root, 'VERSION')
            
            # LOGGING für Pi5 Debug
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"VERSION DEBUG: Pfad={version_path}, existiert={os.path.exists(version_path)}")
            
            # Version aus Datei lesen
            if os.path.exists(version_path):
                with open(version_path, 'r', encoding='utf-8') as f:
                    version = f.read().strip()
                
                logger.info(f"VERSION DEBUG: Gelesen='{version}', hasattr={hasattr(self, 'label_version')}")
                
                # Version-Label setzen - label_version nur Version, lblVersion mit "Futterkarre"
                if hasattr(self, 'label_version'):
                    self.label_version.setText(version)
                    logger.info(f"VERSION DEBUG: label_version gesetzt auf '{version}'")
                elif hasattr(self, 'lblVersion'):
                    self.lblVersion.setText(f"Futterkarre {version}")
                    logger.info(f"VERSION DEBUG: lblVersion gesetzt")
                else:
                    # Fallback: Version im Window-Titel anzeigen
                    self.setWindowTitle(f"Futterkarre - Version {version}")
                    logger.info(f"VERSION DEBUG: Window-Titel gesetzt")
            else:
                logger.warning(f"VERSION DEBUG: Datei nicht gefunden: {version_path}")
                # Fallback wenn VERSION-Datei nicht existiert
                if hasattr(self, 'label_version'):
                    self.label_version.setText("Version unbekannt")
                    logger.warning(f"VERSION DEBUG: Fallback gesetzt")
                    
        except Exception as e:
            print(f"Fehler beim Laden der Version: {e}")
            # Stumm weitermachen wenn Version nicht geladen werden kann

    def zu_auswahl(self):
        if self.navigation:
            self.navigation.show_status("auswahl")

