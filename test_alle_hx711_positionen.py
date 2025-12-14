#!/usr/bin/env python3
"""
ESP8266 Alle HX711-Positionen Tester
Testet systematisch alle 4 HX711-Anschlüsse
"""

import requests
import time
import json

class AllHX711PositionsTester:
    def __init__(self):
        self.esp_ips = ["192.168.2.20", "192.168.4.1"]
        self.hx711_configs = {
            "HX711_1": {"clk_pin": "D1 (GPIO5)", "dt_pin": "D2 (GPIO4)"},
            "HX711_2": {"clk_pin": "D3 (GPIO0)", "dt_pin": "D4 (GPIO2)"},
            "HX711_3": {"clk_pin": "D5 (GPIO14)", "dt_pin": "D6 (GPIO12)"},
            "HX711_4": {"clk_pin": "D7 (GPIO13)", "dt_pin": "D8 (GPIO15)"}
        }
        
    def test_single_position(self, position_name):
        """Testet eine spezifische HX711-Position"""
        print(f"\n🔍 TESTE {position_name}")
        print("=" * 50)
        
        config = self.hx711_configs[position_name]
        print(f"📋 Verkabelung für {position_name}:")
        print(f"   CLK → {config['clk_pin']}")
        print(f"   DT  → {config['dt_pin']}")
        print(f"   VCC → 5V")
        print(f"   GND → GND")
        print("-" * 30)
        
        # Teste ESP8266 Status
        for ip in self.esp_ips:
            try:
                response = requests.get(f"http://{ip}/status", timeout=3)
                if response.status_code == 200:
                    status = response.json()
                    
                    print(f"✅ ESP8266 ({ip}) erreichbar")
                    print(f"   Device: {status.get('device_name', 'Unknown')}")
                    
                    weight_avail = status.get('weight_available', False)
                    current_weight = status.get('current_weight', 0)
                    
                    if weight_avail:
                        print(f"   🎉 {position_name} FUNKTIONIERT!")
                        print(f"   📊 Gewicht: {current_weight} kg")
                        return True, ip, current_weight
                    else:
                        print(f"   ❌ {position_name} nicht bereit")
                        print(f"   💡 Kabel an {config['clk_pin']} und {config['dt_pin']} prüfen")
                        
            except Exception as e:
                print(f"   ❌ ESP8266 ({ip}) nicht erreichbar: {e}")
                continue
        
        return False, None, 0
    
    def test_all_positions_sequentially(self):
        """Testet alle Positionen nacheinander"""
        print("🧪 SEQUENZIELLER TEST ALLER HX711-POSITIONEN")
        print("=" * 60)
        
        results = {}
        
        for position in ["HX711_1", "HX711_2", "HX711_3", "HX711_4"]:
            success, ip, weight = self.test_single_position(position)
            results[position] = {"success": success, "ip": ip, "weight": weight}
            
            if success:
                print(f"\n✅ {position} ERFOLGREICH auf {ip}")
                
                # Warte auf Benutzer-Bestätigung für nächste Position
                if position != "HX711_4":  # Nicht beim letzten
                    input(f"\n👆 Stecken Sie jetzt den HX711 von {position} auf die NÄCHSTE Position um und drücken ENTER...")
            else:
                print(f"\n❌ {position} NICHT GEFUNDEN")
                if position != "HX711_4":
                    retry = input(f"\n🔄 Retry {position}? (j/N): ").strip().lower()
                    if retry == 'j':
                        success, ip, weight = self.test_single_position(position)
                        results[position] = {"success": success, "ip": ip, "weight": weight}
        
        # Ergebnisse zusammenfassen
        self.print_summary(results)
        
    def print_summary(self, results):
        """Zeigt Zusammenfassung aller Tests"""
        print("\n" + "=" * 60)
        print("📊 ZUSAMMENFASSUNG ALLER HX711-POSITIONEN")
        print("=" * 60)
        
        working_positions = []
        failed_positions = []
        
        for position, result in results.items():
            config = self.hx711_configs[position]
            status = "✅ FUNKTIONIERT" if result["success"] else "❌ NICHT GEFUNDEN"
            
            print(f"{position:10} | {status:15} | CLK: {config['clk_pin']:12} | DT: {config['dt_pin']}")
            
            if result["success"]:
                working_positions.append(position)
                print(f"            | Gewicht: {result['weight']:.2f} kg")
            else:
                failed_positions.append(position)
        
        print("\n" + "=" * 60)
        print(f"✅ Funktionsfähig: {len(working_positions)} von 4 Positionen")
        print(f"❌ Problematisch:   {len(failed_positions)} von 4 Positionen")
        
        if working_positions:
            print(f"\n🎉 Funktionierende Positionen: {', '.join(working_positions)}")
        
        if failed_positions:
            print(f"\n🔧 Zu prüfende Positionen: {', '.join(failed_positions)}")
            print("💡 Verkabelung und Lötstellen kontrollieren!")
    
    def quick_position_check(self):
        """Schneller Check welche Position gerade angeschlossen ist"""
        print("⚡ SCHNELL-CHECK: Welche Position ist angeschlossen?")
        print("=" * 50)
        
        for ip in self.esp_ips:
            try:
                response = requests.get(f"http://{ip}/status", timeout=2)
                if response.status_code == 200:
                    status = response.json()
                    
                    if status.get('weight_available', False):
                        weight = status.get('current_weight', 0)
                        print(f"✅ ESP8266 ({ip}): HX711 aktiv - Gewicht: {weight} kg")
                        print("💡 Diese Position funktioniert!")
                        return True
                    else:
                        print(f"❌ ESP8266 ({ip}): Kein HX711 erkannt")
                        
            except Exception as e:
                print(f"❌ ESP8266 ({ip}) nicht erreichbar: {e}")
        
        print("🔧 Keine funktionsfähige HX711-Position gefunden")
        return False
    
    def continuous_monitoring(self):
        """Kontinuierliche Überwachung für Live-Debugging"""
        print("\n📊 KONTINUIERLICHE ÜBERWACHUNG")
        print("Überwacht alle 2 Sekunden - Ctrl+C zum Stoppen")
        print("-" * 60)
        
        try:
            while True:
                timestamp = time.strftime('%H:%M:%S')
                
                found_active = False
                for ip in self.esp_ips:
                    try:
                        response = requests.get(f"http://{ip}/status", timeout=1.5)
                        if response.status_code == 200:
                            status = response.json()
                            weight_avail = status.get('weight_available', False)
                            weight = status.get('current_weight', 0)
                            
                            if weight_avail:
                                print(f"[{timestamp}] ✅ {ip}: HX711 aktiv - {weight:.2f} kg")
                                found_active = True
                            else:
                                print(f"[{timestamp}] ❌ {ip}: Kein HX711")
                            break
                    except:
                        continue
                
                if not found_active:
                    print(f"[{timestamp}] 🔧 Kein aktiver HX711 gefunden")
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n⏹️ Überwachung gestoppt")

