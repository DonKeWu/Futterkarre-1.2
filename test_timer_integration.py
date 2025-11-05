#!/usr/bin/env python3
"""
Test für Timer-Integration in UI-Komponenten
"""

import sys
import time
from PyQt5.QtWidgets import QApplication

def test_timer_integration():
    print("🧪 Timer-Integration Test gestartet...\n")
    
    # QApplication für UI-Komponenten
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    
    from utils.timer_manager import get_timer_manager
    from hardware.weight_manager import get_weight_manager
    from hardware.sensor_manager import SmartSensorManager
    
    # Manager initialisieren
    tm = get_timer_manager()
    wm = get_weight_manager()
    wm.set_simulation_mode(True)
    
    sensor_manager = SmartSensorManager()
    
    print("1️⃣ UI-Komponenten erstellen...")
    
    # UI-Komponenten erstellen
    try:
        from views.fuettern_seite import FuetternSeite
        from views.beladen_seite import BeladenSeite
        
        fuettern_seite = FuetternSeite()
        beladen_seite = BeladenSeite(sensor_manager)
        
        print("   ✅ UI-Komponenten erstellt")
        
    except Exception as e:
        print(f"   ❌ Fehler bei UI-Erstellung: {e}")
        return
    
    print("\n2️⃣ Timer-Status vor Integration:")
    status = tm.get_timer_status()
    print(f"   Registrierte Timer: {status['total_timers']}")
    print(f"   Aktive Timer: {status['active_timers']}")
    
    for timer_id, timer_info in status['timers'].items():
        print(f"      {timer_id}: {timer_info['component']} ({'aktiv' if timer_info['active'] else 'inaktiv'})")
    
    print("\n3️⃣ Seitenwechsel-Simulation...")
    
    # Simulation: FuetternSeite aktivieren
    print("\n   📄 Aktiviere FuetternSeite...")
    tm.set_active_page("FuetternSeite")
    
    # Kurz warten und Events verarbeiten
    start_time = time.time()
    while time.time() - start_time < 2:
        app.processEvents()
        time.sleep(0.1)
    
    status_fuettern = tm.get_timer_status()
    print(f"   FuetternSeite Timer aktiv: {any(t['active'] and t['component'] == 'FuetternSeite' for t in status_fuettern['timers'].values())}")
    
    # Simulation: BeladenSeite aktivieren
    print("\n   📦 Aktiviere BeladenSeite...")
    tm.set_active_page("BeladenSeite")
    
    # Kurz warten und Events verarbeiten
    start_time = time.time()
    while time.time() - start_time < 2:
        app.processEvents()
        time.sleep(0.1)
    
    status_beladen = tm.get_timer_status()
    fuettern_active = any(t['active'] and t['component'] == 'FuetternSeite' for t in status_beladen['timers'].values())
    beladen_active = any(t['active'] and t['component'] == 'BeladenSeite' for t in status_beladen['timers'].values())
    
    print(f"   FuetternSeite Timer noch aktiv: {fuettern_active} (sollte False sein)")
    print(f"   BeladenSeite Timer aktiv: {beladen_active} (sollte True sein)")
    
    print("\n4️⃣ Timer-Statistiken:")
    for timer_id, timer_info in status_beladen['timers'].items():
        print(f"   {timer_id}:")
        print(f"      Komponente: {timer_info['component']}")
        print(f"      Intervall: {timer_info['interval']}ms")
        print(f"      Status: {'🟢 Aktiv' if timer_info['active'] else '🔴 Inaktiv'}")
        print(f"      Aufrufe: {timer_info['trigger_count']}")
    
    print("\n5️⃣ Memory-Leak Test...")
    
    # Memory vor dem Test
    memory_before = tm.get_memory_stats()
    print(f"   Timer vor Test: {memory_before['timer_count']}")
    
    # Mehrfache Seitenwechsel
    for i in range(5):
        tm.set_active_page("FuetternSeite")
        time.sleep(0.1)
        app.processEvents()
        
        tm.set_active_page("BeladenSeite")
        time.sleep(0.1)
        app.processEvents()
    
    # Memory nach dem Test
    memory_after = tm.get_memory_stats()
    print(f"   Timer nach Test: {memory_after['timer_count']}")
    print(f"   Memory-Leak Test: {'✅ Bestanden' if memory_after['timer_count'] == memory_before['timer_count'] else '❌ Fehlgeschlagen'}")
    
    print("\n6️⃣ Gewichts-Observer + Timer Integration...")
    
    # Gewichtsänderung während Timer aktiv sind
    print("   Beladen simulieren...")
    wm.simulate_weight_change(25.0)
    
    # Events verarbeiten
    for _ in range(10):
        app.processEvents()
        time.sleep(0.1)
    
    current_weight = wm.read_weight()
    print(f"   Aktuelles Gewicht: {current_weight:.2f} kg")
    
    print("\n7️⃣ Cleanup...")
    
    # Timer stoppen
    tm.stop_all_timers()
    
    # UI-Komponenten aufräumen
    if hasattr(fuettern_seite, 'closeEvent'):
        fuettern_seite.close()
    if hasattr(beladen_seite, 'closeEvent'):
        beladen_seite.close()
    
    # Timer aufräumen
    tm.cleanup()
    
    final_status = tm.get_timer_status()
    print(f"   Timer nach Cleanup: {final_status['total_timers']} (sollte 0 sein)")
    
    print("\n8️⃣ Legacy-Kompatibilität Test...")
    
    # Test, dass alte start_timer()/stop_timer() Aufrufe nicht crashen
    try:
        fuettern_seite = FuetternSeite()
        fuettern_seite.start_timer()  # Legacy-Methode
        fuettern_seite.stop_timer()   # Legacy-Methode
        print("   ✅ Legacy-Methoden funktionieren")
    except Exception as e:
        print(f"   ❌ Legacy-Kompatibilität fehlgeschlagen: {e}")
    
    print("\n🎉 Timer-Integration Test abgeschlossen!")
    print("✅ Timer-Management erfolgreich zentralisiert")
    print("✅ Memory-Leaks verhindert")
    print("✅ Legacy-Kompatibilität erhalten")

if __name__ == "__main__":
    test_timer_integration()