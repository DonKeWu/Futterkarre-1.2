#!/usr/bin/env python3
"""
Test ESP8266 Dual-Mode WiFi System
Testet beide IP-Adressen (AP und Station) gleichzeitig
"""

import requests
import json
import time
from datetime import datetime

def test_esp8266_dual_mode():
    """Test ESP8266 dual-mode functionality"""
    
    # Test IPs for dual-mode
    ap_ip = "192.168.4.1"      # Futterkarre_WiFi (Access Point)
    station_ip = "192.168.2.17"  # Heimnetz (Station)
    
    print("🔄 ESP8266 Dual-Mode Test gestartet...")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    for ip in [ap_ip, station_ip]:
        print(f"\n📡 Testing {ip}...")
        
        try:
            # HTTP Status API Test
            response = requests.get(f"http://{ip}/status", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS - {ip} responds!")
                
                # Key dual-mode data
                print(f"   📱 Device: {data.get('device_name', 'N/A')}")
                print(f"   📶 WiFi Connected: {data.get('wifi_connected', False)}")
                print(f"   📍 AP IP: {data.get('ap_ip', 'N/A')}")
                print(f"   🏠 Station IP: {data.get('station_ip', 'N/A')}")
                print(f"   📡 Signal: {data.get('signal_strength', 'N/A')} dBm")
                print(f"   🔋 Battery: {data.get('battery_voltage', 'N/A')} V")
                print(f"   ⚡ Free Heap: {data.get('free_heap', 'N/A')} bytes")
                
            else:
                print(f"❌ HTTP Error {response.status_code}")
                
        except requests.exceptions.ConnectTimeout:
            print(f"⏰ Timeout - {ip} nicht erreichbar")
        except requests.exceptions.ConnectionError:
            print(f"🚫 Connection Error - {ip} nicht verfügbar")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Dual-Mode Test abgeschlossen")

def continuous_monitoring():
    """Kontinuierliches Monitoring beider IPs"""
    print("\n🔄 Kontinuierliches Monitoring gestartet (Ctrl+C zum Beenden)")
    
    try:
        while True:
            test_esp8266_dual_mode()
            time.sleep(15)  # 15 Sekunden Pause
    except KeyboardInterrupt:
        print("\n🛑 Monitoring beendet")

if __name__ == "__main__":
    test_esp8266_dual_mode()
    
    # Optional: Kontinuierliches Monitoring
    answer = input("\n❓ Kontinuierliches Monitoring starten? (j/n): ")
    if answer.lower() in ['j', 'ja', 'y', 'yes']:
        continuous_monitoring()