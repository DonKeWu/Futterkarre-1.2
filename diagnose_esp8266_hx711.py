#!/usr/bin/env python3
"""
ESP8266-HX711 Hardware-Diagnose
Analysiert warum weight_available=false ist
"""

import requests
import time
import sys

def diagnose_esp8266_hx711(esp_ip):
    print("🔍 ESP8266-HX711 HARDWARE-DIAGNOSE")
    print("=" * 50)
    print(f"📡 ESP8266 IP: {esp_ip}")
    print()
    
    # Status abrufen
    try:
        response = requests.get(f"http://{esp_ip}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("📊 ESP8266 Status:")
            print(f"   Device: {data.get('device_name', 'UNBEKANNT')}")
            print(f"   Firmware: {data.get('firmware_version', 'UNBEKANNT')}")
            print(f"   WiFi: {'✅ Verbunden' if data.get('wifi_connected', False) else '❌ Getrennt'}")
            print(f"   Uptime: {data.get('uptime', 0)/1000:.1f} Sekunden")
            print(f"   Free Heap: {data.get('free_heap', 0)} Bytes")
            
            # KRITISCH: HX711 Status
            weight_available = data.get('weight_available', False)
            print(f"\n🎯 HX711 Status: {'✅ FUNKTIONIERT' if weight_available else '❌ NICHT VERFÜGBAR'}")
            
            if not weight_available:
                print("\n🚨 PROBLEM IDENTIFIZIERT:")
                print("   Der ESP8266 kann NICHT mit dem HX711 kommunizieren!")
                print()
                print("🔧 MÖGLICHE URSACHEN:")
                print("   1. ❌ HX711 hat keine Stromversorgung (VCC/GND)")
                print("   2. ❌ Falsche Pin-Verbindung D6/D7")
                print("   3. ❌ Wägezelle nicht angeschlossen (E+/E-/A+/A-)")
                print("   4. ❌ HX711-Modul defekt")
                print("   5. ❌ ESP8266 Pin-Konfiguration falsch")
                print()
                print("🔍 PRÜFSCHRITTE:")
                print("   1. Multimeter: HX711 VCC → 3.3V oder 5V")
                print("   2. Multimeter: HX711 GND → ESP8266 GND")
                print("   3. Visuell: D6 → HX711 DT")
                print("   4. Visuell: D7 → HX711 SCK")
                print("   5. Wägezelle: 4 Drähte korrekt an E+/E-/A+/A-")
                
        else:
            print(f"❌ ESP8266 Status-Fehler: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Verbindungsfehler: {e}")
        return False
    
    return not data.get('weight_available', False)  # True wenn Problem besteht

def test_multiple_requests(esp_ip):
    """Teste mehrfach um sicherzustellen dass das Problem konsistent ist"""
    print("\n📈 KONSISTENZ-TEST (5 Abfragen)...")
    
    weight_states = []
    for i in range(5):
        try:
            response = requests.get(f"http://{esp_ip}/status", timeout=3)
            if response.status_code == 200:
                data = response.json()
                weight_available = data.get('weight_available', False)
                weight_states.append(weight_available)
                print(f"   Test {i+1}: weight_available = {weight_available}")
            else:
                print(f"   Test {i+1}: HTTP Error {response.status_code}")
                
        except Exception as e:
            print(f"   Test {i+1}: Fehler - {e}")
            
        time.sleep(1)
    
    if weight_states:
        all_false = all(not state for state in weight_states)
        print(f"\n📋 ERGEBNIS: {'❌ KONSISTENT FALSE' if all_false else '⚠️  INKONSISTENT'}")
        
        if all_false:
            print("   → Das HX711-Problem ist DAUERHAFT!")
            print("   → Hardware-Überprüfung erforderlich!")
            
        return all_false
    
    return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python diagnose_esp8266_hx711.py <ESP8266_IP>")
        print("Beispiel: python diagnose_esp8266_hx711.py 192.168.2.20")
        sys.exit(1)
    
    esp_ip = sys.argv[1]
    
    # Hauptdiagnose
    problem_detected = diagnose_esp8266_hx711(esp_ip)
    
    if problem_detected:
        # Konsistenz-Test
        consistent_problem = test_multiple_requests(esp_ip)
        
        if consistent_problem:
            print("\n" + "🚨" * 20)
            print("DIAGNOSE ABGESCHLOSSEN: HX711 HARDWARE-PROBLEM!")
            print("🚨" * 20)
            print("\nNÄCHSTE SCHRITTE:")
            print("1. 🔌 Überprüfe HX711-Stromversorgung mit Multimeter")
            print("2. 📏 Prüfe alle Kabelverbindungen D6/D7")
            print("3. 🎯 Teste HX711 mit anderem ESP8266/Arduino")
            print("4. 🔄 Falls alles OK: ESP8266-Firmware neu flashen")
    else:
        print("\n✅ HX711 funktioniert korrekt!")

if __name__ == "__main__":
    main()