#!/usr/bin/env python3
"""
Wireless Weight Manager für ESP32-S3 Waage
Verbindet sich über WebSocket mit ESP32-Waage

Features:
- WebSocket-Client für ESP32-Kommunikation  
- Echtzeit-Gewichtsdaten empfangen
- Kalibrierungs-Kommandos senden
- Akku-Status überwachen
- Verbindungs-Monitoring
- Integration in bestehende Futterkarre-Software
"""

import asyncio
import websockets
import json
import logging
import threading
import time
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class WirelessWeightData:
    """Struktur für Wireless-Gewichtsdaten"""
    total_kg: float
    corner_1_kg: float 
    corner_2_kg: float
    corner_3_kg: float
    corner_4_kg: float
    battery_voltage: float
    wifi_rssi: int
    timestamp: datetime
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'WirelessWeightData':
        """Erstellt WirelessWeightData aus JSON-Daten"""
        corners = data.get('corners', [0.0, 0.0, 0.0, 0.0])
        
        return cls(
            total_kg=data.get('total_kg', 0.0),
            corner_1_kg=corners[0] if len(corners) > 0 else 0.0,
            corner_2_kg=corners[1] if len(corners) > 1 else 0.0,
            corner_3_kg=corners[2] if len(corners) > 2 else 0.0,
            corner_4_kg=corners[3] if len(corners) > 3 else 0.0,
            battery_voltage=data.get('battery_v', 0.0),
            wifi_rssi=data.get('wifi_rssi', -100),
            timestamp=datetime.now()
        )


