#!/usr/bin/env python3
"""
Debug Script für LED-Status Problem
"""

import urllib.request
import json

def test_hx711_logic():
    """Teste HX711-Erkennungslogik"""
    print("🔍 ESP8266 HX711-Status Test\n")
    
    # ESP8266 Dual-Mode IPs
    test_ips = ["192.168.4.1", "192.168.2.20"]
    zell_namen = ["VL (Vorne Links)", "VR (Vorne Rechts)", "HL (Hinten Links)", "HR (Hinten Rechts)"]
    
    for ip in test_ips:
        try:
            url = f"http://{ip}/live-values-data"
            req = urllib.request.Request(url, headers={'User-Agent': 'Debug-Test'})
            
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            print(f"ESP8266 {ip} gefunden:")
            
            # Raw-Werte direkt prüfen
            raw_values = [
                data.get('vl_value', 0),  # VL
                data.get('vr_value', 0),  # VR  
                data.get('hl_value', 0),  # HL
                data.get('hr_value', 0)   # HR
            ]
            
            # Status für jede Zelle prüfen
            zell_status = [False, False, False, False]
            
            print("Raw-Werte und Status:")
            for i, (raw_val, name) in enumerate(zip(raw_values, zell_namen)):
                try:
                    val = float(raw_val)
                    # Verbesserte Logik: abs(val) > 1000 = angeschlossen (echte Messung)
                    if abs(val) > 1000:
                        zell_status[i] = True
                    
                    led_farbe = "🟢 GRÜN" if zell_status[i] else "🔴 ROT"
                    print(f"  {i}: {name} = {val} → {led_farbe}")
                    
                except (ValueError, TypeError):
                    print(f"  {i}: {name} = FEHLER ({raw_val})")
                    zell_status[i] = False
            
            print(f"\nErgebnis: {sum(zell_status)}/4 HX711 angeschlossen")
            print(f"Status-Array: {zell_status}")
            
            # Welche sollten grün/rot sein?
            print("\nErwartete LED-Farben:")
            for i, (status, name) in enumerate(zip(zell_status, zell_namen)):
                farbe = "🟢 GRÜN" if status else "🔴 ROT"
                print(f"  LED {i} ({name}): {farbe}")
            
            return  # Erfolg - stop hier
            
        except Exception as e:
            print(f"ESP8266 {ip}: {e}")
            continue
    
    print("❌ Kein ESP8266 erreichbar!")

if __name__ == "__main__":
    test_hx711_logic()