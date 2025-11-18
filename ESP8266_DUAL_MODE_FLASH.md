# 🔥 ESP8266 Dual-Mode Flash - Schnellanleitung

## 🎯 **Firmware Flash auf ESP8266**

### **1. Hardware vorbereiten**
```bash
📱 ESP8266 NodeMCU per USB verbinden
🔌 Stromversorgung: Step-Down-Converter (5V → 3.3V)
⚖️  HX711 + Wägezellen angeschlossen (optional für Test)
```

### **2. Arduino IDE öffnen**
```bash
cd /home/daniel/Dokumente/HOF/Futterwagen/Python/Futterkarre/wireless/esp8266/futterkarre_wireless_waage_esp8266/

# Arduino IDE mit Dual-Mode Firmware starten:
arduino futterkarre_wireless_waage_esp8266.ino
```

### **3. Board konfigurieren**
```
Tools → Board: "NodeMCU 1.0 (ESP-12E Module)"
Tools → Port: /dev/ttyUSB0 (oder /dev/ttyACM0)
Tools → Upload Speed: 115200
Tools → CPU Frequency: 80 MHz  
Tools → Flash Size: "4MB (FS:2MB OTA:~1019KB)"
```

### **4. Firmware-Update validieren**
**Vor dem Flash prüfen - wichtige Zeilen im Code:**

#### **setupWiFi() Funktion (Zeile ~206):**
```cpp
void setupWiFi() {
  Serial.println("🔧 setupWiFi() - Dual-Mode (AP+STA)");
  
  // DUAL-MODE aktiviert (AP + Station gleichzeitig)
  WiFi.mode(WIFI_AP_STA);
  
  // Access Point starten (Futterkarre_WiFi)
  WiFi.softAP(AP_SSID, AP_PASSWORD);
  Serial.println("📡 Access Point 'Futterkarre_WiFi' gestartet: " + WiFi.softAPIP().toString());
  
  // Station-Mode zu Heimnetz
  WiFi.begin(HOME_WIFI_SSID, HOME_WIFI_PASSWORD);
  Serial.println("📱 Station-Mode zu 'IBIMSNOCH1MAL' verbinden...");
```

#### **HTTP Status API (Zeile ~279):**
```cpp
// Dual-Mode IP Adressen (AP + Station)
statusDoc["ap_ip"] = WiFi.softAPIP().toString();        // Futterkarre_WiFi (192.168.4.1)
statusDoc["station_ip"] = WiFi.localIP().toString();    // Heimnetz (192.168.2.x)
statusDoc["ip_address"] = WiFi.localIP().toString();    // Backwards compatibility
```

#### **WiFi Credentials (Zeilen 30-35):**
```cpp
// HOME NETWORK (Station Mode)
const char* HOME_WIFI_SSID = "IBIMSNOCH1MAL";
const char* HOME_WIFI_PASSWORD = "G8pY4B8K56vF";

// ACCESS POINT (für autonomen Betrieb)
const char* AP_SSID = "Futterkarre_WiFi";
const char* AP_PASSWORD = "12345678";
```

### **5. Flash ausführen**
```
1. Sketch → Überprüfen/Kompilieren ✅
2. ESP8266 Reset-Button drücken  
3. Sketch → Hochladen 🚀
4. Warten auf "Hochladen abgeschlossen"
```

### **6. Flash-Erfolg validieren**

#### **Serial Monitor (115200 Baud):**
```
=================================
🚀 Futterkarre Wireless Waage
   ESP8266 NodeMCU Dual-Mode
=================================
🔧 setupWiFi() - Dual-Mode (AP+STA)
📡 Access Point 'Futterkarre_WiFi' gestartet: 192.168.4.1
📱 Station-Mode zu 'IBIMSNOCH1MAL' verbinden...
✅ Station verbunden: 192.168.2.17
📊 Dual-Mode WiFi erfolgreich!
🔌 HTTP Server gestartet auf beiden IPs
🌐 WebSocket Server gestartet (Port 81)
✅ System bereit - Dual Mode aktiv!
```

#### **Network Test:**
```bash
# Test Access Point IP:
ping 192.168.4.1
curl http://192.168.4.1/status

# Test Station IP (wenn Heimnetz verfügbar):
ping 192.168.2.17
curl http://192.168.2.17/status
```

### **7. Dual-Mode Status prüfen**
```json
# HTTP Response sollte enthalten:
{
  "device_name": "Futterkarre_Waage",
  "wifi_connected": true,
  "ap_ip": "192.168.4.1",
  "station_ip": "192.168.2.17",
  "ssid": "IBIMSNOCH1MAL",
  "signal_strength": -45
}
```

## 🚨 **Troubleshooting**

### **Flash-Fehler:**
```bash
❌ Upload failed / Timeout
→ ESP8266 Reset-Button während Upload drücken
→ Richtigen Port wählen (/dev/ttyUSB0)
→ USB-Kabel/Verbindung prüfen

❌ Kompilierungs-Fehler
→ ESP8266 Board-Support installiert?
→ Libraries: HX711, ArduinoJson, WebSockets
```

### **WiFi-Probleme:**
```bash
❌ Station-Mode verbindet nicht
→ SSID/Password korrekt: "IBIMSNOCH1MAL" / "G8pY4B8K56vF"  
→ 2.4GHz WiFi (nicht 5GHz!)
→ WiFi-Router erreichbar?

❌ Access Point startet nicht
→ ESP8266 Power ausreichend (Step-Down-Converter)?
→ Kanal-Konflikte mit anderen APs?
```

## ✅ **Erfolgreiche Installation**

**ESP8266 ist bereit wenn:**
- ✅ Flash ohne Fehler (~315KB verwendet)
- ✅ Serial Monitor zeigt "Dual Mode aktiv!"  
- ✅ Ping zu 192.168.4.1 erfolgreich
- ✅ Ping zu 192.168.2.17 erfolgreich (bei Heimnetz)
- ✅ HTTP API antwortet auf beiden IPs
- ✅ JSON Response enthält ap_ip + station_ip

## 🎯 **Nach erfolgreichem Flash:**

1. **Pi5 vorbereiten:** `./deploy_pi5_dual_mode.sh`
2. **GUI starten:** `python main.py`
3. **ESP8266 Config-Seite öffnen**
4. **Dual-Mode Tests durchführen**

**🚀 ESP8266 Dual-Mode WiFi ist einsatzbereit!**