class WirelessWeightManager:
    """
    Wireless Weight Manager für ESP32-S3 Waage
    
    Verwaltet WebSocket-Verbindung zu ESP32 und empfängt Gewichtsdaten
    """
    
    def __init__(self, esp32_ip: str, port: int = 81):
        self.esp32_ip = esp32_ip
        self.port = port
        self.websocket = None
        self.is_connected = False
        self.observers: List[Callable[[float, Optional[List[float]]], None]] = []
        self.last_weight = 0.0
        self.last_corners = None
        self.connection_status = "disconnected"
        self.battery_voltage = 0.0
        self.wifi_rssi = 0
        
        # Logging
        self.logger = logging.getLogger(f"WirelessWeightManager[{esp32_ip}]")
        
        # Threading für async WebSocket
        self._stop_event = Event()
        self._connection_thread = None
        self._loop = None
        
    def add_observer(self, callback: Callable[[float, Optional[List[float]]], None]):
        """Observer für Gewichts-Updates registrieren"""
        self.observers.append(callback)
        self.logger.debug(f"Observer registriert: {callback.__name__}")
        
    def remove_observer(self, callback: Callable[[float, Optional[List[float]]], None]):
        """Observer entfernen"""
        if callback in self.observers:
            self.observers.remove(callback)
            self.logger.debug(f"Observer entfernt: {callback.__name__}")
    
    async def connect(self):
        """Verbindung zu ESP32 herstellen"""
        try:
            uri = f"ws://{self.esp32_ip}:{self.port}"
            self.logger.info(f"Verbinde zu {uri}...")
            
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            self.connection_status = "connected"
            
            self.logger.info("✅ Verbindung zu ESP32 hergestellt")
            
            # Message-Loop starten
            await self._message_loop()
            
        except Exception as e:
            self.logger.error(f"❌ Verbindung fehlgeschlagen: {e}")
            self.is_connected = False
            self.connection_status = f"error: {e}"
            raise
    
    async def disconnect(self):
        """Verbindung trennen"""
        self.is_connected = False
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        self.connection_status = "disconnected"
        self.logger.info("Verbindung getrennt")
    
    async def send_command(self, command: dict) -> Optional[dict]:
        """Kommando an ESP32 senden"""
        if not self.websocket:
            raise ConnectionError("Nicht mit ESP32 verbunden")
            
        try:
            message = json.dumps(command)
            await self.websocket.send(message)
            self.logger.debug(f"Kommando gesendet: {command}")
            
            # Antwort empfangen (mit Timeout)
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            return json.loads(response)
            
        except Exception as e:
            self.logger.error(f"Kommando fehlgeschlagen: {e}")
            return None
    
    async def send_tare(self) -> Optional[dict]:
        """Waage nullen (Tare)"""
        return await self.send_command({"command": "tare"})
    
    async def send_calibrate(self, weight: float) -> Optional[dict]:
        """Kalibrierung mit bekanntem Gewicht"""
        return await self.send_command({"command": "calibrate", "weight": weight})
    
    async def get_status(self) -> Optional[dict]:
        """ESP32-Status abfragen"""
        return await self.send_command({"command": "get_status"})
    
    async def _message_loop(self):
        """Haupt-Message-Loop für WebSocket"""
        try:
            while self.is_connected:
                message = await self.websocket.recv()
                await self._handle_message(message)
                
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("WebSocket-Verbindung geschlossen")
            self.is_connected = False
        except Exception as e:
            self.logger.error(f"Message-Loop Fehler: {e}")
            self.is_connected = False
    
    async def _handle_message(self, message: str):
        """WebSocket-Message verarbeiten"""
        try:
            data = json.loads(message)
            
            if data.get("type") == "weight_data":
                # Gewichtsdaten verarbeiten
                total_weight = data.get("total_kg", 0.0)
                corners = data.get("corners", [])
                
                self.last_weight = total_weight
                self.last_corners = corners if corners else None
                self.battery_voltage = data.get("battery_v", 0.0)
                self.wifi_rssi = data.get("wifi_rssi", 0)
                
                # Observer benachrichtigen
                for observer in self.observers:
                    try:
                        observer(total_weight, corners if corners else None)
                    except Exception as e:
                        self.logger.error(f"Observer-Fehler: {e}")
                        
            elif data.get("type") == "response":
                # Kommando-Antwort (wird von send_command verarbeitet)
                pass
                
            else:
                self.logger.warning(f"Unbekannte Message: {data}")
                
        except Exception as e:
            self.logger.error(f"Message-Verarbeitung fehlgeschlagen: {e}")
        
    def start(self):
        """Startet Wireless-Verbindung"""
        if self.running:
            return
            
        self.running = True
        self.connection_thread = threading.Thread(target=self._connection_loop, daemon=True)
        self.connection_thread.start()
        
        logger.info(f"📡 Wireless Weight Manager gestartet - Verbinde zu {self.websocket_url}")
    
    def stop(self):
        """Stoppt Wireless-Verbindung"""
        self.running = False
        
        if self.websocket:
            asyncio.create_task(self.websocket.close())
            
        if self.connection_thread:
            self.connection_thread.join(timeout=2.0)
            
        logger.info("🛑 Wireless Weight Manager gestoppt")
    
    def _connection_loop(self):
        """Haupt-Connection-Loop (läuft in separatem Thread)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self.running:
            try:
                loop.run_until_complete(self._connect_and_listen())
                
            except Exception as e:
                logger.error(f"❌ Wireless-Verbindungsfehler: {e}")
                self.last_error = str(e)
                self._notify_connection_observers(False)
                
                # Exponential Backoff für Reconnect
                wait_time = min(2 ** self.reconnect_attempts, 30)
                logger.info(f"🔄 Reconnect in {wait_time}s (Versuch {self.reconnect_attempts + 1})")
                
                for _ in range(wait_time * 10):  # 0.1s Schritte für responsives Shutdown
                    if not self.running:
                        break
                    time.sleep(0.1)
                
                self.reconnect_attempts += 1
                if self.reconnect_attempts >= self.max_reconnect_attempts:
                    logger.error("🚫 Maximale Reconnect-Versuche erreicht")
                    break
        
        loop.close()
    
    async def _connect_and_listen(self):
        """WebSocket-Verbindung und Message-Handling"""
        logger.info(f"🔌 Verbinde zu ESP32-Waage: {self.websocket_url}")
        
        async with websockets.connect(
            self.websocket_url,
            ping_interval=30,
            ping_timeout=10,
            close_timeout=5
        ) as websocket:
            
            self.websocket = websocket
            self.connected = True
            self.reconnect_attempts = 0
            self.last_error = None
            
            logger.info("✅ ESP32-Waage verbunden")
            self._notify_connection_observers(True)
            
            # Status abfragen nach Verbindung
            await self._send_command("get_status")
            
            # Message-Loop
            async for message in websocket:
                try:
                    await self._handle_message(message)
                except Exception as e:
                    logger.error(f"❌ Message-Handler-Fehler: {e}")
    
    async def _handle_message(self, message: str):
        """Verarbeitet eingehende WebSocket-Messages"""
        try:
            data = json.loads(message)
            message_type = data.get('type', 'unknown')
            
            if message_type == 'weight_data':
                self._handle_weight_data(data)
                
            elif message_type == 'welcome':
                self._handle_welcome(data)
                
            elif message_type == 'response':
                self._handle_response(data)
                
            elif message_type == 'status':
                self._handle_status(data)
                
            elif message_type == 'battery_critical':
                self._handle_battery_critical(data)
                
            else:
                logger.debug(f"🔍 Unbekannte Message: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON-Parse-Fehler: {e}")
        except Exception as e:
            logger.error(f"❌ Message-Handler-Fehler: {e}")
    
    def _handle_weight_data(self, data: Dict[str, Any]):
        """Verarbeitet Gewichtsdaten vom ESP32"""
        try:
            weight_data = WirelessWeightData.from_json(data)
            self.current_weight = weight_data
            
            # Observer benachrichtigen
            self._notify_weight_observers(weight_data)
            
            # Debug-Logging (nur gelegentlich)
            if int(time.time()) % 5 == 0:  # Alle 5 Sekunden
                logger.debug(f"📊 Gewicht: {weight_data.total_kg:.2f}kg, "
                           f"Akku: {weight_data.battery_voltage:.1f}V, "
                           f"WiFi: {weight_data.wifi_rssi}dBm")
            
        except Exception as e:
            logger.error(f"❌ Gewichtsdaten-Verarbeitung fehlgeschlagen: {e}")
    
    def _handle_welcome(self, data: Dict[str, Any]):
        """Welcome-Message vom ESP32"""
        device = data.get('device', 'Unknown')
        version = data.get('version', '0.0')
        features = data.get('features', 'None')
        
        logger.info(f"👋 ESP32-Waage verbunden: {device} v{version}")
        logger.info(f"🔧 Features: {features}")
    
    def _handle_response(self, data: Dict[str, Any]):
        """Response auf gesendete Kommandos"""
        command = data.get('command', 'unknown')
        status = data.get('status', 'unknown')
        message = data.get('message', '')
        
        logger.info(f"📨 ESP32-Response: {command} → {status} ({message})")
        
        # Kalibrierungs-Callback
        if command == 'calibrate' and self.calibration_callback:
            success = status == 'success'
            self.calibration_callback(success, message)
            self.calibration_callback = None
            self.calibration_active = False
    
    def _handle_status(self, data: Dict[str, Any]):
        """Status-Daten vom ESP32"""
        uptime = data.get('uptime_ms', 0) / 1000
        battery = data.get('battery_voltage', 0.0)
        rssi = data.get('wifi_rssi', -100)
        free_heap = data.get('free_heap', 0)
        hx711_ready = data.get('hx711_ready', [])
        
        logger.info(f"📊 ESP32-Status: Uptime {uptime:.1f}s, "
                   f"Akku {battery:.1f}V, WiFi {rssi}dBm, "
                   f"RAM {free_heap}B, HX711 {sum(hx711_ready)}/4")
    
    def _handle_battery_critical(self, data: Dict[str, Any]):
        """Kritischer Akku-Stand"""
        voltage = data.get('voltage', 0.0)
        message = data.get('message', 'Battery critical')
        
        logger.warning(f"🔋 ESP32-Akku kritisch: {voltage:.1f}V - {message}")
        
        # UI benachrichtigen (falls Observer registriert)
        for observer in self.connection_observers:
            try:
                observer(False)  # Verbindung wird gleich getrennt
            except Exception as e:
                logger.error(f"Observer-Fehler: {e}")
    
    async def _send_command(self, command: str, **kwargs):
        """Sendet Kommando an ESP32"""
        if not self.websocket or not self.connected:
            logger.warning(f"❌ Kann Kommando '{command}' nicht senden - keine Verbindung")
            return False
        
        try:
            message = {
                'command': command,
                'timestamp': int(time.time() * 1000),
                **kwargs
            }
            
            await self.websocket.send(json.dumps(message))
            logger.debug(f"📤 Kommando gesendet: {command}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Kommando-Senden fehlgeschlagen: {e}")
            return False
    
    # =================== PUBLIC API ===================
    
    def get_current_weight(self) -> Optional[WirelessWeightData]:
        """Liefert aktuelle Gewichtsdaten"""
        return self.current_weight
    
    def get_weight_kg(self) -> float:
        """Liefert aktuelles Gesamt-Gewicht in kg"""
        if self.current_weight:
            return self.current_weight.total_kg
        return 0.0
    
    def is_connected(self) -> bool:
        """Prüft ob ESP32-Verbindung aktiv ist"""
        return self.connected
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Liefert detaillierte Verbindungs-Informationen"""
        return {
            'connected': self.connected,
            'esp32_url': self.websocket_url,
            'last_error': self.last_error,
            'reconnect_attempts': self.reconnect_attempts,
            'current_weight_available': self.current_weight is not None,
            'battery_voltage': self.current_weight.battery_voltage if self.current_weight else 0.0,
            'wifi_signal': self.current_weight.wifi_rssi if self.current_weight else -100
        }
    
    def tare_scale(self, callback: Optional[Callable[[bool, str], None]] = None):
        """Nullt die Waage (Tare)"""
        if not self.connected:
            if callback:
                callback(False, "Keine ESP32-Verbindung")
            return
        
        async def _tare():
            success = await self._send_command("tare")
            if callback and not success:
                callback(False, "Kommando senden fehlgeschlagen")
        
        asyncio.create_task(_tare())
    
    def calibrate_scale(self, known_weight_kg: float, callback: Optional[Callable[[bool, str], None]] = None):
        """Kalibriert die Waage mit bekanntem Gewicht"""
        if not self.connected:
            if callback:
                callback(False, "Keine ESP32-Verbindung")
            return
        
        if self.calibration_active:
            if callback:
                callback(False, "Kalibrierung bereits aktiv")
            return
        
        self.calibration_active = True
        self.calibration_callback = callback
        
        async def _calibrate():
            success = await self._send_command("calibrate", weight=known_weight_kg)
            if not success and callback:
                callback(False, "Kommando senden fehlgeschlagen")
                self.calibration_active = False
                self.calibration_callback = None
        
        asyncio.create_task(_calibrate())
    
    def request_deep_sleep(self):
        """Schickt ESP32 in Deep Sleep (Stromsparmodus)"""
        if self.connected:
            async def _sleep():
                await self._send_command("deep_sleep")
            
            asyncio.create_task(_sleep())
    
    # =================== OBSERVER PATTERN ===================
    
    def add_weight_observer(self, callback: Callable[[WirelessWeightData], None]):
        """Registriert Observer für Gewichtsdaten-Updates"""
        if callback not in self.weight_observers:
            self.weight_observers.append(callback)
            logger.debug(f"📊 Weight-Observer registriert: {callback.__name__}")
    
    def remove_weight_observer(self, callback: Callable[[WirelessWeightData], None]):
        """Entfernt Weight-Observer"""
        if callback in self.weight_observers:
            self.weight_observers.remove(callback)
            logger.debug(f"📊 Weight-Observer entfernt: {callback.__name__}")
    
    def add_connection_observer(self, callback: Callable[[bool], None]):
        """Registriert Observer für Verbindungsstatus-Updates"""
        if callback not in self.connection_observers:
            self.connection_observers.append(callback)
            logger.debug(f"🔗 Connection-Observer registriert: {callback.__name__}")
    
    def remove_connection_observer(self, callback: Callable[[bool], None]):
        """Entfernt Connection-Observer"""
        if callback in self.connection_observers:
            self.connection_observers.remove(callback)
            logger.debug(f"🔗 Connection-Observer entfernt: {callback.__name__}")
    
    def _notify_weight_observers(self, weight_data: WirelessWeightData):
        """Benachrichtigt alle Weight-Observer"""
        for observer in self.weight_observers[:]:  # Copy für Thread-Safety
            try:
                observer(weight_data)
            except Exception as e:
                logger.error(f"❌ Weight-Observer-Fehler: {e}")
    
    def _notify_connection_observers(self, connected: bool):
        """Benachrichtigt alle Connection-Observer"""
        self.connected = connected
        
        for observer in self.connection_observers[:]:  # Copy für Thread-Safety
            try:
                observer(connected)
            except Exception as e:
                logger.error(f"❌ Connection-Observer-Fehler: {e}")


