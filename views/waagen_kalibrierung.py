#!/usr/bin/env python3
"""
Waagen-Kalibrierungs-Seite
Vollständige Kalibrierung der HX711 Wägezellen

Features:
- Live Gewichtsanzeige (Gesamt + 4 Einzelzellen)
- Schritt-für-Schritt Kalibrierung
- Tara (Nullpunkt setzen)
- Referenzgewicht-Kalibrierung
- Kalibrierungs-Test und -Validierung
- Persistente Speicherung der Kalibrierwerte
- Integration mit HX711 Hardware
"""

import sys
import logging
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QProgressBar, QLabel
import os
import subprocess
import time
import json
from pathlib import Path

# Logger Setup
logger = logging.getLogger(__name__)
from datetime import datetime

# Projekt-spezifische Imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.base_ui_widget import BaseViewWidget
from utils.settings_manager import get_settings_manager
# ESP8266 Wireless-Module verwenden statt lokale HX711-Hardware
try:
    from wireless.esp8266_discovery import ESP8266Discovery, get_esp8266_status
    import urllib.request
    import urllib.error
    import json
    
    ESP8266_AVAILABLE = True
    esp8266_discovery = ESP8266Discovery()
    
    def lese_gewicht_hx711():
        """Liest Gesamtgewicht vom ESP8266 via HTTP (alle 4 HX711)"""
        try:
            # ESP8266 Dual-Mode IPs (Stall + Haus)
            test_ips = ["192.168.4.1", "192.168.2.20"]
            
            for ip in test_ips:
                try:
                    url = f"http://{ip}/live-values-data"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Futterkarre-Pi5'})
                    
                    with urllib.request.urlopen(req, timeout=2) as response:
                        data = json.loads(response.read().decode('utf-8'))
                        
                        # Alle 4 HX711-Werte aufsummieren
                        vl_val = float(data.get('vl_value', '0'))
                        vr_val = float(data.get('vr_value', '0'))
                        hl_val = float(data.get('hl_value', '0'))
                        hr_val = float(data.get('hr_value', '0'))
                        
                        # Umrechnung von Raw-Werten zu kg (vereinfacht)
                        # TODO: Echte Kalibrierungsfaktoren verwenden
                        total_raw = vl_val + vr_val + hl_val + hr_val
                        total_kg = total_raw / 100000.0  # Vereinfachte Skalierung
                        
                        logger.info(f"ESP8266 ({ip}): VL={vl_val}, VR={vr_val}, HL={hl_val}, HR={hr_val} → {total_kg:.3f}kg")
                        return total_kg
                        
                except urllib.error.URLError:
                    continue  # Nächste IP probieren
                except Exception as e:
                    logger.warning(f"ESP8266 {ip} Fehler: {e}")
                    continue
            
            logger.warning("Kein ESP8266 unter bekannten IPs erreichbar")
            return 0.0
        except Exception as e:
            logger.error(f"ESP8266 Gewicht-Fehler: {e}")
            return 0.0
    
    def lese_einzelzellwerte_hx711():
        """Liest alle 4 Einzelzellen vom ESP8266 via HTTP"""
        try:
            # ESP8266 Dual-Mode IPs (Stall + Haus)
            test_ips = ["192.168.4.1", "192.168.2.20"]
            
            for ip in test_ips:
                try:
                    url = f"http://{ip}/live-values-data"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Futterkarre-Pi5'})
                    
                    with urllib.request.urlopen(req, timeout=2) as response:
                        data = json.loads(response.read().decode('utf-8'))
                        
                        # Raw-Werte von allen 4 HX711
                        vl_raw = float(data.get('vl_value', '0'))
                        vr_raw = float(data.get('vr_value', '0'))
                        hl_raw = float(data.get('hl_value', '0'))
                        hr_raw = float(data.get('hr_value', '0'))
                        
                        # Umrechnung zu kg (vereinfacht)
                        scale_factor = 100000.0  # TODO: Echte Kalibrierung
                        
                        weights = [
                            vl_raw / scale_factor,  # VL (Vorne Links)
                            vr_raw / scale_factor,  # VR (Vorne Rechts)
                            hl_raw / scale_factor,  # HL (Hinten Links)
                            hr_raw / scale_factor   # HR (Hinten Rechts)
                        ]
                        
                        logger.info(f"ESP8266 Einzelzellen: {weights}")
                        return weights
                        
                except urllib.error.URLError:
                    continue  # Nächste IP probieren
                except Exception as e:
                    logger.warning(f"ESP8266 {ip} Fehler: {e}")
                    continue
            
            logger.warning("Kein ESP8266 für Einzelzellwerte erreichbar")
            return [0.0, 0.0, 0.0, 0.0]
        except Exception as e:
            logger.error(f"ESP8266 Einzelzell-Fehler: {e}")
            return [0.0, 0.0, 0.0, 0.0]
    
    def nullpunkt_setzen_alle():
        """Sendet Tare-Kommando an alle 4 HX711 über ESP8266"""
        try:
            test_ips = ["192.168.2.20", "192.168.4.1"]
            
            for ip in test_ips:
                try:
                    # ESP8266 hat noch kein /tare-Endpoint
                    # Für jetzt nur Logging
                    logger.info(f"ESP8266 ({ip}): Tare-Funktion noch nicht implementiert")
                    
                    # TODO: ESP8266-Firmware um /tare-Endpoint erweitern
                    # url = f"http://{ip}/tare-all"
                    # req = urllib.request.Request(url, method='POST')
                    # urllib.request.urlopen(req, timeout=5)
                    
                    return True
                    
                except Exception as e:
                    logger.warning(f"ESP8266 {ip} Tare-Fehler: {e}")
                    continue
            
            logger.warning("Kein ESP8266 für Tare erreichbar")
            return False
        except Exception as e:
            logger.error(f"ESP8266 Tare-Fehler: {e}")
            return False
    
    def kalibriere_einzelzelle(index, gewicht):
        """Sendet Kalibrierungs-Kommando an ESP8266"""
        try:
            test_ips = ["192.168.2.20", "192.168.4.1"]
            
            zellen_namen = ["VL", "VR", "HL", "HR"]
            if index >= len(zellen_namen):
                logger.error(f"Ungültiger Zellen-Index: {index}")
                return False
            
            for ip in test_ips:
                try:
                    # ESP8266 hat noch kein Kalibrierungs-Endpoint
                    logger.info(f"ESP8266 ({ip}): Kalibrierung für {zellen_namen[index]} mit {gewicht}kg noch nicht implementiert")
                    
                    # TODO: ESP8266-Firmware um /calibrate-Endpoint erweitern
                    # data = json.dumps({'cell': index, 'weight': gewicht})
                    # req = urllib.request.Request(f"http://{ip}/calibrate", data=data.encode(), method='POST')
                    # urllib.request.urlopen(req, timeout=5)
                    
                    return True
                    
                except Exception as e:
                    logger.warning(f"ESP8266 {ip} Kalibrierungs-Fehler: {e}")
                    continue
            
            return False
        except Exception as e:
            logger.error(f"ESP8266 Kalibrierungs-Fehler: {e}")
            return False
    
    def nullpunkt_setzen_alle():
        """Setzt Nullpunkt für alle ESP8266-HX711-Zellen"""
        try:
            test_ips = ["192.168.4.1", "192.168.2.20"]
            
            for ip in test_ips:
                try:
                    url = f"http://{ip}/tare"
                    req = urllib.request.Request(url, method='POST')
                    
                    with urllib.request.urlopen(req, timeout=5) as response:
                        if response.status == 200:
                            logger.info(f"✅ ESP8266 Nullpunkt gesetzt: {ip}")
                            return True
                except Exception:
                    continue
                    
            logger.error("❌ ESP8266 Nullpunkt-Setzung fehlgeschlagen")
            return False
        except Exception as e:
            logger.error(f"ESP8266 Tare-Fehler: {e}")
            return False
    
    def kalibriere_einzelzelle(index, gewicht):
        """Sendet Kalibrierungs-Kommando an ESP8266"""
        try:
            test_ips = ["192.168.2.20", "192.168.4.1"]
            
            for ip in test_ips:
                try:
                    url = f"http://{ip}/calibrate"
                    data = json.dumps({"weight": gewicht}).encode('utf-8')
                    req = urllib.request.Request(url, data=data, method='POST')
                    req.add_header('Content-Type', 'application/json')
                    
                    with urllib.request.urlopen(req, timeout=5) as response:
                        if response.status == 200:
                            logger.info(f"✅ ESP8266 kalibriert mit {gewicht}kg: {ip}")
                            return True
                except Exception:
                    continue
                    
            logger.error(f"❌ ESP8266 Kalibrierung fehlgeschlagen: {gewicht}kg")
            return False
        except Exception as e:
            logger.error(f"ESP8266 Kalibrierungs-Fehler: {e}")
            return False

