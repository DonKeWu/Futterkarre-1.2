#!/usr/bin/env python3
"""
🔥 ESP8266 ↔ Pi5 Integration Schnelltest
Testet die Verbindung zwischen Pi5 und ESP8266 mit HX711-Daten
"""

import json
import urllib.request
import urllib.error
import time
import sys

def test_esp8266_connection():
    """Testet ESP8266-Verbindung und HX711-Daten"""
    
    print("🚀 ESP8266 ↔ Pi5 Integration Test")
    print("=" * 50)
    
    # Test-IPs
    test_ips = ["192.168.2.20", "192.168.4.1"]
    esp_found = False
    
    for ip in test_ips:
        print(f"📡 Teste ESP8266 unter {ip}...")
        
        try:
            # Live-Values-Data abrufen
            url = f"http://{ip}/live-values-data"
            req = urllib.request.Request(url, headers={'User-Agent': 'Pi5-Test'})
            
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                print(f"✅ ESP8266 gefunden unter: {ip}")
                print(f"⏰ Timestamp: {data.get('timestamp', 'unbekannt')}ms")
                print("")
                
                # HX711-Status
                print("📊 HX711 Hardware-Status:")
                hx711_modules = [
                    ("VL (D2/D1)", data.get('vl_ready', False), data.get('vl_value', '0')),
                    ("VR (D4/D3)", data.get('vr_ready', False), data.get('vr_value', '0')),  
                    ("HL (D6/D5)", data.get('hl_ready', False), data.get('hl_value', '0')),
                    ("HR (D8/D7)", data.get('hr_ready', False), data.get('hr_value', '0'))
                ]
                
                ready_count = 0
                for name, ready, value in hx711_modules:
                    status_icon = "✅" if ready else "❌"
                    print(f"  {status_icon} {name}: {'Ready' if ready else 'Not Ready'} - Raw: {value}")
                    if ready:
                        ready_count += 1
                
                print("")
                print(f"🎯 Ergebnis: {ready_count}/4 HX711-Module bereit")
                
                if ready_count == 0:
                    print("⚠️  WARNUNG: Keine HX711-Module Ready!")
                    print("   - Hardware angeschlossen?")
                    print("   - 5V Stromversorgung (nicht 3.3V)?")
                elif ready_count < 4:
                    print("ℹ️  INFO: Nur teilweise HX711-Hardware erkannt")
                else:
                    print("🎉 ERFOLG: Alle HX711-Module funktionsfähig!")
                
                # Gewichts-Integration testen
                print("")
                print("⚖️ Gewichts-Integration Test:")
                try:
                    # Vereinfachte Umrechnung (wie in waagen_kalibrierung.py)
                    vl_val = float(data.get('vl_value', '0'))
                    vr_val = float(data.get('vr_value', '0'))
                    hl_val = float(data.get('hl_value', '0'))
                    hr_val = float(data.get('hr_value', '0'))
                    
                    scale_factor = 100000.0  # Vereinfachte Skalierung
                    
                    weights = [
                        vl_val / scale_factor,
                        vr_val / scale_factor,
                        hl_val / scale_factor,
                        hr_val / scale_factor
                    ]
                    
                    total_weight = sum(weights)
                    
                    print(f"  🔢 Einzelgewichte: VL={weights[0]:.3f}, VR={weights[1]:.3f}, HL={weights[2]:.3f}, HR={weights[3]:.3f}")
                    print(f"  ⚖️  Gesamtgewicht: {total_weight:.3f} kg")
                    
                except Exception as e:
                    print(f"  ❌ Gewichts-Berechnung Fehler: {e}")
                
                print("")
                print("🌐 ESP8266 Web-Interfaces:")
                print(f"  • Hauptseite: http://{ip}/")
                print(f"  • Live-Werte: http://{ip}/live-values")
                print(f"  • Hardware-Test: http://{ip}/hardware-test")
                
                esp_found = True
                break
                
        except urllib.error.URLError as e:
            print(f"❌ {ip} nicht erreichbar: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ {ip} JSON-Parse Fehler: {e}")
        except Exception as e:
            print(f"❌ {ip} Unbekannter Fehler: {e}")
        
        print("")
    
    if not esp_found:
        print("🚨 FEHLER: ESP8266 nicht gefunden!")
        print("")
        print("🔧 Troubleshooting:")
        print("  1. ESP8266 eingeschaltet?")
        print("  2. WiFi-Verbindung aktiv?")
        print("  3. IP 192.168.2.20 oder 192.168.4.1?")
        print("  4. Aktuelle Firmware geflasht?")
        print("")
        return False
    
    print("🎉 ESP8266 ↔ Pi5 Integration funktioniert!")
    return True

def test_futterkarre_integration():
    """Testet Futterkarre-Integration"""
    print("\n" + "=" * 50)
    print("🐎 Futterkarre-Integration Test")
    print("=" * 50)
    
    try:
        # Import-Test
        print("📦 Teste Python-Imports...")
        
        from views.waagen_kalibrierung import lese_gewicht_hx711, lese_einzelzellwerte_hx711
        print("✅ waagen_kalibrierung Import erfolgreich")
        
        # Funktions-Test
        print("⚖️ Teste Gewichts-Funktionen...")
        
        total_weight = lese_gewicht_hx711()
        individual_weights = lese_einzelzellwerte_hx711()
        
        print(f"✅ Gesamtgewicht: {total_weight:.3f} kg")
        print(f"✅ Einzelgewichte: {individual_weights}")
        
        print("🎉 Futterkarre-Integration funktioniert!")
        return True
        
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        print("   → Futterkarre-Pfad korrekt?")
        print("   → Dependencies installiert?")
        return False
    except Exception as e:
        print(f"❌ Integration-Fehler: {e}")
        return False

if __name__ == "__main__":
    print("🔥 ESP8266 ↔ Pi5 INTEGRATION SCHNELLTEST")
    print("Testet ob ESP8266 und Pi5 korrekt kommunizieren\n")
    
    # ESP8266-Verbindung testen
    esp_ok = test_esp8266_connection()
    
    # Futterkarre-Integration testen (nur wenn ESP8266 funktioniert)
    if esp_ok:
        futterkarre_ok = test_futterkarre_integration()
        
        if futterkarre_ok:
            print("\n🎯 GESAMTERGEBNIS: ✅ ALLES FUNKTIONIERT!")
            print("🚀 Bereit für Produktions-Einsatz!")
            sys.exit(0)
        else:
            print("\n🎯 GESAMTERGEBNIS: ⚠️ ESP8266 OK, Futterkarre-Integration Probleme")
            sys.exit(1)
    else:
        print("\n🎯 GESAMTERGEBNIS: ❌ ESP8266-Verbindung fehlgeschlagen")
        sys.exit(1)