def main():
    tester = AllHX711PositionsTester()
    
    print("🛠️ ESP8266 HX711-Positionen Tester")
    print("=" * 50)
    print("MENÜ:")
    print("1. Alle Positionen sequenziell testen")
    print("2. Schnell-Check (aktuelle Position)")
    print("3. Kontinuierliche Überwachung")
    print("4. Pin-Übersicht anzeigen")
    
    while True:
        choice = input("\nWählen Sie (1-4): ").strip()
        
        if choice == '1':
            print("\n🎯 STARTET SEQUENZIELLEN TEST")
            print("Sie werden aufgefordert, den HX711 zwischen den Positionen umzustecken.")
            input("🔌 Stellen Sie sicher, dass der HX711 an Position 1 (D1/D2) angeschlossen ist und drücken ENTER...")
            tester.test_all_positions_sequentially()
            
        elif choice == '2':
            tester.quick_position_check()
            
        elif choice == '3':
            tester.continuous_monitoring()
            
        elif choice == '4':
            print("\n📋 ESP8266 NodeMCU HX711-PIN ÜBERSICHT:")
            print("=" * 50)
            for position, config in tester.hx711_configs.items():
                print(f"{position}: CLK → {config['clk_pin']}, DT → {config['dt_pin']}")
            print("\nZusätzlich für alle:")
            print("VCC → 5V, GND → GND")
            
        else:
            print("❌ Ungültige Eingabe!")

if __name__ == "__main__":
    main()