# views/display_config_seite.py
import os
import sys
import json
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QSlider
from PyQt5.QtCore import QTimer, pyqtSignal

# Basis-Widget importieren
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.base_ui_widget import BaseViewWidget
from utils.settings_manager import SettingsManager
from utils.theme_manager import get_theme_manager


class DisplayConfigSeite(BaseViewWidget):
    """Display-Konfiguration für Helligkeit, Themes und Auto-Nacht-Modus"""
    
    # Signale für externe Komponenten
    theme_changed = pyqtSignal(str)  # Neues Theme wird geladen
    brightness_changed = pyqtSignal(int)  # Neue Helligkeit gesetzt
    
    def __init__(self, parent=None):
        # BaseViewWidget mit UI-Datei initialisieren
        super().__init__(parent, ui_filename="display_config_seite.ui", page_name="display_config")
        
        # Settings Manager
        self.settings = SettingsManager()
        
        # Theme Manager
        self.theme_manager = get_theme_manager()
        
        # Hardware-Pfade
        self.brightness_path = "/sys/class/backlight/11-0045/brightness"
        self.brightness_max_path = "/sys/class/backlight/11-0045/max_brightness"
        
        # Auto-Nacht Timer
        self.auto_night_timer = QTimer()
        self.auto_night_timer.timeout.connect(self.check_auto_night_mode)
        
        # UI initialisieren
        self.setup_ui()
        self.load_current_settings()
        
        # Timer für Auto-Nacht starten (alle 30 Sekunden prüfen)
        self.auto_night_timer.start(30000)

    def setup_ui(self):
        """UI-Elemente konfigurieren und Signale verbinden"""
        try:
            # Buttons verbinden
            self.connect_buttons_safe({
                "btn_back": self.zurueck_zu_einstellungen,
                "btn_speichern": self.settings_speichern,
                "btn_reset": self.settings_zuruecksetzen,
                "btn_vorschau_demo": self.demo_animation
            })
            
            # Helligkeit-Slider
            if hasattr(self, 'slider_helligkeit'):
                self.slider_helligkeit.valueChanged.connect(self.on_brightness_changed)
                self.slider_helligkeit.sliderPressed.connect(self.start_brightness_preview)
                self.slider_helligkeit.sliderReleased.connect(self.stop_brightness_preview)
            
            # Theme ComboBox
            if hasattr(self, 'combo_theme'):
                self.combo_theme.currentTextChanged.connect(self.on_theme_changed)
            
            # Auto-Nacht CheckBox
            if hasattr(self, 'chk_auto_nachtmodus'):
                self.chk_auto_nachtmodus.toggled.connect(self.on_auto_night_toggled)
                
            print("✅ Display-Config UI erfolgreich initialisiert")
            
        except Exception as e:
            print(f"❌ Fehler beim Setup der Display-Config UI: {e}")

    def load_current_settings(self):
        """Aktuelle Einstellungen aus settings.json laden"""
        try:
            # Helligkeit laden
            current_brightness = self.get_hardware_brightness()
            if hasattr(self, 'slider_helligkeit'):
                self.slider_helligkeit.setValue(current_brightness)
            self.update_brightness_label(current_brightness)
            
            # Theme laden
            current_theme = self.settings.get_setting('ui', 'theme', 'Standard')
            if hasattr(self, 'combo_theme'):
                index = self.combo_theme.findText(current_theme)
                if index >= 0:
                    self.combo_theme.setCurrentIndex(index)
            
            # Auto-Nacht laden
            auto_night = self.settings.get_setting('system', 'auto_night_mode', False)
            if hasattr(self, 'chk_auto_nachtmodus'):
                self.chk_auto_nachtmodus.setChecked(auto_night)
                
            print(f"✅ Settings geladen: Helligkeit={current_brightness}, Theme={current_theme}, Auto-Nacht={auto_night}")
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der Display-Settings: {e}")

    def get_hardware_brightness(self):
        """Aktuelle Hardware-Helligkeit vom PiTouch2 lesen"""
        try:
            if os.path.exists(self.brightness_path):
                with open(self.brightness_path, 'r') as f:
                    return int(f.read().strip())
            else:
                print(f"⚠️ Brightness-Pfad nicht gefunden: {self.brightness_path}")
                return 15  # Fallback Mittelwert
        except Exception as e:
            print(f"❌ Fehler beim Lesen der Hardware-Helligkeit: {e}")
            return 15

    def set_hardware_brightness(self, value):
        """Hardware-Helligkeit am PiTouch2 setzen"""
        try:
            # Wert auf gültigen Bereich begrenzen (1-31)
            value = max(1, min(31, value))
            
            if os.path.exists(self.brightness_path):
                # Root-Rechte erforderlich, aber versuchen wir es
                with open(self.brightness_path, 'w') as f:
                    f.write(str(value))
                print(f"✅ Hardware-Helligkeit gesetzt: {value}")
                return True
            else:
                print(f"⚠️ Brightness-Hardware nicht verfügbar: {self.brightness_path}")
                return False
                
        except PermissionError:
            print(f"⚠️ Keine Berechtigung für Hardware-Helligkeit. Sudo erforderlich.")
            # Fallback: Über sudo versuchen
            try:
                os.system(f"echo {value} | sudo tee {self.brightness_path} > /dev/null")
                print(f"✅ Hardware-Helligkeit per sudo gesetzt: {value}")
                return True
            except:
                print(f"❌ Auch sudo-Versuch fehlgeschlagen")
                return False
        except Exception as e:
            print(f"❌ Fehler beim Setzen der Hardware-Helligkeit: {e}")
            return False

    def update_brightness_label(self, value):
        """Prozent-Label für Helligkeit aktualisieren"""
        try:
            # 1-31 auf 3%-100% umrechnen
            percent = int(((value - 1) / 30) * 97 + 3)
            if hasattr(self, 'lbl_helligkeit_wert'):
                self.lbl_helligkeit_wert.setText(f"{percent}%")
        except Exception as e:
            print(f"❌ Fehler beim Aktualisieren des Helligkeit-Labels: {e}")

    def on_brightness_changed(self, value):
        """Helligkeit-Slider wurde bewegt"""
        try:
            # Label sofort aktualisieren
            self.update_brightness_label(value)
            
            # Hardware nur bei Live-Vorschau aktualisieren
            if hasattr(self, '_brightness_preview_active') and self._brightness_preview_active:
                self.set_hardware_brightness(value)
            
            # Signal emittieren
            self.brightness_changed.emit(value)
            
        except Exception as e:
            print(f"❌ Fehler bei Helligkeit-Änderung: {e}")

    def start_brightness_preview(self):
        """Live-Vorschau für Helligkeit starten"""
        self._brightness_preview_active = True
        print("🔆 Helligkeit Live-Vorschau gestartet")

    def stop_brightness_preview(self):
        """Live-Vorschau für Helligkeit stoppen"""
        self._brightness_preview_active = False
        print("🔆 Helligkeit Live-Vorschau gestoppt")

    def on_theme_changed(self, theme_name):
        """Theme wurde geändert"""
        try:
            # Globales Theme anwenden
            success = self.theme_manager.apply_theme(theme_name)
            if success:
                # Lokale Vorschau auch aktualisieren
                self.apply_theme_preview(theme_name)
                self.theme_changed.emit(theme_name)
                print(f"🎨 Theme gewechselt zu: {theme_name}")
            else:
                print(f"❌ Theme konnte nicht angewendet werden: {theme_name}")
        except Exception as e:
            print(f"❌ Fehler beim Theme-Wechsel: {e}")

    def apply_theme_preview(self, theme_name):
        """Theme auf Vorschau-Bereich anwenden"""
        try:
            # Theme-Mapping
            theme_styles = {
                "Standard": {
                    "bg_color": "#fdffe0",
                    "header_bg": "#2E672F",
                    "header_fg": "#fdffe0",
                    "text_color": "#000000",
                    "button_bg": "#2E672F",
                    "button_fg": "white"
                },
                "Nacht (Blau)": {
                    "bg_color": "#1a1a2e",
                    "header_bg": "#16213e",
                    "header_fg": "#87ceeb",
                    "text_color": "#87ceeb",
                    "button_bg": "#0f3460",
                    "button_fg": "#87ceeb"
                },
                "Natur (Grün)": {
                    "bg_color": "#0d1f0d",
                    "header_bg": "#1a3d1a",
                    "header_fg": "#90ee90",
                    "text_color": "#90ee90",
                    "button_bg": "#2d5a2d",
                    "button_fg": "#90ee90"
                },
                "Ultra-Dunkel": {
                    "bg_color": "#000000",
                    "header_bg": "#1a1a1a",
                    "header_fg": "#666666",
                    "text_color": "#333333",
                    "button_bg": "#2a2a2a",
                    "button_fg": "#666666"
                }
            }
            
            if theme_name in theme_styles:
                style = theme_styles[theme_name]
                
                # Vorschau-Frame stylen
                if hasattr(self, 'frame_vorschau'):
                    self.frame_vorschau.setStyleSheet(f"""
                        QFrame {{
                            background-color: {style['bg_color']};
                            border: 3px solid {style['header_bg']};
                            border-radius: 15px;
                        }}
                    """)
                
                # Vorschau-Titel stylen
                if hasattr(self, 'lbl_vorschau_titel'):
                    self.lbl_vorschau_titel.setStyleSheet(f"""
                        background-color: {style['header_bg']};
                        color: {style['header_fg']};
                        border-radius: 8px;
                        padding: 5px;
                    """)
                
                # Vorschau-Text stylen
                if hasattr(self, 'lbl_vorschau_text'):
                    self.lbl_vorschau_text.setStyleSheet(f"""
                        color: {style['text_color']};
                    """)
                
                # Demo-Button stylen
                if hasattr(self, 'btn_vorschau_demo'):
                    self.btn_vorschau_demo.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {style['button_bg']};
                            color: {style['button_fg']};
                            border-radius: 8px;
                            padding: 5px;
                        }}
                        QPushButton:hover {{
                            background-color: {style['header_bg']};
                        }}
                    """)
                    
        except Exception as e:
            print(f"❌ Fehler beim Anwenden des Themes: {e}")

    def on_auto_night_toggled(self, checked):
        """Auto-Nacht-Modus wurde geändert"""
        try:
            print(f"🌙 Auto-Nacht-Modus: {'Aktiviert' if checked else 'Deaktiviert'}")
            
            # Sofort prüfen wenn aktiviert
            if checked:
                self.check_auto_night_mode()
                
        except Exception as e:
            print(f"❌ Fehler beim Auto-Nacht Toggle: {e}")

    def check_auto_night_mode(self):
        """Prüft ob Auto-Nacht-Modus aktiv werden soll"""
        try:
            # Nur prüfen wenn Auto-Modus aktiviert ist
            if not (hasattr(self, 'chk_auto_nachtmodus') and self.chk_auto_nachtmodus.isChecked()):
                return
            
            # Aktuelle Zeit prüfen
            now = datetime.now()
            hour = now.hour
            
            # Nacht-Zeit: 22:00 - 06:00
            is_night_time = hour >= 22 or hour < 6
            
            # Theme automatisch wechseln
            if hasattr(self, 'combo_theme'):
                current_theme = self.combo_theme.currentText()
                
                if is_night_time and "Nacht" not in current_theme:
                    # Zu Nacht-Theme wechseln
                    night_index = self.combo_theme.findText("Nacht (Blau)")
                    if night_index >= 0:
                        self.combo_theme.setCurrentIndex(night_index)
                        print(f"🌙 Auto-Wechsel zu Nacht-Theme um {now.strftime('%H:%M')}")
                        
                elif not is_night_time and "Nacht" in current_theme:
                    # Zu Standard-Theme wechseln
                    standard_index = self.combo_theme.findText("Standard")
                    if standard_index >= 0:
                        self.combo_theme.setCurrentIndex(standard_index)
                        print(f"☀️ Auto-Wechsel zu Tag-Theme um {now.strftime('%H:%M')}")
                        
        except Exception as e:
            print(f"❌ Fehler bei Auto-Nacht-Prüfung: {e}")

    def demo_animation(self):
        """Demo-Animation für Vorschau"""
        try:
            # Einfache Demo: Button-Text kurz ändern
            if hasattr(self, 'btn_vorschau_demo'):
                original_text = self.btn_vorschau_demo.text()
                self.btn_vorschau_demo.setText("✨ Demo läuft!")
                
                # Nach 1 Sekunde zurücksetzen
                QTimer.singleShot(1000, lambda: self.btn_vorschau_demo.setText(original_text))
                
        except Exception as e:
            print(f"❌ Fehler bei Demo-Animation: {e}")

    def settings_speichern(self):
        """Aktuelle Einstellungen in settings.json speichern"""
        try:
            # Helligkeit speichern und Hardware setzen
            if hasattr(self, 'slider_helligkeit'):
                brightness = self.slider_helligkeit.value()
                self.settings.set_setting('system', 'brightness', brightness)
                self.set_hardware_brightness(brightness)
            
            # Theme speichern
            if hasattr(self, 'combo_theme'):
                theme = self.combo_theme.currentText()
                self.settings.set_setting('ui', 'theme', theme)
            
            # Auto-Nacht speichern
            if hasattr(self, 'chk_auto_nachtmodus'):
                auto_night = self.chk_auto_nachtmodus.isChecked()
                self.settings.set_setting('system', 'auto_night_mode', auto_night)
            
            # Settings speichern
            self.settings.save_settings()
            
            print("✅ Display-Einstellungen gespeichert!")
            self.show_success_message("Einstellungen gespeichert!")
            
        except Exception as e:
            print(f"❌ Fehler beim Speichern der Display-Settings: {e}")
            self.show_error_message("Fehler beim Speichern!")

    def settings_zuruecksetzen(self):
        """Einstellungen auf Standard-Werte zurücksetzen"""
        try:
            # Standard-Werte setzen
            if hasattr(self, 'slider_helligkeit'):
                self.slider_helligkeit.setValue(15)  # 50% Helligkeit
            
            if hasattr(self, 'combo_theme'):
                standard_index = self.combo_theme.findText("Standard")
                if standard_index >= 0:
                    self.combo_theme.setCurrentIndex(standard_index)
            
            if hasattr(self, 'chk_auto_nachtmodus'):
                self.chk_auto_nachtmodus.setChecked(False)
            
            print("🔄 Display-Einstellungen zurückgesetzt!")
            self.show_success_message("Einstellungen zurückgesetzt!")
            
        except Exception as e:
            print(f"❌ Fehler beim Zurücksetzen: {e}")

    def zurueck_zu_einstellungen(self):
        """Zurück zur Einstellungen-Seite"""
        try:
            if self.navigation:
                self.navigation.show_status("einstellungen")
        except Exception as e:
            print(f"❌ Fehler bei Navigation zurück: {e}")

    def show_success_message(self, message):
        """Erfolgs-Nachricht anzeigen (Fallback)"""
        print(f"✅ {message}")

    def show_error_message(self, message):
        """Fehler-Nachricht anzeigen (Fallback)"""
        print(f"❌ {message}")