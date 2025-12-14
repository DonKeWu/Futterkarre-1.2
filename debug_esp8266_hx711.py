#!/usr/bin/env python3
"""
ESP8266 HX711 Debug Tool
Testet einzelne HX711-Sensoren über ESP8266-API
"""

import requests
import json
import time
import sys

class ESP8266HX711Debugger:
    def __init__(self, esp_ip="192.168.2.20"):
        self.esp_ip = esp_ip
        self.base_url = f"http://{esp_ip}"
        
    def get_status(self):
        """Holt ESP8266-Status"""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=3)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Status-Fehler: {e}")
            return None
    
    def test_connection(self):
        """Testet ESP8266-Verbindung"""
        print(f"🔍 Teste ESP8266-Verbindung zu {self.esp_ip}...")
        
        status = self.get_status()
        if status:
            print("✅ ESP8266 erreichbar")
            print(f"   Device: {status.get('device_name')}")
            print(f"   Firmware: {status.get('firmware_version')}")
            print(f"   WiFi Signal: {status.get('signal_strength')} dBm")
            print(f"   Uptime: {status.get('uptime', 0) // 1000} Sekunden")
            print(f"   Weight Available: {status.get('weight_available')}")
            return True
        else:
            print("❌ ESP8266 nicht erreichbar")
            return False
    
    def send_hx711_debug_command(self):
        """Sendet Debug-Kommando für HX711-Status"""
        try:
            # Versuche verschiedene Debug-APIs
            debug_urls = [
                f"{self.base_url}/debug_hx711",
                f"{self.base_url}/sensor_status", 
                f"{self.base_url}/raw_values"
            ]
            
            for url in debug_urls:
                try:
                    response = requests.get(url, timeout=3)
                    if response.status_code == 200:
                        print(f"✅ Debug-API gefunden: {url}")
                        print(f"Response: {response.text}")
                        return response.json()
                except:
                    continue
            
            print("❌ Keine HX711-Debug-API gefunden")
            return None
            
        except Exception as e:
            print(f"❌ Debug-Kommando Fehler: {e}")
            return None
    
    def test_raw_sensor_read(self):
        """Testet Raw-Sensor-Werte"""
        print("\n🔧 Teste Raw-Sensor-Lesungen...")
        
        # Mehrere Versuche
        for i in range(5):
            print(f"\n📊 Versuch {i+1}/5:")
            status = self.get_status()
            
            if status:
                weight_avail = status.get('weight_available', False)
                current_weight = status.get('current_weight', 0)
                
                print(f"   Weight Available: {weight_avail}")
                print(f"   Current Weight: {current_weight} kg")
                
                if weight_avail and current_weight != 0:
                    print("✅ HX711 liefert Daten!")
                    return True
                else:
                    print("⚠️  HX711 keine Daten")
            
            time.sleep(2)
        
        return False
    
    def analyze_hx711_problem(self):
        """Analysiert HX711-Probleme"""
        print("\n🔍 HX711-Problem-Analyse:")
        print("=" * 40)
        
        # 1. Basis-Verbindung
        if not self.test_connection():
            return
        
        # 2. Status prüfen
        status = self.get_status()
        if not status:
            return
            
        if not status.get('weight_available', False):
            print("\n❌ PROBLEM IDENTIFIZIERT: HX711 nicht bereit")
            print("\n💡 MÖGLICHE URSACHEN:")
            print("   1. HX711 nicht richtig verkabelt")
            print("   2. Falsche Pin-Zuordnung in ESP8266-Code")
            print("   3. HX711-Stromversorgung unzureichend")  
            print("   4. ESP8266-Pins beschädigt")
            print("   5. HX711-Module defekt")
            
            print("\n🔧 LÖSUNGSVORSCHLÄGE:")
            print("   1. Verkabelung prüfen:")
            print("      • VCC → 5V")
            print("      • GND → GND") 
            print("      • DT → D2 (GPIO4)")
            print("      • SCK → D1 (GPIO5)")
            print("   2. ESP8266 Serial Monitor checken")
            print("   3. HX711 mit Multimeter messen")
            
        # 3. Raw-Sensor-Test
        self.test_raw_sensor_read()
    
    def interactive_debug(self):
        """Interaktives Debug-Menü"""
        print("\n🛠️  ESP8266 HX711 Interactive Debugger")
        print("=" * 50)
        
        while True:
            print("\nVerfügbare Commands:")
            print("1. Status prüfen")
            print("2. Raw-Sensor-Test")
            print("3. Problem-Analyse")
            print("4. Kontinuierlicher Monitor")
            print("q. Quit")
            
            choice = input("\nWählen Sie (1-4, q): ").strip()
            
            if choice == '1':
                self.test_connection()
            elif choice == '2':
                self.test_raw_sensor_read()
            elif choice == '3':
                self.analyze_hx711_problem()
            elif choice == '4':
                self.continuous_monitor()
            elif choice.lower() == 'q':
                break
            else:
                print("Ungültige Eingabe!")
    
    def continuous_monitor(self):
        """Kontinuierlicher Monitor"""
        print("\n📊 Kontinuierlicher HX711-Monitor (Ctrl+C zum Stoppen)")
        print("-" * 50)
        
        try:
            while True:
                status = self.get_status()
                if status:
                    timestamp = time.strftime('%H:%M:%S')
                    weight_avail = status.get('weight_available', False)
                    weight = status.get('current_weight', 0)
                    
                    status_symbol = "✅" if weight_avail else "❌"
                    print(f"[{timestamp}] {status_symbol} Weight: {weight:.2f}kg Available: {weight_avail}")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] ❌ ESP8266 nicht erreichbar")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⏹️  Monitor gestoppt")

def main():
    # ESP8266-IP aus Argumenten oder Default
    esp_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.2.20"
    
    debugger = ESP8266HX711Debugger(esp_ip)
    
    if len(sys.argv) > 2 and sys.argv[2] == "auto":
        # Automatische Analyse
        debugger.analyze_hx711_problem()
    else:
        # Interaktives Menü
        debugger.interactive_debug()

if __name__ == "__main__":
    main()