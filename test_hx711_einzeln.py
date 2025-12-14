#!/usr/bin/env python3
"""
ESP8266 Einzelner HX711-Test
Testet nur HX711_1 (den Sie angeschlossen haben)
"""

import requests
import time
import json

class SingleHX711Tester:
    def __init__(self):
        self.esp_ips = ["192.168.2.20", "192.168.4.1"]
        
    def test_single_hx711(self):
        print("🔧 ESP8266 HX711_1 Einzeltest")
        print("=" * 40)
        print("📋 Erwartete Verkabelung:")
        print("   HX711 → ESP8266 NodeMCU")
        print("   CLK   → D1 (GPIO5)")
        print("   DT    → D2 (GPIO4)") 
        print("   VCC   → 5V")
        print("   GND   → GND")
        print("=" * 40)
        
        for ip in self.esp_ips:
            print(f"\n🔍 Teste ESP8266: {ip}")
            
            # Status abrufen
            try:
                response = requests.get(f"http://{ip}/status", timeout=3)
                if response.status_code == 200:
                    status = response.json()
                    
                    print(f"✅ ESP8266 erreichbar")
                    print(f"   Device: {status.get('device_name')}")
                    print(f"   Uptime: {status.get('uptime', 0) // 1000}s")
                    print(f"   Weight Available: {status.get('weight_available')}")
                    
                    weight_avail = status.get('weight_available', False)
                    
                    if weight_avail:
                        current_weight = status.get('current_weight', 0)
                        print(f"   ✅ HX711_1 funktioniert!")
                        print(f"   📊 Current Weight: {current_weight} kg")
                        return True
                    else:
                        print(f"   ❌ HX711_1 nicht bereit")
                        print(f"   💡 Prüfen Sie die Verkabelung!")
                        
            except Exception as e:
                print(f"   ❌ Nicht erreichbar: {e}")
                continue
        
        return False
    
    def verkabelungs_hilfe(self):
        print("\n🔧 VERKABELUNGS-HILFE:")
        print("=" * 40)
        print("📌 ESP8266 NodeMCU Pins:")
        print("   D1 = GPIO5  (CLK)")
        print("   D2 = GPIO4  (DT)")
        print("   5V = VCC Power")
        print("   G  = GND")
        print("")
        print("📌 HX711 Pins:")
        print("   CLK → D1 (GPIO5)")
        print("   DT  → D2 (GPIO4)")
        print("   VCC → 5V") 
        print("   GND → GND")
        print("")
        print("⚡ WICHTIG:")
        print("   • HX711 braucht 5V (nicht 3.3V!)")
        print("   • Kurze, stabile Kabel verwenden")
        print("   • Festen Kontakt sicherstellen")
        
    def kontinuierlicher_test(self):
        print("\n📊 Kontinuierlicher HX711-Test (Ctrl+C zum Stoppen)")
        print("Teste alle 2 Sekunden...")
        print("-" * 50)
        
        try:
            while True:
                timestamp = time.strftime('%H:%M:%S')
                
                # Teste beide IPs
                success = False
                for ip in self.esp_ips:
                    try:
                        response = requests.get(f"http://{ip}/status", timeout=2)
                        if response.status_code == 200:
                            status = response.json()
                            weight_avail = status.get('weight_available', False)
                            current_weight = status.get('current_weight', 0)
                            
                            status_symbol = "✅" if weight_avail else "❌"
                            print(f"[{timestamp}] {ip}: {status_symbol} HX711_1 - Weight: {current_weight:.2f}kg")
                            
                            if weight_avail:
                                success = True
                            break
                    except:
                        continue
                
                if not success:
                    print(f"[{timestamp}] ❌ ESP8266 nicht erreichbar")
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n⏹️  Test gestoppt")

def main():
    tester = SingleHX711Tester()
    
    print("🛠️  ESP8266 Einzelner HX711-Tester")
    print("Menü:")
    print("1. Einmal testen")
    print("2. Verkabelungs-Hilfe")  
    print("3. Kontinuierlicher Test")
    
    while True:
        choice = input("\nWählen Sie (1-3): ").strip()
        
        if choice == '1':
            if tester.test_single_hx711():
                print("\n🎉 HX711_1 funktioniert! Sie können jetzt kalibrieren.")
            else:
                print("\n🔧 HX711_1 Problem - prüfen Sie die Verkabelung.")
                
        elif choice == '2':
            tester.verkabelungs_hilfe()
            
        elif choice == '3':
            tester.kontinuierlicher_test()
            
        else:
            print("Ungültige Eingabe!")

if __name__ == "__main__":
    main()