# ESP32-S3 Wireless Waage für Futterkarre

## 🚀 Übersicht

Komplettes Wireless-Waage-System bestehend aus:
- **ESP32-S3** Hardware-Unit (4x HX711 + Wägezellen)  
- **Python WebSocket-Client** für Pi5-Integration
- **Futterkarre-Software-Integration** (Plug & Play)

## 📦 Hardware-Liste

### ESP32-S3 Waage-Unit:
```
├── ESP32-S3 DevKit-C-1 N16R8 (~15€)
├── 4x HX711 24-Bit ADC Module (~20€)  
├── 4x 50kg Wägezellen (~60€)
├── 18650 Akku + TP4056 Lademodul (~10€)
├── Wasserdichtes Gehäuse + Status-LEDs (~15€)
└── Gesamt: ~120€
```

### Pi5-Unit (bereits vorhanden):
```
├── Raspberry Pi 5 + Touchscreen
├── WiFi-Verbindung zu ESP32
└── Futterkarre-Software
```

## ⚡ Features

### ESP32-Firmware (`futterkarre_wireless_waage.ino`):
- ✅ **4x HX711** simultane Gewichtsmessung
- ✅ **WiFi WebSocket-Server** (Port 81)
- ✅ **JSON-Protokoll** für Kommunikation  
- ✅ **Kalibrierung & Tare** per Remote-Kommando
- ✅ **Akku-Monitoring** mit Low-Battery-Warnung
- ✅ **Deep Sleep** für Stromsparmodus
- ✅ **Status-LEDs** (Power/WiFi/Error)
- ✅ **OTA-Updates** möglich
- ✅ **Persistente Kalibrierung** (Flash-Speicher)

### Python-Integration (`wireless_weight_manager.py`):
- ✅ **WebSocket-Client** für ESP32-Verbindung
- ✅ **Echtzeit-Gewichtsdaten** (2Hz Updates)
- ✅ **Observer-Pattern** für UI-Updates  
- ✅ **Auto-Reconnect** mit Exponential-Backoff
- ✅ **Kompatibilitäts-Adapter** für bestehende WeightManager-API
- ✅ **Verbindungs-Monitoring** + Status-Display
- ✅ **Kalibrierungs-Interface** (Tare, Gewichts-Kalibrierung)

## 🔧 Installation & Setup

### 1. ESP32-Firmware flashen:
```arduino
// Arduino IDE oder PlatformIO
// Libraries: WiFi, WebSocketsServer, ArduinoJson, HX711
// Board: ESP32-S3 Dev Module
// Datei: wireless/esp32/futterkarre_wireless_waage.ino
```

### 2. Python-Dependencies:
```bash
pip install websockets asyncio
```

### 3. Futterkarre-Integration:
```python
# In hardware/sensor_manager.py
from wireless.wireless_weight_manager import WirelessWeightManagerAdapter

# ESP8266-IP konfigurieren (z.B. 192.168.1.100)
weight_manager = WirelessWeightManagerAdapter("192.168.1.100")
```

### 🔄 ESP8266 Alternative (empfohlen für 2m):
```
ESP8266 NodeMCU v3 statt ESP32-S3:
✅ 60% günstiger (~5€ vs ~15€)
✅ 50% weniger Stromverbrauch  
✅ Einfachere Programmierung
✅ Gleiche WiFi-Performance bei 2m
→ Siehe: wireless/esp8266/ für ESP8266-Version
```

## 📡 Kommunikations-Protokoll

### WebSocket Messages (JSON):

#### Gewichtsdaten (ESP32 → Pi5):
```json
{
  "type": "weight_data",
  "timestamp": 1699123456789,
  "total_kg": 45.67,
  "corners": [11.2, 11.4, 11.6, 11.47],
  "battery_v": 3.8,
  "wifi_rssi": -45
}
```

#### Kommandos (Pi5 → ESP32):
```json
// Waage nullen
{
  "command": "tare"
}

// Kalibrierung (10kg Gewicht auflegen)
{
  "command": "calibrate", 
  "weight": 10.0
}

// Status abfragen
{
  "command": "get_status"
}

// Deep Sleep aktivieren
{
  "command": "deep_sleep"
}
```

#### Antworten (ESP32 → Pi5):
```json
{
  "type": "response",
  "command": "calibrate",
  "status": "success",
  "message": "Kalibrierung abgeschlossen"
}
```

## 🔌 Hardware-Verkabelung

