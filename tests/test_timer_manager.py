#!/usr/bin/env python3
"""
Test-Script für TimerManager - Timer-Zentralisierung
"""

import sys
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def test_timer_manager():
    print("🧪 TimerManager Test gestartet...\n")
    
    # QApplication für QTimer
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    
    from utils.timer_manager import get_timer_manager
    
    tm = get_timer_manager()
    
    print("1️⃣ TimerManager Initialisierung:")
    status = tm.get_timer_status()
    print(f"   Aktive Seite: {status['active_page']}")
    print(f"   Gesamte Timer: {status['total_timers']}")
    print(f"   Aktive Timer: {status['active_timers']}")
    
    # Callback-Funktionen für Tests
    callback_counter = {'fuettern': 0, 'beladen': 0, 'einstellungen': 0}
    
    def fuettern_callback():
        callback_counter['fuettern'] += 1
        print(f"   📊 FuetternSeite Timer: Aufruf #{callback_counter['fuettern']}")
    
    def beladen_callback():
        callback_counter['beladen'] += 1
        print(f"   📦 BeladenSeite Timer: Aufruf #{callback_counter['beladen']}")
    
    def einstellungen_callback():
        callback_counter['einstellungen'] += 1
        print(f"   ⚙️ EinstellungenSeite Timer: Aufruf #{callback_counter['einstellungen']}")
    
    print("\n2️⃣ Timer registrieren...")
    
    # Timer für verschiedene UI-Komponenten registrieren
    tm.register_timer("fuettern_weight_update", "FuetternSeite", 1000, fuettern_callback)
    tm.register_timer("beladen_weight_update", "BeladenSeite", 500, beladen_callback)
    tm.register_timer("einstellungen_status", "EinstellungenSeite", 2000, einstellungen_callback)
    
    status = tm.get_timer_status()
    print(f"   Registrierte Timer: {status['total_timers']}")
    
    for timer_id, timer_info in status['timers'].items():
        print(f"      {timer_id}: {timer_info['component']} ({timer_info['interval']}ms)")
    
    print("\n3️⃣ Seitenwechsel-Simulation...")
    
    # Simulation: Wechsel zur FuetternSeite
    print("\n   📄 Wechsel zu FuetternSeite...")
    tm.set_active_page("FuetternSeite")
    
    # Event-Loop für Timer-Ausführung
    start_time = time.time()
    while time.time() - start_time < 3:  # 3 Sekunden warten
        app.processEvents()
        time.sleep(0.1)
    
    print(f"\n   FuetternSeite Timer-Aufrufe: {callback_counter['fuettern']}")
    print(f"   BeladenSeite Timer-Aufrufe: {callback_counter['beladen']} (sollte 0 sein)")
    
    # Simulation: Wechsel zur BeladenSeite
    print("\n   📄 Wechsel zu BeladenSeite...")
    tm.set_active_page("BeladenSeite")
    
    start_time = time.time()
    while time.time() - start_time < 2:  # 2 Sekunden warten
        app.processEvents()
        time.sleep(0.1)
    
    print(f"\n   BeladenSeite Timer-Aufrufe: {callback_counter['beladen']}")
    print(f"   FuetternSeite Timer-Aufrufe: {callback_counter['fuettern']} (sollte gestoppt sein)")
    
    print("\n4️⃣ Timer-Statistiken:")
    
    final_status = tm.get_timer_status()
    for timer_id, timer_info in final_status['timers'].items():
        print(f"   {timer_id}:")
        print(f"      Komponente: {timer_info['component']}")
        print(f"      Aktiv: {'✅' if timer_info['active'] else '❌'}")
        print(f"      Aufrufe: {timer_info['trigger_count']}")
        print(f"      Letzter Aufruf: {timer_info['last_triggered']:.1f}")
    
    print("\n5️⃣ Memory-Test...")
    
    # Viele Timer erstellen und wieder entfernen (Memory-Leak Test)
    print("   Erstelle 10 temporäre Timer...")
    temp_timers = []
    
    for i in range(10):
        timer_id = f"temp_timer_{i}"
        tm.register_timer(timer_id, "TempComponent", 100, lambda: None)
        temp_timers.append(timer_id)
    
    memory_before = tm.get_memory_stats()
    print(f"   Timer vor Cleanup: {memory_before['timer_count']}")
    
    # Timer wieder entfernen
    for timer_id in temp_timers:
        tm.unregister_timer(timer_id)
    
    memory_after = tm.get_memory_stats()
    print(f"   Timer nach Cleanup: {memory_after['timer_count']}")
    print(f"   Memory-Leak Test: {'✅ Bestanden' if memory_after['timer_count'] == 3 else '❌ Fehlgeschlagen'}")
    
    print("\n6️⃣ Alle Timer stoppen...")
    tm.stop_all_timers()
    
    final_status = tm.get_timer_status()
    active_count = sum(1 for t in final_status['timers'].values() if t['active'])
    print(f"   Aktive Timer nach Stop: {active_count} (sollte 0 sein)")
    
    print("\n7️⃣ Cleanup...")
    tm.cleanup()
    
    cleanup_status = tm.get_timer_status()
    print(f"   Timer nach Cleanup: {cleanup_status['total_timers']} (sollte 0 sein)")
    
    print("\n🎉 TimerManager Test abgeschlossen!")
    print("✅ Timer-Management erfolgreich zentralisiert")

if __name__ == "__main__":
    test_timer_manager()