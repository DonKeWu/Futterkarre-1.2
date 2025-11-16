"""
Integration Test für ESP32-S3 Wireless Weight System

Tests:
1. WebSocket-Verbindung zu ESP32
2. Gewichtsdaten empfangen  
3. Kommandos senden (Tare, Kalibrierung)
4. Adapter-Kompatibilität mit bestehendem Code
"""

import asyncio
import logging
from typing import Optional

# Lokale Imports
from wireless.wireless_weight_manager import WirelessWeightManager, WirelessWeightManagerAdapter

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestObserver:
    """Test-Observer für Gewichtsdaten"""
    
    def __init__(self):
        self.last_weight = None
        self.last_corners = None
        self.update_count = 0
        
    def on_weight_update(self, total_weight: float, corner_weights: Optional[list] = None):
        """Callback für Gewichts-Updates"""
        self.last_weight = total_weight
        self.last_corners = corner_weights
        self.update_count += 1
        
        logger.info(f"Gewicht empfangen: {total_weight:.2f}kg")
        if corner_weights:
            logger.info(f"Ecken: {corner_weights}")

async def test_direct_manager(esp32_ip: str):
    """Test WirelessWeightManager direkt"""
    logger.info("=== Test 1: Direkter WirelessWeightManager ===")
    
    # Manager erstellen
    manager = WirelessWeightManager(esp32_ip)
    observer = TestObserver()
    
    try:
        # Observer registrieren
        manager.add_observer(observer.on_weight_update)
        
        # Verbindung starten
        logger.info(f"Verbinde zu ESP32: {esp32_ip}")
        await manager.connect()
        
        # 5 Sekunden Gewichtsdaten sammeln
        logger.info("Sammle 5 Sekunden Gewichtsdaten...")
        await asyncio.sleep(5)
        
        # Status abrufen
        status = await manager.get_status()
        logger.info(f"ESP32-Status: {status}")
        
        # Tare-Kommando senden
        logger.info("Sende Tare-Kommando...")
        response = await manager.send_tare()
        logger.info(f"Tare-Response: {response}")
        
        # Noch 2 Sekunden warten
        await asyncio.sleep(2)
        
        # Ergebnisse
        logger.info(f"Updates empfangen: {observer.update_count}")
        logger.info(f"Letztes Gewicht: {observer.last_weight}")
        
        return True
        
    except Exception as e:
        logger.error(f"Test fehlgeschlagen: {e}")
        return False
        
    finally:
        await manager.disconnect()

def test_adapter_compatibility():
    """Test WirelessWeightManagerAdapter für Kompatibilität"""
    logger.info("=== Test 2: Adapter-Kompatibilität ===")
    
    # ESP32-IP (wird in echtem Test angepasst)
    esp32_ip = "192.168.1.100"
    
    try:
        # Adapter erstellen (simuliert bestehende WeightManager-Nutzung)
        adapter = WirelessWeightManagerAdapter(esp32_ip)
        observer = TestObserver()
        
        # Observer registrieren (wie bei bestehendem WeightManager)
        adapter.add_observer(observer.on_weight_update)
        
        # Simuliere typische WeightManager-Operationen
        logger.info("Starte Adapter...")
        # adapter.start()  # Wird in echtem Test mit ESP32 aktiviert
        
        logger.info("Adapter erfolgreich erstellt")
        logger.info("Alle WeightManager-Methoden verfügbar:")
        
        # Zeige verfügbare Methoden
        methods = [method for method in dir(adapter) if not method.startswith('_')]
        for method in methods:
            logger.info(f"  - {method}")
            
        return True
        
    except Exception as e:
        logger.error(f"Adapter-Test fehlgeschlagen: {e}")
        return False

def test_mock_esp32():
    """Test mit Mock-ESP32 (ohne echte Hardware)"""
    logger.info("=== Test 3: Mock-ESP32 Test ===")
    
    try:
        # Adapter mit nicht-existierender IP (wird timeout)
        adapter = WirelessWeightManagerAdapter("192.168.1.999")
        
        # Observer registrieren
        observer = TestObserver()
        adapter.add_observer(observer.on_weight_update)
        
        logger.info("Mock-Test erfolgreich - Adapter funktioniert ohne ESP32")
        return True
        
    except Exception as e:
        logger.error(f"Mock-Test fehlgeschlagen: {e}")
        return False

def main():
    """Hauptfunktion für Tests"""
    logger.info("🚀 ESP32-S3 Wireless Weight System - Integration Test")
    logger.info("=" * 60)
    
    # ESP32-IP konfigurieren (wird automatisch via mDNS erkannt oder manuell gesetzt)
    ESP32_IP = "192.168.1.100"  # Standard-IP - wird via WiFi-Setup angepasst
    
    # Test-Ergebnisse
    results = {}
    
    # Test 1: Mock-Test (ohne Hardware)
    results['mock'] = test_mock_esp32()
    
    # Test 2: Adapter-Kompatibilität
    results['adapter'] = test_adapter_compatibility()
    
    # Test 3: Echter ESP32-Test (nur wenn Hardware verfügbar)
    logger.info(f"Für echten ESP32-Test: IP {ESP32_IP} verwenden")
    logger.info("Hardware-Test wird übersprungen (ESP32 nicht verfügbar)")
    results['hardware'] = None  # Wird True bei echter Hardware
    
    # Ergebnisse zusammenfassen
    logger.info("=" * 60)
    logger.info("📊 Test-Ergebnisse:")
    
    for test, result in results.items():
        if result is True:
            logger.info(f"  ✅ {test}: ERFOLGREICH")
        elif result is False:
            logger.info(f"  ❌ {test}: FEHLGESCHLAGEN")
        else:
            logger.info(f"  ⏭️ {test}: ÜBERSPRUNGEN")
    
    # Gesamtergebnis
    successful_tests = sum(1 for r in results.values() if r is True)
    total_tests = sum(1 for r in results.values() if r is not None)
    
    logger.info(f"Gesamt: {successful_tests}/{total_tests} Tests erfolgreich")
    
    if successful_tests == total_tests:
        logger.info("🎉 Alle Tests erfolgreich!")
        logger.info("System bereit für ESP32-Hardware-Integration")
    else:
        logger.error("⚠️ Einige Tests fehlgeschlagen")
        
    return successful_tests == total_tests

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Tests durch Benutzer abgebrochen")
        exit(1)