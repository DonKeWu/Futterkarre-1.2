#!/usr/bin/env python3
"""
Test-Script für WeightManager - Gewichtssynchronisation
"""

def test_weight_manager():
    print("🧪 WeightManager Test gestartet...\n")
    
    from hardware.weight_manager import get_weight_manager
    import hardware.hx711_sim as hx711_sim
    import time
    
    wm = get_weight_manager()
    
    # 1. Status prüfen
    print("1️⃣ WeightManager Status:")
    status = wm.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # 2. Simulation aktivieren
    print("\n2️⃣ Simulation aktivieren...")
    wm.set_simulation_mode(True)
    hx711_sim.setze_simulation(True)
    
    # 3. Gewicht lesen (sollte 0 sein)
    print("\n3️⃣ Initialgewicht:")
    weight = wm.read_weight()
    print(f"   Gewicht: {weight:.2f} kg")
    
    # 4. Karre beladen simulieren
    print("\n4️⃣ Karre beladen (35kg)...")
    wm.simulate_weight_change(35.0)
    weight = wm.read_weight(use_cache=False)
    print(f"   Gewicht nach Beladen: {weight:.2f} kg")
    
    # 5. Entnahme simulieren
    print("\n5️⃣ Fütterung simulieren (-4.5kg)...")
    wm.simulate_weight_change(-4.5)
    weight = wm.read_weight(use_cache=False)
    print(f"   Gewicht nach Entnahme: {weight:.2f} kg")
    
    # 6. Observer testen
    print("\n6️⃣ Observer-System testen...")
    
    gewicht_updates = []
    def weight_observer(weight):
        gewicht_updates.append(weight)
        print(f"   Observer: Neues Gewicht {weight:.2f} kg")
    
    wm.register_observer("test_observer", weight_observer)
    
    # Mehrere Gewichtsänderungen
    for i in range(3):
        wm.simulate_weight_change(-2.0)
        weight = wm.read_weight(use_cache=False)
        time.sleep(0.1)
    
    print(f"   Observer erhielt {len(gewicht_updates)} Updates")
    
    # 7. Einzelzellen testen
    print("\n7️⃣ Einzelzellen-Lesung:")
    cells = wm.read_individual_cells()
    for i, cell_weight in enumerate(cells):
        print(f"   Zelle {i+1}: {cell_weight:.2f} kg")
    
    # 8. Nullpunkt setzen
    print("\n8️⃣ Nullpunkt setzen...")
    success = wm.tare_weight()
    print(f"   Nullpunkt gesetzt: {'✅' if success else '❌'}")
    
    weight = wm.read_weight(use_cache=False)
    print(f"   Gewicht nach Nullpunkt: {weight:.2f} kg")
    
    # 9. Finaler Status
    print("\n9️⃣ Finaler Status:")
    status = wm.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Observer aufräumen
    wm.unregister_observer("test_observer")
    
    print("\n🎉 WeightManager Test abgeschlossen!")

if __name__ == "__main__":
    test_weight_manager()