# =================== INTEGRATION IN BESTEHENDE FUTTERKARRE ===================

class WirelessWeightManagerAdapter:
    """
    Adapter-Klasse für Integration in bestehende WeightManager-Architektur
    Macht WirelessWeightManager kompatibel mit bestehender Futterkarre-Software
    """
    
    def __init__(self, esp32_ip: str = "192.168.1.100"):
        self.wireless_manager = WirelessWeightManager(esp32_ip)
        self.wireless_manager.start()
        
        # Für Kompatibilität mit bestehendem WeightManager
        self.hardware_available = False
        self.observers = []
        
        # Connection-Observer für Hardware-Status
        self.wireless_manager.add_connection_observer(self._on_connection_changed)
    
    def _on_connection_changed(self, connected: bool):
        """Callback für Verbindungsänderungen"""
        self.hardware_available = connected
        
        if connected:
            logger.info("✅ Wireless-Waage verfügbar - Hardware-Status: True")
        else:
            logger.warning("❌ Wireless-Waage nicht verfügbar - Hardware-Status: False")
    
    def read_weight(self) -> float:
        """Kompatibilitäts-Methode - liefert aktuelles Gewicht"""
        return self.wireless_manager.get_weight_kg()
    
    def tare(self):
        """Kompatibilitäts-Methode - Waage nullen"""
        self.wireless_manager.tare_scale()
    
    def is_hardware_available(self) -> bool:
        """Kompatibilitäts-Methode - Hardware-Status"""
        return self.hardware_available
    
    def add_observer(self, callback):
        """Kompatibilitäts-Methode - Observer hinzufügen"""
        self.observers.append(callback)
        
        # Weight-Observer für Wireless-Updates
        def weight_observer(weight_data: WirelessWeightData):
            for obs in self.observers:
                try:
                    obs(weight_data.total_kg)
                except Exception as e:
                    logger.error(f"Observer-Fehler: {e}")
        
        self.wireless_manager.add_weight_observer(weight_observer)
    
    def stop(self):
        """Stoppt Wireless-Manager"""
        self.wireless_manager.stop()


