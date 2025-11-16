#!/usr/bin/env python3
"""
Einfacher ESP8266 HTTP Monitor (ohne WebSockets)
Funktioniert sofort nach dem Flash - kein async/await
"""

import requests
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import logging

logging.basicConfig(level=logging.INFO)

class SimpleESP8266Monitor(QWidget):
    def __init__(self):
        super().__init__()
        self.esp_ip = None
        self.init_ui()
        
        # Auto-Discovery Timer
        self.discovery_timer = QTimer()
        self.discovery_timer.timeout.connect(self.find_esp8266)
        self.discovery_timer.start(5000)  # Alle 5 Sekunden
        
        # Status Timer  
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(2000)  # Alle 2 Sekunden
        
    def init_ui(self):
        self.setWindowTitle("🔧 ESP8266 Simple Monitor")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
        # Status Display
        self.status_label = QLabel("🔍 ESP8266 suchen...")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: orange;")
        layout.addWidget(self.status_label)
        
        # Data Display
        self.data_text = QTextEdit()
        self.data_text.setReadOnly(True)
        layout.addWidget(self.data_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.btn_tare = QPushButton("⚖️ Tare")
        self.btn_tare.clicked.connect(self.tare_scale)
        button_layout.addWidget(self.btn_tare)
        
        self.btn_calibrate = QPushButton("🔧 Kalibrieren")
        self.btn_calibrate.clicked.connect(self.calibrate_scale) 
        button_layout.addWidget(self.btn_calibrate)
        
        self.btn_test = QPushButton("🧪 Test")
        self.btn_test.clicked.connect(self.test_connection)
        button_layout.addWidget(self.btn_test)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def find_esp8266(self):
        """ESP8266 per HTTP finden"""
        # Test IPs
        test_ips = [
            "192.168.4.1",      # Stall-Modus
            "192.168.2.100",    # Haus-Modus
            "192.168.2.101",
            "192.168.2.110"
        ]
        
        for ip in test_ips:
            if self.test_http_connection(ip):
                if self.esp_ip != ip:
                    self.esp_ip = ip
                    mode = "Stall" if ip == "192.168.4.1" else "Haus" 
                    self.status_label.setText(f"✅ ESP8266: {ip} ({mode})")
                    self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
                    self.log(f"🎯 ESP8266 gefunden: {ip}")
                return True
        
        # Nicht gefunden
        if self.esp_ip:
            self.esp_ip = None
            self.status_label.setText("❌ ESP8266 nicht gefunden")
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
        
        return False
            
    def test_http_connection(self, ip: str, timeout: float = 1.0) -> bool:
        """Teste HTTP-Verbindung"""
        try:
            url = f"http://{ip}/status"
            response = requests.get(url, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("device") == "FutterWaage_ESP8266"
            
        except Exception:
            pass
            
        return False
    
    def update_status(self):
        """Status aktualisieren"""
        if not self.esp_ip:
            return
            
        try:
            url = f"http://{self.esp_ip}/status"
            response = requests.get(url, timeout=2.0)
            
            if response.status_code == 200:
                data = response.json()
                
                # Status formatieren
                status_text = f"""
🔧 ESP8266 Status ({self.esp_ip}):
════════════════════════════════════

📊 System:
  • Device: {data.get('device', 'Unknown')}
  • Uptime: {data.get('uptime', 0)} Sekunden
  • Free Heap: {data.get('free_heap', 0)} Bytes
  • WiFi RSSI: {data.get('wifi_rssi', 0)} dBm

⚖️ Waage:
  • Gewicht: {data.get('weight', 0):.2f} kg
  • Raw Value: {data.get('weight_raw', 0)}
  • Kalibriert: {'✅' if data.get('calibrated', False) else '❌'}
  • Tare Offset: {data.get('tare_offset', 0)}

🌡️ Sensoren:
  • Temperature: {data.get('temperature', 0):.1f}°C

📡 WiFi:
  • SSID: {data.get('wifi_ssid', 'Unknown')}
  • IP: {data.get('ip', 'Unknown')}
  • Mode: {data.get('wifi_mode', 'Unknown')}

⏰ Timestamp: {data.get('timestamp', 'Unknown')}
"""
                
                self.data_text.setPlainText(status_text)
                
            else:
                self.log(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ Status Update Fehler: {e}")
    
    def tare_scale(self):
        """Waage tarieren"""
        if not self.esp_ip:
            self.log("❌ Keine ESP8266 Verbindung")
            return
            
        try:
            url = f"http://{self.esp_ip}/tare"
            response = requests.post(url, timeout=3.0)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log("✅ Waage tariert")
                else:
                    self.log(f"❌ Tare fehlgeschlagen: {data.get('message')}")
            else:
                self.log(f"❌ Tare HTTP Error: {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ Tare Fehler: {e}")
    
    def calibrate_scale(self):
        """Waage kalibrieren"""
        weight, ok = QInputDialog.getDouble(
            self, "Kalibrierung", 
            "Bekanntes Gewicht eingeben (kg):", 
            1.0, 0.1, 100.0, 2
        )
        
        if not ok or not self.esp_ip:
            return
            
        try:
            url = f"http://{self.esp_ip}/calibrate"
            data = {"weight": weight}
            response = requests.post(url, json=data, timeout=5.0)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log(f"✅ Kalibrierung erfolgreich mit {weight}kg")
                else:
                    self.log(f"❌ Kalibrierung fehlgeschlagen: {result.get('message')}")
            else:
                self.log(f"❌ Kalibrierung HTTP Error: {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ Kalibrierung Fehler: {e}")
    
    def test_connection(self):
        """Verbindung testen"""
        if not self.esp_ip:
            self.log("❌ Keine ESP8266 IP gefunden")
            return
            
        self.log(f"🧪 Teste Verbindung zu {self.esp_ip}...")
        
        # Ping Test
        import subprocess
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '1', self.esp_ip],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                self.log("✅ Ping erfolgreich")
            else:
                self.log("❌ Ping fehlgeschlagen")
                
        except Exception as e:
            self.log(f"❌ Ping Fehler: {e}")
        
        # HTTP Test
        if self.test_http_connection(self.esp_ip, 3.0):
            self.log("✅ HTTP-Verbindung OK")
        else:
            self.log("❌ HTTP-Verbindung fehlgeschlagen")
    
    def log(self, message: str):
        """Log-Nachricht ausgeben"""
        print(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    monitor = SimpleESP8266Monitor()
    monitor.show()
    
    print("🔧 ESP8266 Simple Monitor gestartet")
    print("📡 HTTP-basiertes Monitoring (kein WebSocket)")
    print("🔍 Auto-Discovery läuft...")
    
    sys.exit(app.exec_())