#!/usr/bin/env python3
"""
ESP8266 Serial Diagnose Logger
Analysiert warum ESP8266 keine WiFi-Verbindung aufbaut

Verwendung:
1. ESP8266 per USB verbinden
2. python esp8266_diagnose.py
3. Diagnose-Log wird erstellt und analysiert
"""

import serial
import time
import re
import json
from datetime import datetime
import sys

class ESP8266Diagnose:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.log_data = []
        self.analysis = {
            'wifi_attempts': 0,
            'wifi_connected': False,
            'ap_mode_started': False,
            'boot_successful': False,
            'errors': [],
            'warnings': [],
            'network_scans': [],
            'ip_addresses': []
        }
        
    def connect_serial(self):
        """Verbindung zum ESP8266 herstellen"""
        try:
            print(f"🔌 Verbinde zu {self.port} @ {self.baudrate} Baud...")
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # ESP8266 Zeit zum Starten geben
            print("✅ Serial-Verbindung hergestellt")
            return True
        except Exception as e:
            print(f"❌ Serial-Verbindung fehlgeschlagen: {e}")
            return False
    
    def read_and_analyze(self, duration_seconds=60):
        """ESP8266 Output lesen und analysieren"""
        if not self.serial_conn:
            print("❌ Keine Serial-Verbindung")
            return
            
        print(f"📊 Starte Diagnose für {duration_seconds} Sekunden...")
        print("🔍 Suche nach:")
        print("   • Boot-Nachrichten")
        print("   • WiFi-Verbindungsversuche") 
        print("   • Fehlermeldungen")
        print("   • AP-Modus Start")
        print("   • IP-Adressen")
        print("\n" + "="*60)
        
        start_time = time.time()
        
        while (time.time() - start_time) < duration_seconds:
            try:
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        log_entry = f"[{timestamp}] {line}"
                        print(log_entry)
                        self.log_data.append(log_entry)
                        self.analyze_line(line)
                        
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\n⏹️ Diagnose durch Benutzer beendet")
                break
            except Exception as e:
                print(f"⚠️ Lesefehler: {e}")
        
        print("\n" + "="*60)
        self.generate_report()
    
    def analyze_line(self, line):
        """Einzelne Log-Zeile analysieren"""
        line_lower = line.lower()
        
        # Boot-Nachrichten
        if 'ready' in line_lower or 'boot' in line_lower or 'starting' in line_lower:
            self.analysis['boot_successful'] = True
            
        # WiFi-Verbindungsversuche
        if 'wifi' in line_lower and ('connect' in line_lower or 'connecting' in line_lower):
            self.analysis['wifi_attempts'] += 1
            
        # WiFi erfolgreich verbunden
        if 'wifi connected' in line_lower or 'connected to' in line_lower:
            self.analysis['wifi_connected'] = True
            
        # AP-Modus gestartet
        if 'ap mode' in line_lower or 'access point' in line_lower or 'softap' in line_lower:
            self.analysis['ap_mode_started'] = True
            
        # IP-Adressen finden
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, line)
        for ip in ips:
            if ip not in self.analysis['ip_addresses'] and not ip.startswith('0.0'):
                self.analysis['ip_addresses'].append(ip)
        
        # Fehlermeldungen
        if any(error in line_lower for error in ['error', 'failed', 'timeout', 'exception']):
            self.analysis['errors'].append(line)
            
        # Warnungen
        if any(warn in line_lower for warn in ['warning', 'warn', 'retry', 'disconnect']):
            self.analysis['warnings'].append(line)
            
        # Netzwerk-Scans
        if 'scan' in line_lower and ('network' in line_lower or 'ssid' in line_lower):
            self.analysis['network_scans'].append(line)
    
    def generate_report(self):
        """Diagnose-Bericht erstellen"""
        print("\n🔍 ESP8266 DIAGNOSE-BERICHT")
        print("="*60)
        
        # Grundstatus
        print(f"📊 Boot erfolgreich: {'✅' if self.analysis['boot_successful'] else '❌'}")
        print(f"📡 WiFi-Verbindungsversuche: {self.analysis['wifi_attempts']}")
        print(f"🌐 WiFi verbunden: {'✅' if self.analysis['wifi_connected'] else '❌'}")
        print(f"📻 AP-Modus gestartet: {'✅' if self.analysis['ap_mode_started'] else '❌'}")
        
        # IP-Adressen
        if self.analysis['ip_addresses']:
            print(f"🏠 Gefundene IP-Adressen: {', '.join(self.analysis['ip_addresses'])}")
        else:
            print("🏠 Keine IP-Adressen gefunden")
            
        print("\n🚨 PROBLEM-DIAGNOSE:")
        print("-" * 40)
        
        # Hauptproblem identifizieren
        if not self.analysis['boot_successful']:
            print("❌ HAUPTPROBLEM: ESP8266 bootet nicht richtig")
            print("   → Stromversorgung prüfen")
            print("   → Flash-Speicher korrupt?")
            print("   → Hardware-Reset versuchen")
            
        elif self.analysis['wifi_attempts'] == 0:
            print("❌ HAUPTPROBLEM: Keine WiFi-Verbindungsversuche")
            print("   → Code läuft nicht oder WiFi-Init fehlt")
            print("   → Serial Monitor Baudrate prüfen (115200)")
            
        elif self.analysis['wifi_attempts'] > 0 and not self.analysis['wifi_connected']:
            print("❌ HAUPTPROBLEM: WiFi-Verbindung schlägt fehl")
            print("   → SSID 'IBIMSNOCH1MAL' korrekt?")
            print("   → Passwort 'G8pY4B8K56vF' korrekt?") 
            print("   → Signalstärke ausreichend?")
            print("   → 2.4GHz WiFi verfügbar?")
            
        elif self.analysis['wifi_connected'] and not self.analysis['ap_mode_started']:
            print("✅ WiFi OK, aber kein AP-Modus")
            print("   → ESP8266 sollte im Heimnetz erreichbar sein")
            print(f"   → Teste IPs: {self.analysis['ip_addresses']}")
            
        elif not self.analysis['wifi_connected'] and not self.analysis['ap_mode_started']:
            print("❌ HAUPTPROBLEM: Weder WiFi noch AP-Modus")
            print("   → Fallback-Logik fehlt")
            print("   → Timeout-Problem?")
            print("   → Code-Logik prüfen")
        
        # Fehlerliste
        if self.analysis['errors']:
            print(f"\n🚨 GEFUNDENE FEHLER ({len(self.analysis['errors'])}):")
            for i, error in enumerate(self.analysis['errors'][-10:], 1):  # Nur letzte 10
                print(f"   {i}. {error}")
        
        # Warnungen
        if self.analysis['warnings']:
            print(f"\n⚠️ WARNUNGEN ({len(self.analysis['warnings'])}):")
            for i, warn in enumerate(self.analysis['warnings'][-5:], 1):  # Nur letzte 5
                print(f"   {i}. {warn}")
        
        # Empfehlungen
        print(f"\n💡 NÄCHSTE SCHRITTE:")
        print("-" * 40)
        
        if not self.analysis['boot_successful']:
            print("1. Hardware-Reset: Reset-Button 10s drücken")
            print("2. Stromversorgung: Externes 1A+ Netzteil verwenden")
            print("3. Re-Flash: Code erneut auf ESP8266 flashen")
            
        elif not self.analysis['wifi_connected']:
            print("1. WiFi-Credentials prüfen:")
            print("   SSID: 'IBIMSNOCH1MAL'")  
            print("   Pass: 'G8pY4B8K56vF'")
            print("2. Router-Einstellungen: 2.4GHz aktiviert?")
            print("3. Signalstärke: ESP8266 näher zum Router")
            
        else:
            print("1. IP-Scan: Netzwerk nach ESP8266 durchsuchen")
            print("2. Port-Test: HTTP Port 81 testen")
            print("3. Firewall: Router-Firewall prüfen")
        
        # Log-Datei speichern
        self.save_log_file()
    
    def save_log_file(self):
        """Diagnose-Log in Datei speichern"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"esp8266_diagnose_{timestamp}.log"
        report_filename = f"esp8266_report_{timestamp}.json"
        
        # Raw Log speichern
        with open(log_filename, 'w') as f:
            f.write(f"ESP8266 Diagnose Log - {datetime.now()}\n")
            f.write("="*60 + "\n\n")
            for entry in self.log_data:
                f.write(entry + "\n")
        
        # Analyse-Report speichern
        with open(report_filename, 'w') as f:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'analysis': self.analysis,
                'total_log_lines': len(self.log_data),
                'duration_seconds': 60
            }
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Logs gespeichert:")
        print(f"   📋 Raw Log: {log_filename}")
        print(f"   📊 Report: {report_filename}")
    
    def disconnect(self):
        """Serial-Verbindung schließen"""
        if self.serial_conn:
            self.serial_conn.close()
            print("🔌 Serial-Verbindung geschlossen")

def main():
    print("🔧 ESP8266 WiFi-Diagnose Tool")
    print("="*40)
    
    # Serial Port automatisch finden
    ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']
    
    diagnose = None
    for port in ports:
        try:
            diagnose = ESP8266Diagnose(port=port)
            if diagnose.connect_serial():
                break
        except Exception as e:
            print(f"Port {port} nicht verfügbar: {e}")
            continue
    
    if not diagnose or not diagnose.serial_conn:
        print("❌ Kein ESP8266 gefunden!")
        print("💡 Prüfen Sie:")
        print("   • ESP8266 per USB verbunden?")
        print("   • USB-Treiber installiert?")
        print("   • Anderes Programm (Arduino IDE) geschlossen?")
        return
    
    try:
        # ESP8266 Reset auslösen für sauberen Start
        print("\n🔄 ESP8266 Reset für saubere Diagnose...")
        diagnose.serial_conn.setDTR(False)
        time.sleep(0.1)
        diagnose.serial_conn.setDTR(True)
        time.sleep(1)
        
        # Diagnose starten
        diagnose.read_and_analyze(duration_seconds=60)
        
    except KeyboardInterrupt:
        print("\n⏹️ Diagnose abgebrochen")
    finally:
        diagnose.disconnect()

if __name__ == "__main__":
    main()