### ESP32-S3 Pin-Mapping:
```
HX711_1 (Ecke vorne-links):  CLK=GPIO1,  DT=GPIO2
HX711_2 (Ecke vorne-rechts): CLK=GPIO3,  DT=GPIO4  
HX711_3 (Ecke hinten-links): CLK=GPIO5,  DT=GPIO6
HX711_4 (Ecke hinten-rechts):CLK=GPIO7,  DT=GPIO8

Status-LEDs:
├── Power (grün): GPIO9
├── WiFi (blau):  GPIO10
└── Error (rot):  GPIO11

Akku-Monitor: GPIO A0 (Spannungsteiler)
```

### Stromversorgung:
```
18650 Akku (3.7V, 3000mAh)
├── TP4056 USB-C Lademodul
├── 3.3V für ESP32-S3
├── 5V für HX711 (via Boost-Converter)
└── ~30h Laufzeit bei 2Hz Messungen
```

## 🌐 WiFi-Konfiguration

### ESP32-Einstellungen:
```cpp
const char* WIFI_SSID = "Futterkarre_WiFi";
const char* WIFI_PASSWORD = "FutterWaage2025";
const char* DEVICE_NAME = "FutterWaage_ESP32";
```

### Netzwerk-Setup:
1. **Option A:** Pi5 als WiFi-Hotspot
2. **Option B:** Gemeinsames WLAN-Netzwerk  
3. **Option C:** Dedicated 2.4GHz-Router

## 🔋 Power-Management

### Akku-Überwachung:
- **Normal:** >3.6V (LED grün)
- **Warnung:** 3.4-3.6V (LED blinkt)  
- **Kritisch:** <3.4V (Auto Deep-Sleep)

### Deep-Sleep-Modi:
- **Timer:** 1 Stunde Schlaf, dann 5min aktiv
- **Remote:** Per Pi5-Kommando aktivierbar
- **Battery:** Auto-Aktivierung bei niedrigem Akku

## 🚀 Vorteile vs. Kabel-Lösung

| Aspekt | Wireless | Kabel |
|--------|----------|-------|
| **Mobilität** | ✅ Vollständig flexibel | ❌ Kabellänge begrenzt |
| **Installation** | ✅ Einfach, keine Verkabelung | ❌ 16 Kabel + Stecker |
| **Wartung** | ✅ Aufladen per USB-C | ✅ Keine Akkus |
| **Reichweite** | ✅ 50-100m WiFi | ❌ Maximal 10-20m |
| **Störanfälligkeit** | ⚠️ WiFi-abhängig | ✅ Direkte Verbindung |
| **Kosten** | ⚠️ +50€ für ESP32+Akku | ✅ Nur HX711+Kabel |

## 📊 Performance

- **Update-Rate:** 2Hz (500ms Intervall)
- **Latenz:** <50ms (WiFi + Processing)
- **Genauigkeit:** 24-Bit ADC = ~0.01kg bei 100kg
- **Akku-Laufzeit:** ~30h bei kontinuierlicher Nutzung  
- **WiFi-Reichweite:** 50-100m (abhängig von Umgebung)

## 🛠️ Entwicklung & Debug

### ESP32-Debug:
```cpp
Serial.begin(115200);  // USB-Serial-Monitor
```

### Pi5-Debug:
```python
# Logging aktivieren
logging.getLogger("wireless").setLevel(logging.DEBUG)

# Verbindungs-Status
status = manager.get_connection_status()
print(f"ESP32: {status}")
```

### WebSocket-Test:
```bash
# Browser-Console oder wscat
wscat -c ws://192.168.1.100:81
{"command": "get_status"}
```

## 🎯 Integration in Futterkarre

Die Wireless-Waage ist **Plug & Play** kompatibel:

```python
# Einfacher Austausch in sensor_manager.py:

# Alt (HX711 direkt):
from hardware.weight_manager import WeightManager  
weight_manager = WeightManager()

# Neu (Wireless):
from wireless.wireless_weight_manager import WirelessWeightManagerAdapter
weight_manager = WirelessWeightManagerAdapter("192.168.1.100")

# Alle bestehenden Funktionen funktionieren weiter:
weight = weight_manager.read_weight()  # ✅
weight_manager.tare()                  # ✅  
weight_manager.add_observer(callback)  # ✅
```

## 🚀 Deployment

1. **ESP32-Hardware** bauen + flashen
2. **Waage** mechanisch installieren  
3. **WiFi-Netzwerk** einrichten
4. **Python-Code** in Futterkarre aktivieren
5. **Kalibrierung** durchführen
6. **Fertig!** 🎉

---

**Die Wireless-Lösung macht die Futterkarre zur modernsten mobilen Waage!** 📡⚖️🚀