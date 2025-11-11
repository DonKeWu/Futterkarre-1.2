"""
ESP32-S3 Wireless Weight Manager für Futterkarre

Dieses Modul stellt eine WebSocket-basierte Verbindung zu einer ESP32-S3
Waage her und integriert sich nahtlos in die bestehende Futterkarre-Architektur.
"""

import asyncio
import json
import logging
import time
from typing import List, Optional, Callable
from threading import Thread, Event
import websockets


class WirelessWeightManager:
    """
    Wireless Weight Manager für ESP32-S3 Waage
    
    Verwaltet WebSocket-Verbindung zu ESP32 und empfängt Gewichtsdaten
    """
    
    def __init__(self, esp32_ip: str, port: int = 81):
        self.esp32_ip = esp32_ip
        self.port = port
        self.websocket = None
        self._is_connected = False
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
        
    @property
    def is_connected(self) -> bool:
        """Verbindungsstatus abfragen"""
        return self._is_connected
    
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
            self._is_connected = True
            self.connection_status = "connected"
            
            self.logger.info("✅ Verbindung zu ESP32 hergestellt")
            
            # Message-Loop starten
            await self._message_loop()
            
        except Exception as e:
            self.logger.error(f"❌ Verbindung fehlgeschlagen: {e}")
            self._is_connected = False
            self.connection_status = f"error: {e}"
            raise
    
    async def disconnect(self):
        """Verbindung trennen"""
        self._is_connected = False
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
            while self._is_connected and self.websocket:
                message = await self.websocket.recv()
                await self._handle_message(str(message))
                
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("WebSocket-Verbindung geschlossen")
            self._is_connected = False
        except Exception as e:
            self.logger.error(f"Message-Loop Fehler: {e}")
            self._is_connected = False
    
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


class WirelessWeightManagerAdapter:
    """
    Adapter-Klasse für nahtlose Integration in bestehende Futterkarre-Architektur
    
    Diese Klasse implementiert die gleiche API wie der bestehende WeightManager,
    aber nutzt intern die ESP32-WebSocket-Verbindung.
    """
    
    def __init__(self, esp32_ip: str, port: int = 81):
        self.esp32_ip = esp32_ip
        self.port = port
        self.wireless_manager = WirelessWeightManager(esp32_ip, port)
        self.observers: List[Callable[[float, Optional[List[float]]], None]] = []
        
        # Threading für async Operations
        self._loop = None
        self._thread = None
        self._running = False
        
        # Status
        self.connection_status = "disconnected"
        
        # Logging
        self.logger = logging.getLogger(f"WirelessAdapter[{esp32_ip}]")
        
    def start(self):
        """Adapter starten (startet WebSocket-Verbindung)"""
        if self._running:
            return
            
        self._running = True
        self._thread = Thread(target=self._run_async_loop, daemon=True)
        self._thread.start()
        self.logger.info("Wireless Weight Adapter gestartet")
    
    def stop(self):
        """Adapter stoppen"""
        self._running = False
        if self._loop:
            asyncio.run_coroutine_threadsafe(self.wireless_manager.disconnect(), self._loop)
        if self._thread:
            self._thread.join(timeout=2)
        self.logger.info("Wireless Weight Adapter gestoppt")
    
    def _run_async_loop(self):
        """Async Event Loop in separatem Thread"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        try:
            # Observer weiterleiten
            self.wireless_manager.add_observer(self._forward_weight_data)
            
            # Verbindung starten
            self._loop.run_until_complete(self._connect_with_retry())
            
        except Exception as e:
            self.logger.error(f"Async Loop Fehler: {e}")
        finally:
            self._loop.close()
    
    async def _connect_with_retry(self):
        """Verbindung mit Retry-Logik"""
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                await self.wireless_manager.connect()
                self.connection_status = "connected"
                break
                
            except Exception as e:
                self.logger.warning(f"Verbindungsversuch {attempt+1}/{max_retries} fehlgeschlagen: {e}")
                self.connection_status = f"retry {attempt+1}/{max_retries}"
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    self.connection_status = "failed"
                    self.logger.error("Alle Verbindungsversuche fehlgeschlagen")
    
    def _forward_weight_data(self, total_weight: float, corner_weights: Optional[List[float]] = None):
        """Gewichtsdaten an registrierte Observer weiterleiten"""
        for observer in self.observers:
            try:
                observer(total_weight, corner_weights)
            except Exception as e:
                self.logger.error(f"Observer-Weiterleitungsfehler: {e}")
    
    # WeightManager-kompatible API
    def add_observer(self, callback: Callable[[float, Optional[List[float]]], None]):
        """Observer registrieren (WeightManager-kompatibel)"""
        self.observers.append(callback)
        self.logger.debug(f"Observer registriert: {callback.__name__}")
        
    def remove_observer(self, callback: Callable[[float, Optional[List[float]]], None]):
        """Observer entfernen (WeightManager-kompatibel)"""
        if callback in self.observers:
            self.observers.remove(callback)
            self.logger.debug(f"Observer entfernt: {callback.__name__}")
    
    def read_weight(self) -> float:
        """Aktuelles Gesamtgewicht lesen (WeightManager-kompatibel)"""
        return self.wireless_manager.last_weight
    
    def read_corner_weights(self) -> Optional[List[float]]:
        """Eckgewichte lesen (WeightManager-kompatibel)"""
        return self.wireless_manager.last_corners
    
    def tare(self):
        """Waage nullen (WeightManager-kompatibel)"""
        if self._loop and self._running:
            future = asyncio.run_coroutine_threadsafe(
                self.wireless_manager.send_tare(), 
                self._loop
            )
            try:
                result = future.result(timeout=5)
                self.logger.info(f"Tare-Kommando: {result}")
                return result
            except Exception as e:
                self.logger.error(f"Tare fehlgeschlagen: {e}")
                return None
    
    def calibrate(self, weight: float):
        """Kalibrierung (WeightManager-kompatibel)"""
        if self._loop and self._running:
            future = asyncio.run_coroutine_threadsafe(
                self.wireless_manager.send_calibrate(weight), 
                self._loop
            )
            try:
                result = future.result(timeout=10)
                self.logger.info(f"Kalibrierung ({weight}kg): {result}")
                return result
            except Exception as e:
                self.logger.error(f"Kalibrierung fehlgeschlagen: {e}")
                return None
    
    @property
    def is_connected(self) -> bool:
        """Verbindungsstatus (WeightManager-kompatibel)"""
        return self.wireless_manager.is_connected
    
    def get_connection_status(self) -> dict:
        """Detaillierte Verbindungsinfo"""
        return {
            'connected': self.is_connected,
            'status': self.connection_status,
            'esp32_ip': self.esp32_ip,
            'last_weight': self.read_weight(),
            'battery_voltage': self.wireless_manager.battery_voltage,
            'wifi_rssi': self.wireless_manager.wifi_rssi
        }