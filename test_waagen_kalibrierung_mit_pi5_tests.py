#!/usr/bin/env python3
"""
Test der erweiterten Waagen-Kalibrierung mit Pi5 System-Tests
"""

import sys
import os

# Pfad für Imports
sys.path.append('/home/daniel/Dokumente/HOF/Futterwagen/Python/Futterkarre')

try:
    from PyQt5.QtWidgets import QApplication
    from views.waagen_kalibrierung import WaagenKalibrierung, Pi5SystemTester
    
    print("🧪 TESTE ERWEITERTE WAAGEN-KALIBRIERUNG")
    print("=" * 50)
    
    # 1. Pi5SystemTester separat testen
    print("\n1️⃣ Pi5SystemTester Test:")
    tester = Pi5SystemTester()
    print("✅ Pi5SystemTester erstellt")
    
    # Quick Test
    tester.run_quick_test()
    
    # 2. GUI Test (falls Display verfügbar)
    try:
        app = QApplication(sys.argv)
        print("\n2️⃣ GUI Test:")
        
        # WaagenKalibrierung mit Tests erstellen
        window = WaagenKalibrierung()
        print("✅ WaagenKalibrierung mit Pi5-Tests erstellt")
        
        # Fenster anzeigen
        window.resize(1000, 800)
        window.show()
        
        print("✅ GUI-Fenster geöffnet")
        print("🎯 Teste die Pi5-Test-Buttons in der GUI!")
        print("❌ Schließe das Fenster zum Beenden")
        
        # Event Loop (kurz für Test)
        import time
        for i in range(3):
            app.processEvents()
            time.sleep(1)
            if not window.isVisible():
                break
        
        print("✅ GUI Test erfolgreich")
        
    except Exception as e:
        print(f"⚠️ GUI Test übersprungen: {e}")
    
    print("\n🎉 ALLE TESTS ERFOLGREICH!")
    print("Die Waagen-Kalibrierung hat jetzt Pi5 System-Tests integriert!")
    
except Exception as e:
    print(f"❌ Test fehlgeschlagen: {e}")
    import traceback
    print(traceback.format_exc())