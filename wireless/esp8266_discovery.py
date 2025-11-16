#!/usr/bin/env python3
"""
ESP8266 Auto-Discovery für Hybrid WiFi-System
Findet ESP8266 automatisch in beiden Modi:
1. Stall-Modus: Futterkarre_WiFi (192.168.4.1)
2. Haus-Modus: Heimnetz (192.168.2.x)
"""

import subprocess
import asyncio
import json
import logging
from typing import Optional, Tuple
import time
import urllib.request
import urllib.error
import socket

# Websockets optional - fallback für Entwicklung
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logging.getLogger(__name__).warning("websockets-Modul nicht verfügbar - ESP8266Discovery deaktiviert")

logger = logging.getLogger(__name__)

class ESP8266Discovery:
    def __init__(self):
        self.esp8266_ip = None
        self.connection_mode = None
        self.last_scan_time = 0
        
    async def find_esp8266(self, force_rescan: bool = False) -> Optional[Tuple[str, str]]:
        """
        Findet ESP8266 in beiden Modi
        
        Returns:
            (ip, mode) oder None falls nicht gefunden
            mode: "stall" oder "haus"
        """
        # WebSockets-Check
        if not WEBSOCKETS_AVAILABLE:
            logger.warning("ESP8266Discovery: websockets-Modul fehlt")
            return None
            
        # Cache für 30 Sekunden
        if not force_rescan and time.time() - self.last_scan_time < 30:
            if self.esp8266_ip and self.connection_mode:
                return (self.esp8266_ip, self.connection_mode)
        
        logger.info("🔍 ESP8266 Auto-Discovery gestartet...")
        
        # 1. Prüfe Stall-Modus (Futterkarre_WiFi)
        stall_ip = await self.check_stall_mode()
        if stall_ip:
            self.esp8266_ip = stall_ip
            self.connection_mode = "stall"
            self.last_scan_time = time.time()
            logger.info(f"✅ ESP8266 gefunden: {stall_ip} (Stall-Modus)")
            return (stall_ip, "stall")
        
        # 2. Prüfe Haus-Modus (Heimnetz)
        haus_ip = await self.check_haus_mode()
        if haus_ip:
            self.esp8266_ip = haus_ip
            self.connection_mode = "haus"
            self.last_scan_time = time.time()
            logger.info(f"✅ ESP8266 gefunden: {haus_ip} (Haus-Modus)")
            return (haus_ip, "haus")
        
        logger.warning("❌ ESP8266 nicht gefunden")
        return None
    
    async def check_stall_mode(self) -> Optional[str]:
        """Prüft ob Futterkarre_WiFi verfügbar ist"""
        try:
            # Prüfe ob wir mit Futterkarre_WiFi verbunden sind
            if await self.is_connected_to_futterkarre_wifi():
                # Teste direkte Verbindung zu ESP8266 via HTTP
                if self.test_http_status("192.168.4.1"):
                    return "192.168.4.1"
            
            return None
            
        except Exception as e:
            logger.debug(f"Stall-Modus Test Fehler: {e}")
            return None
    
    async def check_haus_mode(self) -> Optional[str]:
        """Scannt Heimnetz nach ESP8266"""
        try:
            # Bestimme Heimnetz-Range
            network_base = "192.168.2"  # Dein Heimnetz
            
            # Teste gängige ESP8266 IP-Bereiche mit HTTP
            for i in range(100, 200):
                ip = f"{network_base}.{i}"
                if self.test_http_status(ip):
                    return ip
            
            return None
            
        except Exception as e:
            logger.debug(f"Haus-Modus Test Fehler: {e}")
            return None
    
    async def is_connected_to_futterkarre_wifi(self) -> bool:
        """Prüft ob Pi5 mit Futterkarre_WiFi verbunden ist"""
        try:
            # Prüfe aktuelle WiFi-Verbindung
            result = subprocess.run(['iwgetid', '-r'], 
                                 capture_output=True, text=True, timeout=5)
            current_ssid = result.stdout.strip()
            
            return current_ssid == "Futterkarre_WiFi"
            
        except Exception:
            return False
    
    def test_http_status(self, ip: str, timeout: float = 3.0) -> Optional[dict]:
        """Testet HTTP /status API und gibt ESP8266-Status zurück"""
        try:
            url = f"http://{ip}/status"
            
            # HTTP Request mit Timeout
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    # Prüfe ob es wirklich ein ESP8266 ist
                    if data.get("device_name") == "FutterWaage_ESP8266":
                        return data
            
            return None
            
        except (urllib.error.URLError, socket.timeout, json.JSONDecodeError):
            return None
    
    async def test_websocket(self, ip: str, timeout: float = 2.0) -> bool:
        """Testet WebSocket-Verbindung zu IP"""
        if not WEBSOCKETS_AVAILABLE:
            return False
            
        try:
            uri = f"ws://{ip}:81"
            websocket = await asyncio.wait_for(
                websockets.connect(uri), timeout=timeout
            )
            
            # Status-Kommando senden
            status_cmd = {"command": "get_status"}
            await websocket.send(json.dumps(status_cmd))
            
            # Antwort empfangen
            response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
            data = json.loads(response)
            
            await websocket.close()
            
            # Prüfe ob es wirklich ein ESP8266 ist
            return data.get("device") == "FutterWaage_ESP8266"
            
        except Exception:
            return False
    
    async def connect_to_stall_wifi(self) -> bool:
        """Verbindet Pi5 mit Futterkarre_WiFi"""
        try:
            logger.info("📡 Verbinde mit Futterkarre_WiFi...")
            
            # NetworkManager verwenden
            cmd = [
                'nmcli', 'device', 'wifi', 'connect', 'Futterkarre_WiFi', 
                'password', 'FutterWaage2025'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("✅ Futterkarre_WiFi Verbindung erfolgreich")
                # Kurz warten bis IP zugewiesen
                await asyncio.sleep(3)
                return True
            else:
                logger.error(f"❌ WiFi-Verbindung fehlgeschlagen: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Fehler bei WiFi-Verbindung: {e}")
            return False
    
    async def get_connection_info(self) -> dict:
        """Liefert detaillierte Verbindungsinfos"""
        esp_info = await self.find_esp8266()
        
        if not esp_info:
            return {
                "connected": False,
                "mode": None,
                "ip": None,
                "status": "ESP8266 nicht gefunden"
            }
        
        ip, mode = esp_info
        
        return {
            "connected": True,
            "mode": mode,
            "ip": ip,
            "status": f"Verbunden ({mode}-Modus)",
            "wifi_network": "Futterkarre_WiFi" if mode == "stall" else "Heimnetz"
        }
    
    async def get_esp8266_status_async(self, ip: Optional[str] = None) -> str:
        """Async Status-Ausgabe für UI-Integration"""
        try:
            # Falls IP gegeben, direkt verwenden
            if ip:
                if await self.test_websocket(ip):
                    # Bestimme Modus basierend auf IP
                    if ip == "192.168.4.1":
                        return f"ESP8266: {ip} (Stall)"
                    else:
                        return f"ESP8266: {ip} (Haus)"
                else:
                    return f"ESP8266: {ip} nicht erreichbar"
            
            # Automatische Suche
            esp_info = await self.find_esp8266()
            
            if not esp_info:
                return "ESP8266: Nicht gefunden"
            
            ip, mode = esp_info
            mode_text = "Stall" if mode == "stall" else "Haus"
            return f"ESP8266: {ip} ({mode_text})"
            
        except Exception as e:
            logger.error(f"Fehler bei ESP8266-Status: {e}")
            return f"ESP8266: Fehler - {str(e)}"
    
    def get_esp8266_status(self, ip: Optional[str] = None) -> str:
        """Synchroner Wrapper für UI-Integration"""
        try:
            # Neuen Event Loop in Thread erstellen
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.get_esp8266_status_async(ip))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Fehler bei synchronem ESP8266-Status: {e}")
            return f"ESP8266: Sync-Fehler - {str(e)}"

