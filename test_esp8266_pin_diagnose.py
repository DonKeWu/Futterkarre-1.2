#!/usr/bin/env python3
"""
ESP8266 Pin-Diagnose für HX711
Testet ob der ESP8266 überhaupt Signale auf den HX711-Pins empfängt
"""

import requests
import time
import json
import sys

class ESP8266PinDiagnose:
    def __init__(self, esp_ip):
        self.esp_ip = esp_ip
        self.base_url = f"http://{esp_ip}"
        
    def test_pin_status(self):
        """Testet den Status der HX711-Pins"""
        print("🔍 ESP8266 Pin-Diagnose gestartet...")
        print(f"📡 ESP8266 IP: {self.esp_ip}")
        print("🔌 HX711 Pins: D6 (DT/Data), D7 (SCK/Clock)")
        print("-" * 50)
        
        try:
            # Pin-Status abfragen
            response = requests.get(f"{self.base_url}/pin-status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ Pin-Status erfolgreich empfangen:")
                print(f"   D6 (HX711-DT):  {data.get('d6_status', 'UNBEKANNT')}")
                print(f"   D7 (HX711-SCK): {data.get('d7_status', 'UNBEKANNT')}")
                return True
            else:
                print(f"❌ Pin-Status Fehler: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Verbindungsfehler: {e}")
            return False
    
    def test_hx711_communication(self):
        """Testet die HX711-Kommunikation direkt"""
        print("\n🔧 HX711 Kommunikations-Test...")
        
        try:
            response = requests.get(f"{self.base_url}/hx711-raw", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                raw_value = data.get('raw_value', 0)
                is_ready = data.get('is_ready', False)
                pin_dt = data.get('pin_dt_state', 'UNBEKANNT')
                pin_sck = data.get('pin_sck_state', 'UNBEKANNT')
                
                print(f"📊 HX711 Raw-Wert: {raw_value}")
                print(f"🚦 HX711 Ready: {'✅ JA' if is_ready else '❌ NEIN'}")
                print(f"📌 DT-Pin (D6): {pin_dt}")
                print(f"📌 SCK-Pin (D7): {pin_sck}")
                
                if raw_value == 0 and not is_ready:
                    print("\n⚠️  DIAGNOSE: HX711 antwortet nicht!")
                    print("   Mögliche Ursachen:")
                    print("   • Keine Stromversorgung am HX711")
                    print("   • Falsche Verkabelung D6/D7")
                    print("   • HX711-Modul defekt")
                    print("   • Wägezelle nicht angeschlossen")
                    
                return True
            else:
                print(f"❌ HX711-Test Fehler: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ HX711-Test fehlgeschlagen: {e}")
            return False
    
    def test_pin_waveform(self):
        """Testet Pin-Signale über Zeit"""
        print("\n📈 Pin-Signal-Analyse (10 Sekunden)...")
        
        signals = []
        for i in range(10):
            try:
                response = requests.get(f"{self.base_url}/pin-signals", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    signals.append({
                        'time': i,
                        'd6': data.get('d6_level', 0),
                        'd7': data.get('d7_level', 0),
                        'hx711_ready': data.get('hx711_ready', False)
                    })
                    print(f"   {i+1:2d}s: D6={data.get('d6_level', 0)} D7={data.get('d7_level', 0)} Ready={data.get('hx711_ready', False)}")
                else:
                    print(f"   {i+1:2d}s: ❌ Keine Antwort")
                    
                time.sleep(1)
                
            except Exception as e:
                print(f"   {i+1:2d}s: ❌ Fehler: {e}")
        
        # Analyse der Signale
        if signals:
            d6_changes = len(set(s['d6'] for s in signals)) > 1
            d7_changes = len(set(s['d7'] for s in signals)) > 1
            ready_changes = len(set(s['hx711_ready'] for s in signals)) > 1
            
            print(f"\n📋 Signal-Analyse:")
            print(f"   D6-Pin Aktivität: {'✅ JA' if d6_changes else '❌ NEIN'}")
            print(f"   D7-Pin Aktivität: {'✅ JA' if d7_changes else '❌ NEIN'}")
            print(f"   HX711-Ready wechselt: {'✅ JA' if ready_changes else '❌ NEIN'}")
            
            if not any([d6_changes, d7_changes, ready_changes]):
                print("\n🚨 KRITISCH: Keine Pin-Aktivität erkannt!")
                print("   Das HX711 kommuniziert NICHT mit dem ESP8266!")
    
    def full_diagnosis(self):
        """Vollständige ESP8266-HX711 Diagnose"""
        print("🔍 ESP8266-HX711 VOLLDIAGNOSE")
        print("=" * 50)
        
        # 1. Basis-Verbindung
        try:
            response = requests.get(f"{self.base_url}/status", timeout=5)
            if response.status_code == 200:
                print("✅ ESP8266 ist erreichbar")
            else:
                print("❌ ESP8266 antwortet nicht korrekt")
                return False
        except:
            print("❌ ESP8266 ist nicht erreichbar!")
            return False
        
        # 2. Pin-Status
        self.test_pin_status()
        
        # 3. HX711-Kommunikation  
        self.test_hx711_communication()
        
        # 4. Signal-Analyse
        self.test_pin_waveform()
        
        print("\n" + "=" * 50)
        print("🏁 Diagnose abgeschlossen")


def main():
    if len(sys.argv) != 2:
        print("Usage: python test_esp8266_pin_diagnose.py <ESP8266_IP>")
        print("Beispiel: python test_esp8266_pin_diagnose.py 192.168.2.20")
        sys.exit(1)
    
    esp_ip = sys.argv[1]
    diagnose = ESP8266PinDiagnose(esp_ip)
    diagnose.full_diagnosis()


if __name__ == "__main__":
    main()