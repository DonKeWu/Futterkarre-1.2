#!/usr/bin/env python3
"""
GUI Test für Futterkarre - Testet die Benutzeroberfläche
"""

import sys
import os
from datetime import datetime

def test_gui():
    print("🖥️ FUTTERKARRE GUI TEST")
    print("=" * 40)
    
    try:
        # PyQt5 Import
        from PyQt5 import QtWidgets, QtCore
        from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton
        print("✅ PyQt5 importiert")
        
        # Test Application erstellen
        app = QApplication(sys.argv)
        print("✅ QApplication erstellt")
        
        # Test Fenster
        window = QWidget()
        window.setWindowTitle("Futterkarre Pi5 GUI Test")
        window.resize(800, 600)
        
        # Layout
        layout = QVBoxLayout()
        
        # Test Labels
        title = QLabel("🎯 FUTTERKARRE GUI TEST")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2E8B57; padding: 20px;")
        layout.addWidget(title)
        
        status = QLabel(f"⏰ Zeit: {datetime.now().strftime('%H:%M:%S')}")
        status.setStyleSheet("font-size: 16px; padding: 10px;")
        layout.addWidget(status)
        
        info = QLabel("✅ PyQt5 GUI funktioniert!\n\n"
                     "🎮 Teste verschiedene Funktionen:\n"
                     "• Fenster öffnet sich\n"
                     "• Text wird angezeigt\n" 
                     "• Button funktioniert\n"
                     "• Schließen möglich")
        info.setStyleSheet("font-size: 14px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(info)
        
        # Test Button
        def button_clicked():
            print("🔘 Button geklickt! GUI reagiert korrekt.")
            info.setText(info.text() + "\n\n🎉 Button Test: ERFOLGREICH!")
        
        button = QPushButton("🔘 Klick mich zum Testen!")
        button.setStyleSheet("font-size: 16px; padding: 15px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;")
        button.clicked.connect(button_clicked)
        layout.addWidget(button)
        
        # Close Button
        def close_app():
            print("👋 GUI Test beendet.")
            app.quit()
        
        close_btn = QPushButton("❌ Test beenden")
        close_btn.setStyleSheet("font-size: 14px; padding: 10px; background-color: #f44336; color: white; border: none; border-radius: 5px;")
        close_btn.clicked.connect(close_app)
        layout.addWidget(close_btn)
        
        # Layout setzen
        window.setLayout(layout)
        
        print("✅ GUI Komponenten erstellt")
        
        # Fenster anzeigen
        window.show()
        print("✅ Fenster wird angezeigt")
        print()
        print("🎯 GUI Test läuft!")
        print("⭐ Wenn das Fenster erscheint, ist PyQt5 funktional!")
        print("🔄 Schließe das Fenster oder drücke Ctrl+C zum Beenden")
        
        # Event Loop
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"❌ PyQt5 Import Error: {e}")
        print("💡 Installiere PyQt5: sudo apt install python3-pyqt5")
        return False
        
    except Exception as e:
        print(f"❌ GUI Test Fehler: {e}")
        return False

def test_futterkarre_gui():
    """Test die echte Futterkarre GUI"""
    print("\n🎯 ECHTE FUTTERKARRE GUI TEST")
    print("=" * 40)
    
    try:
        # Originale Imports testen
        from config.app_config import AppConfig
        from hardware.sensor_manager import SmartSensorManager  
        from views.main_window import MainWindow
        from PyQt5.QtWidgets import QApplication
        
        print("✅ Alle Futterkarre Module importiert")
        
        # App erstellen
        app = QApplication(sys.argv)
        
        # Hardware Manager (Simulation)
        sensor_manager = SmartSensorManager()
        print("✅ Sensor Manager erstellt")
        
        # Hauptfenster
        window = MainWindow(sensor_manager)
        print("✅ MainWindow erstellt")
        
        # Fenster-Modus (für Tests)
        window.resize(1280, 720)
        window.show()
        print("✅ Futterkarre GUI gestartet (Test-Modus)")
        
        print()
        print("🎉 FUTTERKARRE GUI LÄUFT!")
        print("📱 Das ist die echte Futterkarre Oberfläche")
        print("🖱️ Teste alle Funktionen in der GUI")
        print("❌ Schließe das Fenster zum Beenden")
        
        # Event Loop
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ Futterkarre GUI Fehler: {e}")
        import traceback
        print(f"🔍 Details: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("Welchen GUI Test möchtest du ausführen?")
    print("1 = Einfacher PyQt5 Test")
    print("2 = Echte Futterkarre GUI") 
    print("Enter = Einfacher Test")
    
    choice = input("\nWahl (1/2): ").strip()
    
    if choice == "2":
        test_futterkarre_gui()
    else:
        test_gui()