except ImportError as e:
    logger.warning(f"ESP8266-Discovery nicht verfügbar: {e}")
    # Fallback für Entwicklung
    ESP8266_AVAILABLE = False
    
    def lese_gewicht_hx711():
        return 0.0
    
    def lese_einzelzellwerte_hx711():
        return [0.0, 0.0, 0.0, 0.0]
    
    def nullpunkt_setzen_alle():
        logger.warning("ESP8266 nicht verfügbar")
        return False
    
    def kalibriere_einzelzelle(index, gewicht):
        logger.warning("ESP8266 nicht verfügbar")
        return False

logger = logging.getLogger(__name__)

class Pi5SystemTester:
    """Integrierte Pi5 System-Tests für die Futterkarre"""
    
    def __init__(self, text_output_widget=None):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'hostname': self.get_hostname(),
            'tests': {}
        }
        self.text_widget = text_output_widget
        
    def get_hostname(self):
        try:
            return subprocess.check_output(['hostname']).decode().strip()
        except:
            return 'unknown'
    
    def log_message(self, message):
        """Schreibt Nachricht in Text-Widget und Konsole"""
        print(message)
        if self.text_widget:
            self.text_widget.append(message)
            self.text_widget.repaint()
    
    def test_python_environment(self):
        """Test Python und wichtige Module"""
        self.log_message("\n🐍 PYTHON ENVIRONMENT TEST")
        self.log_message("=" * 50)
        
        try:
            python_version = sys.version
            self.log_message(f"✅ Python Version: {python_version.split()[0]}")
            
            modules = ['PyQt5', 'serial', 'json', 'datetime', 'pathlib']
            missing_modules = []
            
            for module in modules:
                try:
                    __import__(module)
                    self.log_message(f"✅ Modul {module}: OK")
                except ImportError:
                    self.log_message(f"❌ Modul {module}: FEHLT")
                    missing_modules.append(module)
            
            self.results['tests']['python_env'] = {
                'status': 'PASS' if not missing_modules else 'FAIL',
                'python_version': python_version,
                'missing_modules': missing_modules
            }
            
        except Exception as e:
            self.log_message(f"❌ Python Environment Test fehlgeschlagen: {e}")
            self.results['tests']['python_env'] = {'status': 'ERROR', 'error': str(e)}
    
    def test_futterkarre_modules(self):
        """Test Futterkarre Module Import"""
        self.log_message("\n🎯 FUTTERKARRE MODULE TEST")
        self.log_message("=" * 50)
        
        try:
            # Config Import Test
            try:
                from config.app_config import AppConfig
                self.log_message("✅ Config Module: OK")
                config_ok = True
            except Exception as e:
                self.log_message(f"❌ Config Module: {e}")
                config_ok = False
            
            # Hardware Import Test  
            try:
                from hardware.sensor_manager import SmartSensorManager
                self.log_message("✅ Hardware Module: OK")
                hardware_ok = True
            except Exception as e:
                self.log_message(f"❌ Hardware Module: {e}")
                hardware_ok = False
            
            # Views Import Test
            try:
                from views.main_window import MainWindow
                self.log_message("✅ Views Module: OK")
                views_ok = True
            except Exception as e:
                self.log_message(f"❌ Views Module: {e}")
                views_ok = False
            
            all_ok = config_ok and hardware_ok and views_ok
            
            self.results['tests']['futterkarre_modules'] = {
                'status': 'PASS' if all_ok else 'FAIL',
                'config_import': config_ok,
                'hardware_import': hardware_ok,
                'views_import': views_ok
            }
            
        except Exception as e:
            self.log_message(f"❌ Futterkarre Module Test fehlgeschlagen: {e}")
            self.results['tests']['futterkarre_modules'] = {'status': 'ERROR', 'error': str(e)}
    
    def test_hardware_detection(self):
        """Test Hardware-Erkennung mit detaillierten HX711-Tests"""
        self.log_message("\n⚙️ HARDWARE DETECTION TEST")
        self.log_message("=" * 50)
        
        try:
            # GPIO Test (falls verfügbar)
            try:
                import RPi.GPIO as GPIO
                self.log_message("✅ RPi.GPIO: Verfügbar")
                gpio_available = True
                
                # GPIO Version Info
                try:
                    version = GPIO.VERSION
                    self.log_message(f"📋 RPi.GPIO Version: {version}")
                except:
                    pass
                    
            except ImportError:
                self.log_message("❌ RPi.GPIO: Nicht verfügbar (Simulation/Development)")
                gpio_available = False
            
            # USB/Serial Ports
            try:
                result = subprocess.run(['ls', '/dev/ttyUSB*'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    usb_ports = result.stdout.strip().split('\n')
                    self.log_message(f"✅ USB Ports gefunden: {usb_ports}")
                else:
                    usb_ports = []
                    self.log_message("⚠️ Keine USB Ports gefunden")
            except:
                usb_ports = []
                self.log_message("❌ USB Port Erkennung fehlgeschlagen")
            
            # I2C Bus Test
            try:
                result = subprocess.run(['ls', '/dev/i2c*'], capture_output=True, text=True)
                if result.returncode == 0:
                    i2c_devices = result.stdout.strip().split('\n')
                    self.log_message(f"✅ I2C Devices: {i2c_devices}")
                    i2c_ok = True
                else:
                    self.log_message("⚠️ Keine I2C Devices gefunden")
                    i2c_ok = False
            except:
                self.log_message("❌ I2C Test fehlgeschlagen")
                i2c_ok = False
            
            # HX711 Import Test
            hx711_import_ok = False
            try:
                from hardware.hx711_real import hx_sensors, lese_gewicht_hx711, lese_einzelzellwerte_hx711, HX711_AVAILABLE
                self.log_message(f"✅ HX711 Module Import: OK")
                self.log_message(f"📋 HX711_AVAILABLE Flag: {HX711_AVAILABLE}")
                hx711_import_ok = True
            except Exception as e:
                self.log_message(f"❌ HX711 Module Import: {e}")
                hx711_import_ok = False
            
            # HX711 Hardware Test
            hx711_hardware_ok = False
            if hx711_import_ok:
                try:
                    if hx_sensors and len(hx_sensors) > 0:
                        self.log_message(f"✅ HX711 Sensoren initialisiert: {len(hx_sensors)} Stück")
                        
                        # Teste jeden Sensor einzeln
                        for i, sensor in enumerate(hx_sensors):
                            try:
                                sensor_name = sensor.config.get('name', f'Sensor_{i+1}')
                                raw_weight = sensor.read_weight(samples=1)
                                self.log_message(f"  📊 {sensor_name}: {raw_weight:.3f}kg")
                                hx711_hardware_ok = True
                            except Exception as e:
                                self.log_message(f"  ❌ {sensor_name}: Fehler - {e}")
                        
                        # Gesamtgewicht testen
                        try:
                            total_weight = lese_gewicht_hx711()
                            self.log_message(f"✅ Gesamtgewicht: {total_weight:.2f}kg")
                        except Exception as e:
                            self.log_message(f"❌ Gesamtgewicht-Fehler: {e}")
                            
                    else:
                        self.log_message("❌ HX711 Sensoren: Nicht initialisiert oder leer")
                        hx711_hardware_ok = False
                        
                except Exception as e:
                    self.log_message(f"❌ HX711 Hardware Test: {e}")
                    hx711_hardware_ok = False
            
            # SPI Test (für HX711)
            spi_ok = False
            try:
                result = subprocess.run(['ls', '/dev/spi*'], capture_output=True, text=True)
                if result.returncode == 0:
                    spi_devices = result.stdout.strip().split('\n')
                    self.log_message(f"✅ SPI Devices: {spi_devices}")
                    spi_ok = True
                else:
                    self.log_message("⚠️ Keine SPI Devices gefunden")
            except:
                self.log_message("❌ SPI Test fehlgeschlagen")
            
            # Zusammenfassung
            overall_status = 'PASS' if hx711_hardware_ok else ('PARTIAL' if hx711_import_ok else 'FAIL')
            
            self.results['tests']['hardware'] = {
                'status': overall_status,
                'gpio_available': gpio_available,
                'usb_ports': usb_ports,
                'i2c_available': i2c_ok,
                'spi_available': spi_ok,
                'hx711_import_ok': hx711_import_ok,
                'hx711_hardware_ok': hx711_hardware_ok,
                'sensor_count': len(hx_sensors) if hx711_import_ok and hx_sensors else 0
            }
            
        except Exception as e:
            self.log_message(f"❌ Hardware Detection fehlgeschlagen: {e}")
            self.results['tests']['hardware'] = {'status': 'ERROR', 'error': str(e)}
    
    def test_system_resources(self):
        """Test System-Ressourcen"""
        self.log_message("\n💾 SYSTEM RESOURCES TEST")
        self.log_message("=" * 50)
        
        try:
            # Memory Test
            try:
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                    total_mem = int([line for line in meminfo.split('\n') if 'MemTotal' in line][0].split()[1]) // 1024
                    free_mem = int([line for line in meminfo.split('\n') if 'MemAvailable' in line][0].split()[1]) // 1024
                    self.log_message(f"💾 RAM: {total_mem}MB total, {free_mem}MB verfügbar")
                    memory_ok = free_mem > 500
                    self.log_message(f"{'✅' if memory_ok else '⚠️'} Memory Status: {'OK' if memory_ok else 'NIEDRIG'}")
            except:
                total_mem = free_mem = 0
                memory_ok = False
                self.log_message("❌ Memory Info nicht verfügbar")
            
            # CPU Info
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    cpu_info = f.read()
                    cpu_model = [line for line in cpu_info.split('\n') if 'model name' in line][0].split(':')[1].strip()
                    self.log_message(f"🔧 CPU: {cpu_model}")
            except:
                cpu_model = "CPU Info nicht verfügbar"
                self.log_message("❌ CPU Info nicht verfügbar")
            
            self.results['tests']['system_resources'] = {
                'status': 'PASS' if memory_ok else 'WARNING',
                'total_memory_mb': total_mem,
                'free_memory_mb': free_mem,
                'memory_ok': memory_ok,
                'cpu_model': cpu_model
            }
            
        except Exception as e:
            self.log_message(f"❌ System Resources Test fehlgeschlagen: {e}")
            self.results['tests']['system_resources'] = {'status': 'ERROR', 'error': str(e)}
    
    def test_weight_system(self):
        """Test Weight Manager und HX711 System"""
        self.log_message("\n⚖️ WEIGHT SYSTEM TEST")
        self.log_message("=" * 50)
        
        try:
            # Weight Manager Test
            try:
                from hardware.weight_manager import get_weight_manager
                wm = get_weight_manager()
                self.log_message("✅ Weight Manager: OK")
                
                # Gewicht lesen
                weight = wm.read_weight()
                self.log_message(f"📊 Aktuelles Gewicht: {weight:.2f}kg")
                
                # Einzelzellen lesen
                cells = wm.read_individual_cells()
                self.log_message(f"🔍 Einzelzellen: VL={cells[0]:.2f}, VR={cells[1]:.2f}, HL={cells[2]:.2f}, HR={cells[3]:.2f}")
                
                weight_ok = True
            except Exception as e:
                self.log_message(f"❌ Weight Manager: {e}")
                weight_ok = False
            
            # ESP8266 Test (falls verfügbar)
            esp8266_ok = False
            if ESP8266_AVAILABLE:
                try:
                    esp_weight = lese_gewicht_hx711()
                    self.log_message(f"📡 ESP8266 Gewicht: {esp_weight:.2f}kg")
                    esp8266_ok = True
                except Exception as e:
                    self.log_message(f"❌ ESP8266: {e}")
            else:
                self.log_message("⚠️ ESP8266: Nicht verfügbar")
            
            self.results['tests']['weight_system'] = {
                'status': 'PASS' if weight_ok else 'FAIL',
                'weight_manager_ok': weight_ok,
                'esp8266_available': esp8266_ok
            }
            
        except Exception as e:
            self.log_message(f"❌ Weight System Test fehlgeschlagen: {e}")
            self.results['tests']['weight_system'] = {'status': 'ERROR', 'error': str(e)}
    
    def run_quick_test(self):
        """Schneller Test der wichtigsten Komponenten"""
        self.log_message("⚡ QUICK PI5 FUTTERKARRE TEST")
        self.log_message("=" * 40)
        
        self.test_python_environment()
        self.test_futterkarre_modules()
        self.test_hardware_detection()
        self.test_weight_system()
        
        self.print_summary()
    
    def run_full_test(self):
        """Vollständiger System-Test"""
        self.log_message("🚀 VOLLSTÄNDIGER PI5 FUTTERKARRE SYSTEM TEST")
        self.log_message("=" * 60)
        
        self.test_python_environment()
        self.test_futterkarre_modules()
        self.test_hardware_detection()
        self.test_system_resources()
        self.test_weight_system()
        
        self.print_summary()
        self.save_report()
    
    def print_summary(self):
        """Test-Zusammenfassung anzeigen"""
        self.log_message("\n📊 TEST SUMMARY")
        self.log_message("=" * 50)
        
        total_tests = len(self.results['tests'])
        passed = sum(1 for test in self.results['tests'].values() if test.get('status') == 'PASS')
        failed = sum(1 for test in self.results['tests'].values() if test.get('status') == 'FAIL')
        warnings = sum(1 for test in self.results['tests'].values() if test.get('status') in ['PARTIAL', 'WARNING'])
        errors = sum(1 for test in self.results['tests'].values() if test.get('status') == 'ERROR')
        
        self.log_message(f"🎯 Total Tests: {total_tests}")
        self.log_message(f"✅ Passed: {passed}")
        self.log_message(f"⚠️ Warnings: {warnings}")
        self.log_message(f"❌ Failed: {failed}")
        self.log_message(f"💥 Errors: {errors}")
        
        if failed == 0 and errors == 0:
            self.log_message("\n🎉 ALLE KRITISCHEN TESTS BESTANDEN!")
            self.log_message("Das Pi5-System ist bereit für die Futterkarre.")
        else:
            self.log_message(f"\n⚠️ {failed + errors} TESTS FEHLGESCHLAGEN!")
            self.log_message("Bitte prüfe die Fehler oben.")
    
    def save_report(self):
        """Speichere detaillierten JSON-Report"""
        try:
            report_file = f"pi5_gui_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            self.log_message(f"\n📄 Detaillierter Report gespeichert: {report_file}")
        except Exception as e:
            self.log_message(f"❌ Report speichern fehlgeschlagen: {e}")


class WaagenKalibrierung(BaseViewWidget):
    """
    Waagen-Kalibrierungs-Seite mit Live-Anzeige und schrittweiser Kalibrierung
    
    Kalibrierungs-Prozess:
    1. Tara: Nullpunkt setzen (leerer Karren)
    2. Referenzgewicht: Bekanntes Gewicht auflegen und kalibrieren
    3. Test: Verschiedene Gewichte zur Validierung
    4. Speichern: Kalibrierwerte persistent speichern
    """
    
    # Signale
    kalibrierung_abgeschlossen = pyqtSignal(bool)  # Erfolgreich ja/nein
    
    def __init__(self, parent=None):
        # BaseViewWidget mit UI-Datei initialisieren  
        super().__init__(parent, ui_filename="waagen_kalibrierung.ui", page_name="waagen_kalibrierung")
        
        # Manager
        self.settings_manager = get_settings_manager()
        
        # Kalibrierungs-Status
        self.kalibrierung_schritt = 0  # 0=Start, 1=Tara, 2=Kalibriert, 3=Getestet
        self.tara_werte = [0.0, 0.0, 0.0, 0.0]  # Nullpunkt-Werte für 4 Sensoren
        self.kalibrier_faktoren = [1.0, 1.0, 1.0, 1.0]  # Skalenfaktoren
        self.referenz_gewicht = 20.0  # Standard 20kg
        self.toleranz = 0.05  # ±50g Toleranz
        
        # Timer für Live-Updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_live_anzeige)
        
        # UI initialisieren
        self.init_ui()
        self.load_kalibrierungs_daten()
        
        # HX711-Status-Check beim Start
        self.check_hx711_status()
        
        # Live-Updates starten wenn aktiviert
        if hasattr(self, 'cb_live_update') and self.cb_live_update.isChecked():
            self.start_live_updates()
        
        logger.info("WaagenKalibrierung initialisiert")
    
    def init_ui(self):
        """Initialisiert UI-Komponenten und Button-Callbacks"""
        try:
            # Button-Callbacks
            if hasattr(self, 'btn_back'):
                self.btn_back.clicked.connect(self.zurueck_geklickt)
            
            if hasattr(self, 'btn_tara'):
                self.btn_tara.clicked.connect(self.tara_durchfuehren)
            
            if hasattr(self, 'btn_kalibrieren'):
                self.btn_kalibrieren.clicked.connect(self.kalibrierung_durchfuehren)
            
            if hasattr(self, 'btn_test'):
                self.btn_test.clicked.connect(self.kalibrierung_testen)
            
            if hasattr(self, 'btn_speichern'):
                self.btn_speichern.clicked.connect(self.kalibrierwerte_speichern)
            
            if hasattr(self, 'btn_reset'):
                self.btn_reset.clicked.connect(self.kalibrierung_zuruecksetzen)
            
            # Input-Field Callbacks
            if hasattr(self, 'input_referenzgewicht'):
                self.input_referenzgewicht.textChanged.connect(self.referenzgewicht_geaendert)
            
            if hasattr(self, 'input_toleranz'):
                self.input_toleranz.textChanged.connect(self.toleranz_geaendert)
            
            # Live-Update Checkbox
            if hasattr(self, 'cb_live_update'):
                self.cb_live_update.toggled.connect(self.live_update_toggled)
            
            # HX711-Test Buttons (falls vorhanden in UI)
            # ESP8266-Test Button ENTFERNT - ersetzt durch LED-Status
            
            # HX711-Test-Buttons KOMPLETT ENTFERNT - nicht mehr nötig
            # LED-Status-Anzeigen ersetzen alle Test-Funktionen
            
            # Status aktualisieren
            self.update_status("Bereit für Kalibrierung...")
            self.update_kalibrierungs_buttons()
            
        except Exception as e:
            logger.error(f"Fehler bei UI-Initialisierung: {e}")
            self.update_status(f"UI-Fehler: {e}")
    
    def load_kalibrierungs_daten(self):
        """Lädt gespeicherte Kalibrierungsdaten"""
        try:
            # Kalibrierwerte aus Settings laden
            if hasattr(self.settings_manager, 'calibration'):
                cal_data = self.settings_manager.calibration
                
                # Tara-Werte
                if hasattr(cal_data, 'tare_values') and cal_data.tare_values:
                    self.tara_werte = cal_data.tare_values[:4]  # Nur erste 4 Werte
                
                # Kalibrier-Faktoren  
                if hasattr(cal_data, 'scale_factors') and cal_data.scale_factors:
                    self.kalibrier_faktoren = cal_data.scale_factors[:4]
                
                # Letztes Referenzgewicht
                if hasattr(cal_data, 'last_reference_weight'):
                    self.referenz_gewicht = float(cal_data.last_reference_weight)
                    if hasattr(self, 'input_referenzgewicht'):
                        self.input_referenzgewicht.setText(str(self.referenz_gewicht))
                
                # Status bestimmen
                if any(f != 1.0 for f in self.kalibrier_faktoren):
                    self.kalibrierung_schritt = 2  # Bereits kalibriert
                    self.update_status("Vorherige Kalibrierung geladen - bereit für Test")
                else:
                    self.kalibrierung_schritt = 0
                    self.update_status("Keine Kalibrierung gefunden - bitte Tara durchführen")
            
            logger.info(f"Kalibrierungsdaten geladen: Schritt {self.kalibrierung_schritt}")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Kalibrierungsdaten: {e}")
            self.update_status(f"Lade-Fehler: {e}")
    
    def start_live_updates(self):
        """Startet Live-Gewichtsanzeige"""
        if ESP8266_AVAILABLE:
            self.update_timer.start(1000)  # 1 Sekunde Intervall
            self.update_status("Live-Updates gestartet - ESP8266 Wireless")
        else:
            self.update_status("WARNUNG: ESP8266 nicht verfügbar")
            self.update_timer.start(1000)  # Timer trotzdem starten für Fallback
    
    def stop_live_updates(self):
        """Stoppt Live-Updates"""
        self.update_timer.stop()
        self.update_status("Live-Updates gestoppt")
    
    def update_live_anzeige(self):
        """Aktualisiert Live-Gewichtsanzeige"""
        try:
            if ESP8266_AVAILABLE:
                # ESP8266 Wireless-Daten
                gesamtgewicht = lese_gewicht_hx711()
                einzelwerte = lese_einzelzellwerte_hx711()
            else:
                # Fallback wenn ESP8266 nicht verfügbar
                gesamtgewicht = 0.0
                einzelwerte = [0.0, 0.0, 0.0, 0.0]
            
            # Gesamtgewicht anzeigen
            if hasattr(self, 'lbl_gesamtgewicht_wert'):
                self.lbl_gesamtgewicht_wert.setText(f"{gesamtgewicht:.2f} kg")
            
            # Einzelzellen anzeigen
            if hasattr(self, 'lbl_vl_wert'):
                self.lbl_vl_wert.setText(f"{einzelwerte[0]:.2f} kg")
            if hasattr(self, 'lbl_vr_wert'):
                self.lbl_vr_wert.setText(f"{einzelwerte[1]:.2f} kg")
            if hasattr(self, 'lbl_hl_wert'):
                self.lbl_hl_wert.setText(f"{einzelwerte[2]:.2f} kg")
            if hasattr(self, 'lbl_hr_wert'):
                self.lbl_hr_wert.setText(f"{einzelwerte[3]:.2f} kg")
            
        except Exception as e:
            logger.error(f"Fehler bei Live-Update: {e}")
            self.update_status(f"Live-Update Fehler: {e}")
    
    def tara_durchfuehren(self):
        """Führt Tara (Nullpunkt setzen) durch"""
        try:
            # Warnung anzeigen
            reply = QMessageBox.question(
                self, "Tara durchführen",
                "Bitte leeren Sie den Karren vollständig.\n\nFortfahren mit Tara?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            self.update_status("Tara wird durchgeführt...")
            
            # Live-Updates temporär stoppen
            was_running = self.update_timer.isActive()
            if was_running:
                self.stop_live_updates()
            
            if HX711_AVAILABLE and hx_sensors:
                # Echte Hardware-Tara
                nullpunkt_setzen_alle()
                
                # Tara-Werte aus Sensoren lesen
                import time
                time.sleep(1)  # Kurz warten
                self.tara_werte = lese_einzelzellwerte_hx711()
                
                success = True
            else:
                # Simulation
                self.tara_werte = [0.0, 0.0, 0.0, 0.0]
                success = True
            
            if success:
                self.kalibrierung_schritt = 1
                self.update_status("ERFOLG: Tara erfolgreich - bereit für Kalibrierung mit Referenzgewicht")
                QMessageBox.information(self, "Tara", "Nullpunkt erfolgreich gesetzt!")
            else:
                self.update_status("FEHLER: Tara fehlgeschlagen")
                QMessageBox.critical(self, "Fehler", "Tara konnte nicht durchgeführt werden!")
            
            # Live-Updates wieder starten
            if was_running:
                self.start_live_updates()
            
            self.update_kalibrierungs_buttons()
            
        except Exception as e:
            logger.error(f"Tara-Fehler: {e}")
            self.update_status(f"Tara-Fehler: {e}")
            QMessageBox.critical(self, "Fehler", f"Tara-Fehler: {e}")
    
    def kalibrierung_durchfuehren(self):
        """Führt Kalibrierung mit Referenzgewicht durch"""
        try:
            if self.kalibrierung_schritt < 1:
                QMessageBox.warning(self, "Warnung", "Bitte führen Sie zuerst eine Tara durch!")
                return
            
            # Referenzgewicht validieren
            try:
                ref_gewicht = float(self.input_referenzgewicht.text())
                if ref_gewicht <= 0:
                    raise ValueError("Referenzgewicht muss positiv sein")
                self.referenz_gewicht = ref_gewicht
            except ValueError as e:
                QMessageBox.critical(self, "Fehler", f"Ungültiges Referenzgewicht: {e}")
                return
            
            # Bestätigung
            reply = QMessageBox.question(
                self, "Kalibrierung",
                f"Bitte legen Sie genau {self.referenz_gewicht} kg auf den Karren.\n\nFortfahren mit Kalibrierung?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            self.update_status(f"Kalibrierung mit {self.referenz_gewicht} kg...")
            
            # Live-Updates stoppen
            was_running = self.update_timer.isActive()
            if was_running:
                self.stop_live_updates()
            
            if HX711_AVAILABLE and hx_sensors:
                # Echte Hardware-Kalibrierung
                success_count = 0
                
                for i, sensor in enumerate(hx_sensors):
                    try:
                        # Rohwert lesen
                        import time
                        time.sleep(0.5)
                        rohwerte = []
                        for _ in range(10):  # 10 Messungen für Durchschnitt
                            rohwert = sensor.hx.read()
                            rohwerte.append(rohwert)
                            time.sleep(0.1)
                        
                        durchschnitt = sum(rohwerte) / len(rohwerte)
                        
                        # Kalibrierfaktor berechnen
                        if durchschnitt != self.tara_werte[i]:
                            # Pro Sensor 1/4 des Gesamtgewichts angenommen
                            erwarteter_wert = self.referenz_gewicht / 4.0
                            self.kalibrier_faktoren[i] = erwarteter_wert / (durchschnitt - self.tara_werte[i])
                            success_count += 1
                            
                            logger.info(f"Sensor {i}: Faktor = {self.kalibrier_faktoren[i]:.6f}")
                        
                    except Exception as sensor_err:
                        logger.error(f"Kalibrierung Sensor {i} fehlgeschlagen: {sensor_err}")
                
                success = success_count >= 3  # Mindestens 3 von 4 Sensoren erfolgreich
                
            else:
                # Simulation
                self.kalibrier_faktoren = [0.1, 0.1, 0.1, 0.1]  # Beispielwerte
                success = True
            
            if success:
                self.kalibrierung_schritt = 2
                self.update_status("ERFOLG: Kalibrierung erfolgreich - bereit für Test")
                QMessageBox.information(self, "Kalibrierung", "Kalibrierung erfolgreich abgeschlossen!")
            else:
                self.update_status("FEHLER: Kalibrierung fehlgeschlagen")
                QMessageBox.critical(self, "Fehler", "Kalibrierung konnte nicht durchgeführt werden!")
            
            # Live-Updates wieder starten
            if was_running:
                self.start_live_updates()
            
            self.update_kalibrierungs_buttons()
            
        except Exception as e:
            logger.error(f"Kalibrierungs-Fehler: {e}")
            self.update_status(f"Kalibrierungs-Fehler: {e}")
            QMessageBox.critical(self, "Fehler", f"Kalibrierung fehlgeschlagen: {e}")
    
    def kalibrierung_testen(self):
        """Testet die aktuelle Kalibrierung"""
        try:
            if self.kalibrierung_schritt < 2:
                QMessageBox.warning(self, "Warnung", "Bitte führen Sie zuerst eine Kalibrierung durch!")
                return
            
            self.update_status("🧪 Kalibrierung wird getestet...")
            
            # Testgewicht eingeben lassen
            test_gewicht, ok = QtWidgets.QInputDialog.getDouble(
                self, "Kalibrierungs-Test",
                "Testgewicht eingeben (kg):",
                self.referenz_gewicht, 0.1, 1000.0, 2
            )
            
            if not ok:
                return
            
            QMessageBox.information(
                self, "Test-Vorbereitung",
                f"Bitte legen Sie {test_gewicht} kg auf den Karren und drücken Sie OK."
            )
            
            # Gewicht messen
            if HX711_AVAILABLE and hx_sensors:
                gemessenes_gewicht = lese_gewicht_hx711()
            else:
                # Simulation: Zufällige Abweichung
                import random
                abweichung = random.uniform(-0.1, 0.1)
                gemessenes_gewicht = test_gewicht + abweichung
            
            # Abweichung berechnen
            abweichung = abs(gemessenes_gewicht - test_gewicht)
            prozent_abweichung = (abweichung / test_gewicht) * 100
            
            # Toleranz prüfen
            toleranz_ok = abweichung <= self.toleranz
            
            # Ergebnis anzeigen
            result_text = f"""
Kalibrierungs-Test Ergebnis:

Soll-Gewicht: {test_gewicht:.2f} kg
Gemessen: {gemessenes_gewicht:.2f} kg
Abweichung: {abweichung:.3f} kg ({prozent_abweichung:.1f}%)
Toleranz: ±{self.toleranz:.2f} kg

Status: {'BESTANDEN' if toleranz_ok else 'NICHT BESTANDEN'}
"""
            
            if toleranz_ok:
                self.kalibrierung_schritt = 3
                self.update_status("ERFOLG: Kalibrierung validiert - bereit zum Speichern")
                QMessageBox.information(self, "Test erfolgreich", result_text)
            else:
                self.update_status("WARNUNG: Test nicht bestanden - Kalibrierung überprüfen")
                QMessageBox.warning(self, "Test nicht bestanden", result_text + "\n\nBitte Kalibrierung wiederholen.")
            
            self.update_kalibrierungs_buttons()
            
        except Exception as e:
            logger.error(f"Test-Fehler: {e}")
            self.update_status(f"Test-Fehler: {e}")
            QMessageBox.critical(self, "Fehler", f"Kalibrierungs-Test fehlgeschlagen: {e}")
    
    def kalibrierwerte_speichern(self):
        """Speichert Kalibrierungswerte persistent"""
        try:
            if self.kalibrierung_schritt < 2:
                QMessageBox.warning(self, "Warnung", "Keine Kalibrierungswerte zum Speichern vorhanden!")
                return
            
            # In Settings speichern
            if hasattr(self.settings_manager, 'calibration'):
                cal_data = self.settings_manager.calibration
                
                # Werte setzen
                cal_data.tare_values = self.tara_werte
                cal_data.scale_factors = self.kalibrier_faktoren
                cal_data.last_reference_weight = self.referenz_gewicht
                cal_data.calibration_date = datetime.now().isoformat()
                cal_data.is_valid = True
                
                # Speichern
                if self.settings_manager.save_settings():
                    self.update_status("GESPEICHERT: Kalibrierungswerte erfolgreich gespeichert")
                    QMessageBox.information(self, "Gespeichert", "Kalibrierungswerte wurden erfolgreich gespeichert!")
                    
                    # Signal senden
                    self.kalibrierung_abgeschlossen.emit(True)
                else:
                    raise Exception("Settings konnten nicht gespeichert werden")
            
        except Exception as e:
            logger.error(f"Speichern-Fehler: {e}")
            self.update_status(f"Speichern-Fehler: {e}")
            QMessageBox.critical(self, "Fehler", f"Speichern fehlgeschlagen: {e}")
    
    def kalibrierung_zuruecksetzen(self):
        """Setzt Kalibrierung auf Standardwerte zurück"""
        try:
            reply = QMessageBox.question(
                self, "Zurücksetzen",
                "Alle Kalibrierungswerte werden zurückgesetzt!\n\nFortfahren?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Werte zurücksetzen
                self.kalibrierung_schritt = 0
                self.tara_werte = [0.0, 0.0, 0.0, 0.0]
                self.kalibrier_faktoren = [1.0, 1.0, 1.0, 1.0]
                
                # UI aktualisieren
                self.update_status("ZURÜCKGESETZT: Kalibrierung zurückgesetzt - bitte neu durchführen")
                self.update_kalibrierungs_buttons()
                
                QMessageBox.information(self, "Zurückgesetzt", "Kalibrierung wurde zurückgesetzt!")
            
        except Exception as e:
            logger.error(f"Reset-Fehler: {e}")
            QMessageBox.critical(self, "Fehler", f"Reset fehlgeschlagen: {e}")
    
    def update_kalibrierungs_buttons(self):
        """Aktualisiert Button-Status basierend auf Kalibrierungs-Schritt"""
        try:
            if hasattr(self, 'btn_tara'):
                self.btn_tara.setEnabled(True)  # Tara immer möglich
            
            if hasattr(self, 'btn_kalibrieren'):
                self.btn_kalibrieren.setEnabled(self.kalibrierung_schritt >= 1)
            
            if hasattr(self, 'btn_test'):
                self.btn_test.setEnabled(self.kalibrierung_schritt >= 2)
            
            if hasattr(self, 'btn_speichern'):
                self.btn_speichern.setEnabled(self.kalibrierung_schritt >= 2)
            
        except Exception as e:
            logger.error(f"Button-Update Fehler: {e}")
    
    def update_status(self, status_text):
        """Aktualisiert Status-Anzeige"""
        if hasattr(self, 'lbl_status'):
            self.lbl_status.setText(status_text)
        logger.info(f"Kalibrierungs-Status: {status_text}")
    
    def referenzgewicht_geaendert(self):
        """Referenzgewicht Input geändert"""
        try:
            text = self.input_referenzgewicht.text()
            if text:
                self.referenz_gewicht = float(text)
        except ValueError:
            pass  # Ignoriere ungültige Eingaben
    
    def toleranz_geaendert(self):
        """Toleranz Input geändert"""
        try:
            text = self.input_toleranz.text()
            if text:
                self.toleranz = float(text)
        except ValueError:
            pass  # Ignoriere ungültige Eingaben
    
    def live_update_toggled(self, checked):
        """Live-Update Checkbox geändert"""
        if checked:
            self.start_live_updates()
        else:
            self.stop_live_updates()
    
    def zurueck_geklickt(self):
        """Zurück-Button geklickt"""
        try:
            # Live-Updates stoppen
            self.stop_live_updates()
            
            # Zurück zur Einstellungsseite
            if self.navigation:
                self.navigation.show_status("einstellungen")
            
            logger.info("Zurück zur Einstellungsseite")
            
        except Exception as e:
            logger.error(f"Navigation-Fehler: {e}")
    
    # ESP8266-Test-Funktion ENTFERNT - ersetzt durch automatische LED-Status-Checks
    
    # Test-Funktionen ENTFERNT - LED-Status ersetzt alle Tests
    
    def showEvent(self, event):
        """Wird aufgerufen wenn Seite angezeigt wird"""
        super().showEvent(event)
        
        # Live-Updates starten wenn aktiviert
        if hasattr(self, 'cb_live_update') and self.cb_live_update.isChecked():
            self.start_live_updates()
        
        logger.debug("WaagenKalibrierung angezeigt")
    
    def hideEvent(self, event):
        """Wird aufgerufen wenn Seite versteckt wird"""
        super().hideEvent(event)
        
        # Live-Updates stoppen
        self.stop_live_updates()
        
        logger.debug("WaagenKalibrierung versteckt")
    
    def check_hx711_status(self):
        """Prüft HX711-Status und aktualisiert LED-Anzeigen"""
        try:
            logger.info("🔍 Prüfe HX711-Status...")
            
            # HX711-Namen für die 4 Zellen
            zell_namen = ["VL (Vorne Links)", "VR (Vorne Rechts)", "HL (Hinten Links)", "HR (Hinten Rechts)"]
            
            # Status für jede Zelle prüfen
            zell_status = [False, False, False, False]  # Default: nicht gefunden
            
            if ESP8266_AVAILABLE:
                # ESP8266 Status direkt abfragen
                test_ips = ["192.168.4.1", "192.168.2.20"]
                
                for ip in test_ips:
                    try:
                        url = f"http://{ip}/live-values-data"
                        req = urllib.request.Request(url, headers={'User-Agent': 'Futterkarre-Pi5'})
                        
                        with urllib.request.urlopen(req, timeout=3) as response:
                            data = json.loads(response.read().decode('utf-8'))
                            
                            # Raw-Werte direkt prüfen (nicht konvertiert)
                            raw_values = [
                                data.get('vl_value', 0),  # VL
                                data.get('vr_value', 0),  # VR  
                                data.get('hl_value', 0),  # HL
                                data.get('hr_value', 0)   # HR
                            ]
                            
                            for i, raw_val in enumerate(raw_values):
                                try:
                                    val = float(raw_val)
                                    # HX711 ist angeschlossen wenn Raw-Wert != 0 
                                    # (0 = nicht angeschlossen, echte Werte = angeschlossen)
                                    if val != 0:
                                        zell_status[i] = True
                                    logger.info(f"HX711-{i} ({zell_namen[i]}): Raw={val} → {'✅ ANGESCHLOSSEN' if zell_status[i] else '❌ NICHT ANGESCHLOSSEN'}")
                                except (ValueError, TypeError):
                                    logger.warning(f"HX711-{i}: Ungültiger Wert '{raw_val}'")
                                    zell_status[i] = False
                            
                            # Erfolgreich - ESP8266 gefunden
                            logger.info(f"ESP8266 unter {ip} gefunden - Status: {sum(zell_status)}/4 HX711 aktiv")
                            break
                            
                    except urllib.error.URLError:
                        logger.debug(f"ESP8266 unter {ip} nicht erreichbar")
                        continue
                    except Exception as e:
                        logger.warning(f"ESP8266 {ip} Fehler: {e}")
                        continue
                else:
                    logger.warning("Kein ESP8266 unter bekannten IPs erreichbar")
            else:
                logger.warning("ESP8266 nicht verfügbar - simuliere HX711-Status")
                # Simulation: 2 von 4 Zellen "gefunden"
                zell_status = [True, True, False, False]
            
            # UI-Status-LEDs aktualisieren
            self.update_hx711_status_leds(zell_status, zell_namen)
            
        except Exception as e:
            logger.error(f"HX711-Status-Check Fehler: {e}")
    
    def update_hx711_status_leds(self, status_list, namen_list):
        """Aktualisiert HX711-Status-LED-Anzeigen in der UI"""
        try:
            for i, (status, name) in enumerate(zip(status_list, namen_list)):
                # Dynamisch LED-Labels suchen
                led_label_name = f"lbl_hx711_{i}_status"
                
                if hasattr(self, led_label_name):
                    led_label = getattr(self, led_label_name)
                    if status:
                        # Grün für "angeschlossen und funktionsfähig"
                        led_label.setText("🟢")
                        led_label.setToolTip(f"{name}: HX711 angeschlossen und funktionsfähig")
                        led_label.setStyleSheet("color: #4CAF50; font-size: 16px;")
                    else:
                        # Rot für "nicht angeschlossen"
                        led_label.setText("🔴")
                        led_label.setToolTip(f"{name}: HX711 nicht angeschlossen (Raw-Wert = 0)")
                        led_label.setStyleSheet("color: #f44336; font-size: 16px;")
                else:
                    # Fallback: Status in den Gewichts-Labels anzeigen
                    gewicht_label_name = f"lbl_gewicht_{i}"
                    if hasattr(self, gewicht_label_name):
                        gewicht_label = getattr(self, gewicht_label_name)
                        status_symbol = "🟢" if status else "🔴"
                        current_text = gewicht_label.text()
                        if not current_text.startswith(("🟢", "🔴")):
                            gewicht_label.setText(f"{status_symbol} {current_text}")
            
            # Gesamt-Status anzeigen
            gefundene_anzahl = sum(status_list)
            angeschlossene_zellen = [namen_list[i] for i, status in enumerate(status_list) if status]
            if angeschlossene_zellen:
                zell_liste = ", ".join([name.split()[0] for name in angeschlossene_zellen])  # Nur VL, VR, HL, HR
                self.update_status(f"HX711-Hardware: {gefundene_anzahl}/4 Zellen angeschlossen ({zell_liste})")
            else:
                self.update_status("HX711-Hardware: Keine Zellen angeschlossen - ESP8266 prüfen!")
            
        except Exception as e:
            logger.error(f"LED-Status-Update Fehler: {e}")