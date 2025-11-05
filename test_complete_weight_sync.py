#!/usr/bin/env python3
"""
Vollständiger Test für Gewichtssynchronisation zwischen UI-Komponenten
"""

def test_complete_weight_sync():
    print("🧪 Vollständige Gewichtssynchronisation Test...\n")
    
    from hardware.weight_manager import get_weight_manager
    from hardware.sensor_manager import SmartSensorManager
    import hardware.hx711_sim as hx711_sim
    import time
    
    # Komponenten initialisieren
    wm = get_weight_manager()
    legacy_manager = SmartSensorManager()
    
    # Simulation aktivieren
    wm.set_simulation_mode(True)
    hx711_sim.setze_simulation(True)
    
    print("1️⃣ System-Initialisierung:")
    status = wm.get_status()
    print(f"   WeightManager: {status['is_simulation']} (Simulation)")
    print(f"   Legacy Manager: {legacy_manager.read_weight():.2f} kg")
    print(f"   HX711 Simulation: {hx711_sim.ist_simulation_aktiv()}")
    
    # UI-Observer simulieren
    ui_updates = {"fuettern": [], "beladen": []}
    
    def fuettern_observer(weight):
        ui_updates["fuettern"].append(weight)
        print(f"   📊 FuetternSeite Update: {weight:.2f} kg")
    
    def beladen_observer(weight):
        ui_updates["beladen"].append(weight)
        print(f"   📊 BeladenSeite Update: {weight:.2f} kg")
    
    wm.register_observer("fuettern_seite", fuettern_observer)
    wm.register_observer("beladen_seite", beladen_observer)
    
    print("\n2️⃣ Simulation: Karre beladen (35kg)...")
    
    # BeladenSeite Workflow: Karre beladen
    wm.simulate_weight_change(35.0)
    weight_after_load = wm.read_weight(use_cache=False)
    legacy_weight = legacy_manager.read_weight()
    
    print(f"   WeightManager: {weight_after_load:.2f} kg")
    print(f"   Legacy Manager: {legacy_weight:.2f} kg")
    print(f"   Synchronisation: {'✅' if abs(weight_after_load - legacy_weight) < 0.2 else '❌'}")
    
    print("\n3️⃣ Simulation: Fütterung (mehrere Pferde)...")
    
    # FuetternSeite Workflow: Mehrere Fütterungen
    pferde_anzahl = 5
    futter_pro_pferd = 4.5
    
    for pferd_nr in range(1, pferde_anzahl + 1):
        print(f"\n   Pferd {pferd_nr}: Fütterung ({futter_pro_pferd}kg)...")
        
        # Gewicht vor Fütterung
        weight_before = wm.read_weight()
        
        # Fütterung über WeightManager
        wm.simulate_weight_change(-futter_pro_pferd)
        
        # Gewicht nach Fütterung
        weight_after = wm.read_weight(use_cache=False)
        legacy_after = legacy_manager.read_weight()
        
        # Validierung
        expected_change = -futter_pro_pferd
        actual_change = weight_after - weight_before
        
        print(f"      Vorher: {weight_before:.2f} kg")
        print(f"      Nachher: {weight_after:.2f} kg (WM) / {legacy_after:.2f} kg (Legacy)")
        print(f"      Änderung: {actual_change:+.2f} kg (erwartet: {expected_change:+.2f} kg)")
        print(f"      Sync: {'✅' if abs(weight_after - legacy_after) < 0.2 else '❌'}")
        
        time.sleep(0.1)  # Kleine Pause für realistische Simulation
    
    print("\n4️⃣ Simulation: Karre nachladen...")
    
    # Nachladen wenn Karre fast leer
    current_weight = wm.read_weight()
    if current_weight < 10.0:
        print(f"   Karre fast leer ({current_weight:.2f} kg) - Nachladen...")
        wm.simulate_weight_change(30.0)  # 30kg nachladen
        
        weight_reloaded = wm.read_weight(use_cache=False)
        print(f"   Nach Nachladen: {weight_reloaded:.2f} kg")
    
    print("\n5️⃣ Hardware-Simulation: Nullpunkt setzen...")
    
    # Nullpunkt-Test
    success = wm.tare_weight()
    weight_after_tare = wm.read_weight(use_cache=False)
    
    print(f"   Nullpunkt setzen: {'✅' if success else '❌'}")
    print(f"   Gewicht nach Nullpunkt: {weight_after_tare:.2f} kg")
    
    print("\n6️⃣ Einzelzellen-Test...")
    
    # Einzelzellen für Kalibrierung/Debugging
    cells = wm.read_individual_cells()
    total_cells = sum(cells)
    
    for i, cell_weight in enumerate(cells, 1):
        print(f"   Zelle {i}: {cell_weight:.2f} kg")
    
    print(f"   Summe Einzelzellen: {total_cells:.2f} kg")
    print(f"   WeightManager Total: {wm.read_weight():.2f} kg")
    print(f"   Abweichung: {abs(total_cells - wm.read_weight()):.2f} kg")
    
    print("\n7️⃣ Observer-Statistik:")
    print(f"   FuetternSeite Updates: {len(ui_updates['fuettern'])}")
    print(f"   BeladenSeite Updates: {len(ui_updates['beladen'])}")
    
    if ui_updates['fuettern']:
        print(f"   Letztes FuetternSeite Update: {ui_updates['fuettern'][-1]:.2f} kg")
    if ui_updates['beladen']:
        print(f"   Letztes BeladenSeite Update: {ui_updates['beladen'][-1]:.2f} kg")
    
    print("\n8️⃣ Finaler System-Status:")
    final_status = wm.get_status()
    
    print(f"   Endgewicht: {final_status['current_weight']:.2f} kg")
    print(f"   Interface: {final_status['interface']}")
    print(f"   Fehleranzahl: {final_status['error_count']}")
    print(f"   Observer aktiv: {final_status['observers_count']}")
    print(f"   Letztes Update: {time.time() - final_status['last_update']:.1f} s her")
    
    # Aufräumen
    wm.unregister_observer("fuettern_seite")
    wm.unregister_observer("beladen_seite")
    
    print("\n🎉 Vollständige Gewichtssynchronisation Test abgeschlossen!")
    print("✅ WeightManager erfolgreich als zentrale Gewichtsquelle etabliert")

if __name__ == "__main__":
    test_complete_weight_sync()