#!/usr/bin/env python3
"""
ESP8266 Dual-HX711 Schnell-Test
Testet beide HX711 ohne ESP8266 neu zu flashen
"""

import requests
import time

def test_dual_hx711():
    esp_ip = "192.168.2.20"
    print("🔧 ESP8266 Dual-HX711 Schnell-Test")
    print("=" * 40)
    
    # Test 1: Basis-Verbindung
    try:
        response = requests.get(f"http://{esp_ip}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ESP8266 erreichbar: {data.get('device_name', 'ESP8266')}")
            print(f"📊 Weight Available: {data.get('weight_available', False)}")
        else:
            print("❌ ESP8266 antwortet nicht korrekt")
            return
    except:
        print("❌ ESP8266 nicht erreichbar!")
        return
    
    # Test 2: Versuche vorhandene Endpunkte
    endpoints = ["/weight", "/raw", "/calibrate", "/data", "/hx711", "/test"]
    
    print("\n🔍 Teste verfügbare Endpunkte...")
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://{esp_ip}{endpoint}", timeout=3)
            if response.status_code == 200:
                print(f"✅ {endpoint}: {response.text[:100]}...")
            else:
                print(f"❌ {endpoint}: HTTP {response.status_code}")
        except:
            print(f"❌ {endpoint}: Timeout/Fehler")
    
    print("\n📋 DIAGNOSE:")
    if not data.get('weight_available', False):
        print("❌ HX711 noch immer nicht verfügbar!")
        print("\n🔧 VERKABELUNGS-CHECK:")
        print("   HL (Links):  ESP D6→HX711-DT, ESP D7→HX711-SCK")
        print("   HR (Rechts): ESP D8→HX711-DT, ESP D5→HX711-SCK") 
        print("   Beide:       ESP VIN→HX711-VCC, ESP GND→HX711-GND")
        print("\n⚡ STROMVERSORGUNG:")
        print("   Beide HX711-LEDs leuchten?")
        print("   Wägezellen angeschlossen?")
    else:
        print("✅ HX711 ist verfügbar!")

if __name__ == "__main__":
    test_dual_hx711()