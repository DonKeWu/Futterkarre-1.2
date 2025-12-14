#!/usr/bin/env python3
"""
Pi5 System Test - Futterkarre Komponenten Tester
Testet alle wichtigen Hardware- und Software-Komponenten
"""

import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Logging Setup
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Pi5SystemTest:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'hostname': self.get_hostname(),
            'tests': {}
        }
        
    def get_hostname(self):
        try:
            return subprocess.check_output(['hostname']).decode().strip()
        except:
            return 'unknown'

    def test_python_environment(self):
        """Test Python und wichtige Module"""
        print("\n🐍 PYTHON ENVIRONMENT TEST")
        print("=" * 50)
        
        try:
            # Python Version
            python_version = sys.version
            print(f"✅ Python Version: {python_version}")
            
            # Wichtige Module testen
            modules = ['PyQt5', 'serial', 'json', 'datetime', 'pathlib']
            missing_modules = []
            
            for module in modules:
                try:
                    __import__(module)
                    print(f"✅ Modul {module}: OK")
                except ImportError:
                    print(f"❌ Modul {module}: FEHLT")
                    missing_modules.append(module)
            
            self.results['tests']['python_env'] = {
                'status': 'PASS' if not missing_modules else 'FAIL',
                'python_version': python_version,
                'missing_modules': missing_modules
            }
            
        except Exception as e:
            print(f"❌ Python Environment Test fehlgeschlagen: {e}")
            self.results['tests']['python_env'] = {'status': 'ERROR', 'error': str(e)}

    def test_file_structure(self):
        """Test Datei-Struktur der Futterkarre"""
        print("\n📁 FILE STRUCTURE TEST")
        print("=" * 50)
        
        required_files = [
            'main.py',
            'config/app_config.py',
            'config/settings.json',
            'hardware/sensor_manager.py',
            'views/main_window.py',
            'data/pferde.csv'
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in required_files:
            if Path(file_path).exists():
                print(f"✅ {file_path}: OK")
                existing_files.append(file_path)
            else:
                print(f"❌ {file_path}: FEHLT")
                missing_files.append(file_path)
        
        self.results['tests']['file_structure'] = {
            'status': 'PASS' if not missing_files else 'FAIL',
            'existing_files': existing_files,
            'missing_files': missing_files
        }

    def test_hardware_detection(self):
        """Test Hardware-Erkennung"""
        print("\n⚙️ HARDWARE DETECTION TEST")
        print("=" * 50)
        
        try:
            # GPIO Test (falls verfügbar)
            try:
                import RPi.GPIO as GPIO
                print("✅ RPi.GPIO: Verfügbar")
                gpio_available = True
            except ImportError:
                print("❌ RPi.GPIO: Nicht verfügbar")
                gpio_available = False
            
            # USB/Serial Ports
            try:
                result = subprocess.run(['ls', '/dev/ttyUSB*'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    usb_ports = result.stdout.strip().split('\n')
                    print(f"✅ USB Ports gefunden: {usb_ports}")
                else:
                    usb_ports = []
                    print("⚠️ Keine USB Ports gefunden")
            except:
                usb_ports = []
                print("❌ USB Port Erkennung fehlgeschlagen")
            
            # I2C Test
            try:
                result = subprocess.run(['ls', '/dev/i2c*'], 
                                      capture_output=True, text=True)
                i2c_available = result.returncode == 0
                print(f"{'✅' if i2c_available else '❌'} I2C: {'Verfügbar' if i2c_available else 'Nicht verfügbar'}")
            except:
                i2c_available = False
                print("❌ I2C Test fehlgeschlagen")
            
            self.results['tests']['hardware'] = {
                'status': 'PASS',
                'gpio_available': gpio_available,
                'usb_ports': usb_ports,
                'i2c_available': i2c_available
            }
            
        except Exception as e:
            print(f"❌ Hardware Detection fehlgeschlagen: {e}")
            self.results['tests']['hardware'] = {'status': 'ERROR', 'error': str(e)}

    def test_network_connectivity(self):
        """Test Netzwerk-Verbindung"""
        print("\n🌐 NETWORK CONNECTIVITY TEST")
        print("=" * 50)
        
        try:
            # Ping Test
            result = subprocess.run(['ping', '-c', '3', '8.8.8.8'], 
                                  capture_output=True, text=True, timeout=10)
            internet_ok = result.returncode == 0
            print(f"{'✅' if internet_ok else '❌'} Internet Ping: {'OK' if internet_ok else 'FEHLER'}")
            
            # WiFi Status
            try:
                result = subprocess.run(['iwconfig'], capture_output=True, text=True)
                wifi_info = result.stdout if result.returncode == 0 else "WiFi Info nicht verfügbar"
                print(f"📡 WiFi Status: {wifi_info[:100]}...")
            except:
                wifi_info = "WiFi Test fehlgeschlagen"
                print("❌ WiFi Status nicht abrufbar")
            
            # IP Adresse
            try:
                result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
                ip_address = result.stdout.strip() if result.returncode == 0 else "Keine IP"
                print(f"🏠 IP Adresse: {ip_address}")
            except:
                ip_address = "IP nicht ermittelbar"
                print("❌ IP Adresse nicht ermittelbar")
            
            self.results['tests']['network'] = {
                'status': 'PASS' if internet_ok else 'PARTIAL',
                'internet_ping': internet_ok,
                'wifi_info': wifi_info[:200],
                'ip_address': ip_address
            }
            
        except Exception as e:
            print(f"❌ Network Test fehlgeschlagen: {e}")
            self.results['tests']['network'] = {'status': 'ERROR', 'error': str(e)}

    def test_display_system(self):
        """Test Display System"""
        print("\n📺 DISPLAY SYSTEM TEST")
        print("=" * 50)
        
        try:
            # Display Environment
            display = os.environ.get('DISPLAY', 'Nicht gesetzt')
            print(f"🖥️ DISPLAY Variable: {display}")
            
            # X11 Test
            try:
                result = subprocess.run(['xrandr'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("✅ X11/Display System: OK")
                    display_info = result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout
                    display_ok = True
                else:
                    print("❌ X11/Display System: FEHLER")
                    display_info = "Display nicht verfügbar"
                    display_ok = False
            except:
                print("⚠️ X11 Test übersprungen (möglicherweise SSH)")
                display_info = "X11 Test nicht möglich"
                display_ok = None
            
            self.results['tests']['display'] = {
                'status': 'PASS' if display_ok else 'PARTIAL',
                'display_env': display,
                'x11_available': display_ok,
                'display_info': display_info
            }
            
        except Exception as e:
            print(f"❌ Display Test fehlgeschlagen: {e}")
            self.results['tests']['display'] = {'status': 'ERROR', 'error': str(e)}

    def test_futterkarre_import(self):
        """Test Futterkarre Module Import"""
        print("\n🎯 FUTTERKARRE MODULE TEST")
        print("=" * 50)
        
        try:
            # Config Import Test
            try:
                from config.app_config import AppConfig
                print("✅ Config Module: OK")
                config_ok = True
            except Exception as e:
                print(f"❌ Config Module: {e}")
                config_ok = False
            
            # Hardware Import Test  
            try:
                from hardware.sensor_manager import SmartSensorManager
                print("✅ Hardware Module: OK")
                hardware_ok = True
            except Exception as e:
                print(f"❌ Hardware Module: {e}")
                hardware_ok = False
            
            # Views Import Test
            try:
                from views.main_window import MainWindow
                print("✅ Views Module: OK")
                views_ok = True
            except Exception as e:
                print(f"❌ Views Module: {e}")
                views_ok = False
            
            all_ok = config_ok and hardware_ok and views_ok
            
            self.results['tests']['futterkarre_modules'] = {
                'status': 'PASS' if all_ok else 'FAIL',
                'config_import': config_ok,
                'hardware_import': hardware_ok,
                'views_import': views_ok
            }
            
        except Exception as e:
            print(f"❌ Futterkarre Module Test fehlgeschlagen: {e}")
            self.results['tests']['futterkarre_modules'] = {'status': 'ERROR', 'error': str(e)}

    def test_system_resources(self):
        """Test System-Ressourcen"""
        print("\n💾 SYSTEM RESOURCES TEST")
        print("=" * 50)
        
        try:
            # Memory Test
            try:
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                    total_mem = int([line for line in meminfo.split('\n') if 'MemTotal' in line][0].split()[1]) // 1024
                    free_mem = int([line for line in meminfo.split('\n') if 'MemAvailable' in line][0].split()[1]) // 1024
                    print(f"💾 RAM: {total_mem}MB total, {free_mem}MB verfügbar")
                    memory_ok = free_mem > 500  # Mindestens 500MB frei
                    print(f"{'✅' if memory_ok else '⚠️'} Memory Status: {'OK' if memory_ok else 'NIEDRIG'}")
            except:
                total_mem = free_mem = 0
                memory_ok = False
                print("❌ Memory Info nicht verfügbar")
            
            # Disk Space Test
            try:
                result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
                if result.returncode == 0:
                    disk_info = result.stdout.split('\n')[1].split()
                    disk_used_percent = int(disk_info[4].rstrip('%'))
                    print(f"💿 Disk Space: {disk_info[3]} frei, {disk_info[4]} belegt")
                    disk_ok = disk_used_percent < 90
                    print(f"{'✅' if disk_ok else '⚠️'} Disk Status: {'OK' if disk_ok else 'VOLL'}")
                else:
                    disk_ok = False
                    disk_used_percent = 100
            except:
                disk_ok = False
                disk_used_percent = 100
                print("❌ Disk Info nicht verfügbar")
            
            # CPU Info
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    cpu_info = f.read()
                    cpu_model = [line for line in cpu_info.split('\n') if 'model name' in line][0].split(':')[1].strip()
                    print(f"🔧 CPU: {cpu_model}")
            except:
                cpu_model = "CPU Info nicht verfügbar"
                print("❌ CPU Info nicht verfügbar")
            
            self.results['tests']['system_resources'] = {
                'status': 'PASS' if memory_ok and disk_ok else 'WARNING',
                'total_memory_mb': total_mem,
                'free_memory_mb': free_mem,
                'memory_ok': memory_ok,
                'disk_usage_percent': disk_used_percent,
                'disk_ok': disk_ok,
                'cpu_model': cpu_model
            }
            
        except Exception as e:
            print(f"❌ System Resources Test fehlgeschlagen: {e}")
            self.results['tests']['system_resources'] = {'status': 'ERROR', 'error': str(e)}

    def run_all_tests(self):
        """Führe alle Tests aus"""
        print("🚀 PI5 FUTTERKARRE SYSTEM TEST")
        print("=" * 60)
        print(f"Hostname: {self.results['hostname']}")
        print(f"Zeit: {self.results['timestamp']}")
        print("=" * 60)
        
        # Alle Tests ausführen
        self.test_python_environment()
        self.test_file_structure()
        self.test_hardware_detection()
        self.test_network_connectivity()
        self.test_display_system()
        self.test_futterkarre_import()
        self.test_system_resources()
        
        # Ergebnis-Zusammenfassung
        self.print_summary()
        
        # JSON Report speichern
        report_file = f"pi5_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detaillierter Report gespeichert: {report_file}")

    def print_summary(self):
        """Drucke Test-Zusammenfassung"""
        print("\n📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.results['tests'])
        passed = sum(1 for test in self.results['tests'].values() if test.get('status') == 'PASS')
        failed = sum(1 for test in self.results['tests'].values() if test.get('status') == 'FAIL')
        warnings = sum(1 for test in self.results['tests'].values() if test.get('status') in ['PARTIAL', 'WARNING'])
        errors = sum(1 for test in self.results['tests'].values() if test.get('status') == 'ERROR')
        
        print(f"🎯 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"⚠️ Warnings: {warnings}")
        print(f"❌ Failed: {failed}")
        print(f"💥 Errors: {errors}")
        
        if failed == 0 and errors == 0:
            print("\n🎉 ALLE KRITISCHEN TESTS BESTANDEN!")
            print("Das System ist bereit für die Futterkarre.")
        else:
            print(f"\n⚠️ {failed + errors} TESTS FEHLGESCHLAGEN!")
            print("Bitte prüfe die Fehler oben.")

# Hauptprogramm
if __name__ == "__main__":
    import os
    
    print("Pi5 Futterkarre System Test wird gestartet...")
    time.sleep(1)
    
    tester = Pi5SystemTest()
    tester.run_all_tests()
    
    print("\nTest abgeschlossen! 🏁")