# =================== BEISPIEL-VERWENDUNG ===================

if __name__ == "__main__":
    # Test-Setup für Wireless-Waage
    import time
    
    # Logging konfigurieren
    logging.basicConfig(level=logging.INFO)
    
    # Wireless-Manager starten
    manager = WirelessWeightManager("192.168.1.100")
    
    # Observer registrieren
    def on_weight_update(weight_data: WirelessWeightData):
        print(f"📊 Gewicht: {weight_data.total_kg:.2f}kg "
              f"(Ecken: {weight_data.corner_1_kg:.1f}, {weight_data.corner_2_kg:.1f}, "
              f"{weight_data.corner_3_kg:.1f}, {weight_data.corner_4_kg:.1f}) "
              f"Akku: {weight_data.battery_voltage:.1f}V")
    
    def on_connection_change(connected: bool):
        status = "✅ Verbunden" if connected else "❌ Getrennt"
        print(f"🔗 ESP32-Waage: {status}")
    
    manager.add_weight_observer(on_weight_update)
    manager.add_connection_observer(on_connection_change)
    
    # Starten
    manager.start()
    
    try:
        # 30 Sekunden laufen lassen
        time.sleep(30)
        
        # Tare-Test
        print("🎯 Teste Tare...")
        manager.tare_scale(lambda success, msg: print(f"Tare: {msg}"))
        
        time.sleep(5)
        
        # Kalibrierungs-Test (10kg)
        print("📏 Teste Kalibrierung mit 10kg...")
        manager.calibrate_scale(10.0, lambda success, msg: print(f"Kalibrierung: {msg}"))
        
        time.sleep(10)
        
    except KeyboardInterrupt:
        print("👋 Beende Test...")
    
    finally:
        manager.stop()
        print("✅ Test beendet")