# Singleton für globale Verwendung
esp8266_discovery = ESP8266Discovery()

async def get_esp8266_connection() -> Optional[Tuple[str, str]]:
    """Convenience-Funktion für ESP8266-Verbindung"""
    return await esp8266_discovery.find_esp8266()

def get_esp8266_status(ip: str) -> Optional[dict]:
    """Holt aktuellen ESP8266 Status via HTTP"""
    discovery = ESP8266Discovery()
    return discovery.test_http_status(ip)

if __name__ == "__main__":
    # Test-Script
    async def test_discovery():
        logging.basicConfig(level=logging.INFO)
        
        discovery = ESP8266Discovery()
        
        print("🔍 ESP8266 Discovery Test")
        print("=" * 40)
        
        result = await discovery.find_esp8266(force_rescan=True)
        
        if result:
            ip, mode = result
            print(f"✅ ESP8266 gefunden: {ip} ({mode}-Modus)")
            
            # Verbindungsinfo anzeigen
            info = await discovery.get_connection_info()
            print(f"📊 Status: {info['status']}")
            print(f"📡 WiFi: {info['wifi_network']}")
            
        else:
            print("❌ ESP8266 nicht gefunden")
            print("\n🔧 Troubleshooting:")
            print("   1. ESP8266 eingeschaltet?")
            print("   2. Im Stall: Futterkarre_WiFi sichtbar?")
            print("   3. Im Haus: ESP8266 im Heimnetz?")
    
    asyncio.run(test_discovery())