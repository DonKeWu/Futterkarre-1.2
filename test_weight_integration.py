#!/usr/bin/env python3
"""
Test-Script für WeightManager Integration in UI-Komponenten
"""

def test_weight_integration():
    print("🧪 WeightManager UI-Integration Test...\n")
    
    from hardware.weight_manager import get_weight_manager
    import hardware.hx711_sim as hx711_sim
    
    # WeightManager initialisieren und Simulation aktivieren
    wm = get_weight_manager()
    wm.set_simulation_mode(True)
    hx711_sim.setze_simulation(True)
    
    print("1️⃣ WeightManager Status:")
    status = wm.get_status()
    print(f"   Simulation: {status['is_simulation']}")
    print(f"   Interface: {status['interface']}")
    print(f"   Aktuelles Gewicht: {status['current_weight']:.2f} kg")
    
    # Teste sensor_manager Wrapper
    print("\n2️⃣ Legacy sensor_manager Wrapper:")
    try:
        from hardware.sensor_manager import SmartSensorManager
        legacy_manager = SmartSensorManager()
        
        # Gewicht über legacy interface
        weight = legacy_manager.read_weight()
        print(f"   Legacy read_weight(): {weight:.2f} kg")
        
        # Beladen über WeightManager
        print("\n3️⃣ Beladen simulieren (25kg)...")
        wm.simulate_weight_change(25.0)
        
        # Beide Interfaces prüfen
        weight_new = legacy_manager.read_weight()
        weight_direct = wm.read_weight()
        
        print(f"   Legacy Interface: {weight_new:.2f} kg")
        print(f"   Direkt WeightManager: {weight_direct:.2f} kg")
        print(f"   Synchronisation: {'✅' if abs(weight_new - weight_direct) < 0.1 else '❌'}")
        
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    # Observer-System simulieren
    print("\n4️⃣ Observer-System Test:")
    updates_received = []
    
    def ui_observer(weight):
        updates_received.append(weight)
        print(f"   📊 UI Update: {weight:.2f} kg")
    
    wm.register_observer("ui_test", ui_observer)
    
    # Mehrere Gewichtsänderungen
    changes = [-3.0, -2.5, -4.0]  # Fütterung simulieren
    for i, change in enumerate(changes, 1):
        print(f"\n   Änderung {i}: {change:+.1f} kg")
        wm.simulate_weight_change(change)
        # Gewicht lesen löst Observer aus
        current = wm.read_weight(use_cache=False)
    
    print(f"\n   Observer erhielt {len(updates_received)} Updates")
    
    # Aufräumen
    wm.unregister_observer("ui_test")
    
    print("\n5️⃣ Finaler Status:")
    final_status = wm.get_status()
    print(f"   Endgewicht: {final_status['current_weight']:.2f} kg")
    print(f"   Observer: {final_status['observers_count']}")
    
    print("\n🎉 WeightManager UI-Integration Test abgeschlossen!")

if __name__ == "__main__":
    test_weight_integration()