/*
 * ESP32-S3 Wireless Waage für Futterkarre
 * 
 * Hardware:
 * - ESP32-S3 DevKit-C-1 N16R8
 * - 4x HX711 + Wägezellen (Waage-Ecken)
 * - 18650 Akku + TP4056 Charging
 * - Status LEDs (Power/WiFi/Error)
 * 
 * Features:
 * - WiFi Kommunikation mit Pi5
 * - JSON WebSocket Protokoll  
 * - 4-Punkt Gewichtsmessung
 * - Akku-Monitoring
 * - Deep Sleep Power-Management
 * - OTA Updates
 * 
 * Author: Futterkarre Team
 * Version: 1.0
 */

#include <WiFi.h>
#include <WebSocketsServer.h>
#include <ArduinoJson.h>
#include <HX711.h>
#include <Preferences.h>
#include <esp_sleep.h>

// =================== HARDWARE KONFIGURATION ===================

// HX711 Pin-Mapping (4 Wägezellen-Ecken)
#define HX711_1_CLK  1   // Ecke vorne-links
#define HX711_1_DT   2
#define HX711_2_CLK  3   // Ecke vorne-rechts  
#define HX711_2_DT   4
#define HX711_3_CLK  5   // Ecke hinten-links
#define HX711_3_DT   6
#define HX711_4_CLK  7   // Ecke hinten-rechts
#define HX711_4_DT   8

// Status LEDs
#define LED_POWER    9   // Grün - System läuft
#define LED_WIFI     10  // Blau - WiFi verbunden
#define LED_ERROR    11  // Rot - Fehler aufgetreten

// Akku-Monitor (Spannungsteiler)
#define BATTERY_PIN  A0
#define BATTERY_FACTOR 2.0  // Spannungsteiler 1:1

// =================== SYSTEM KONFIGURATION ===================

// WiFi Einstellungen (Futterkarre-Netzwerk)
const char* WIFI_SSID = "Futterkarre_WiFi";
const char* WIFI_PASSWORD = "FutterWaage2025";
const char* DEVICE_NAME = "FutterWaage_ESP32";

// WebSocket Server (Port 81)
WebSocketsServer webSocket = WebSocketsServer(81);

// HX711 Instanzen
HX711 scale_1;  // Vorne-Links
HX711 scale_2;  // Vorne-Rechts  
HX711 scale_3;  // Hinten-Links
HX711 scale_4;  // Hinten-Rechts

// Preferences für Kalibrierung
Preferences preferences;

// =================== SYSTEM VARIABLEN ===================

struct WeightData {
  float corner_1;     // kg
  float corner_2;     // kg
  float corner_3;     // kg  
  float corner_4;     // kg
  float total;        // kg
  float battery;      // V
  unsigned long timestamp;
};

struct CalibrationData {
  float scale_1_factor = 1000.0;  // Default-Werte
  float scale_2_factor = 1000.0;
  float scale_3_factor = 1000.0;
  float scale_4_factor = 1000.0;
  long scale_1_offset = 0;
  long scale_2_offset = 0;
  long scale_3_offset = 0;
  long scale_4_offset = 0;
};

WeightData currentWeight;
CalibrationData calibration;
bool wifiConnected = false;
bool systemReady = false;
unsigned long lastMeasurement = 0;
const unsigned long MEASUREMENT_INTERVAL = 500; // 500ms = 2Hz

// =================== SETUP ===================

void setup() {
  Serial.begin(115200);
  Serial.println("🚀 ESP32-S3 Futterkarre Wireless-Waage Start...");
  
  // Hardware initialisieren
  initializePins();
  initializeHX711();
  loadCalibration();
  
  // WiFi starten
  initializeWiFi();
  
  // WebSocket Server starten
  initializeWebSocket();
  
  systemReady = true;
  digitalWrite(LED_POWER, HIGH);
  
  Serial.println("✅ System bereit - Wireless-Waage aktiv!");
}

// =================== MAIN LOOP ===================

void loop() {
  // WebSocket Events verarbeiten
  webSocket.loop();
  
  // Periodische Gewichtsmessung
  if (millis() - lastMeasurement >= MEASUREMENT_INTERVAL) {
    measureWeight();
    sendWeightData();
    lastMeasurement = millis();
  }
  
  // WiFi-Status überwachen
  monitorWiFi();
  
  // Akku-Monitoring
  monitorBattery();
  
  // Power-Management (bei niedrigem Akku)
  checkPowerManagement();
  
  delay(10);  // CPU entlasten
}

// =================== HARDWARE INITIALISIERUNG ===================

void initializePins() {
  // Status LEDs
  pinMode(LED_POWER, OUTPUT);
  pinMode(LED_WIFI, OUTPUT);
  pinMode(LED_ERROR, OUTPUT);
  
  // Initial: Alle LEDs aus
  digitalWrite(LED_POWER, LOW);
  digitalWrite(LED_WIFI, LOW);
  digitalWrite(LED_ERROR, LOW);
  
  // Akku-Pin
  pinMode(BATTERY_PIN, INPUT);
  
  Serial.println("📌 GPIO-Pins initialisiert");
}

void initializeHX711() {
  Serial.println("⚖️ HX711 Sensoren initialisieren...");
  
  // HX711 initialisieren
  scale_1.begin(HX711_1_DT, HX711_1_CLK);
  scale_2.begin(HX711_2_DT, HX711_2_CLK);
  scale_3.begin(HX711_3_DT, HX711_3_CLK);
  scale_4.begin(HX711_4_DT, HX711_4_CLK);
  
  // Bereit-Check
  if (scale_1.is_ready() && scale_2.is_ready() && 
      scale_3.is_ready() && scale_4.is_ready()) {
    Serial.println("✅ Alle 4 HX711 Sensoren bereit");
  } else {
    Serial.println("❌ HX711 Sensoren-Problem");
    digitalWrite(LED_ERROR, HIGH);
  }
}

// =================== WIFI & WEBSOCKET ===================

void initializeWiFi() {
  Serial.println("📡 WiFi-Verbindung starten...");
  
  WiFi.mode(WIFI_STA);
  WiFi.setHostname(DEVICE_NAME);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
    
    // LED-Blinken während Verbindung
    digitalWrite(LED_WIFI, !digitalRead(LED_WIFI));
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    digitalWrite(LED_WIFI, HIGH);
    
    Serial.println();
    Serial.printf("✅ WiFi verbunden: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("📶 Signal: %d dBm\n", WiFi.RSSI());
  } else {
    Serial.println("❌ WiFi-Verbindung fehlgeschlagen");
    digitalWrite(LED_ERROR, HIGH);
  }
}

void initializeWebSocket() {
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
  
  Serial.printf("🔗 WebSocket-Server gestartet auf Port 81\n");
  Serial.printf("URL: ws://%s:81/\n", WiFi.localIP().toString().c_str());
}

// =================== WEBSOCKET EVENT HANDLER ===================

void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.printf("👋 Client #%u getrennt\n", num);
      break;
      
    case WStype_CONNECTED: {
      IPAddress ip = webSocket.remoteIP(num);
      Serial.printf("🔗 Client #%u verbunden von %s\n", num, ip.toString().c_str());
      
      // Willkommens-Message senden
      sendWelcomeMessage(num);
      break;
    }
    
    case WStype_TEXT: {
      Serial.printf("📨 Nachricht von #%u: %s\n", num, payload);
      handleWebSocketMessage(num, (char*)payload);
      break;
    }
    
    default:
      break;
  }
}

void handleWebSocketMessage(uint8_t clientNum, String message) {
  // JSON-Message parsen
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, message);
  
  if (error) {
    Serial.printf("❌ JSON-Parse-Fehler: %s\n", error.c_str());
    return;
  }
  
  String command = doc["command"];
  
  // Kommandos verarbeiten
  if (command == "tare") {
    performTare();
    sendResponse(clientNum, "tare", "success", "Waage genullt");
    
  } else if (command == "calibrate") {
    float knownWeight = doc["weight"];
    performCalibration(knownWeight);
    sendResponse(clientNum, "calibrate", "success", "Kalibrierung abgeschlossen");
    
  } else if (command == "get_status") {
    sendStatusData(clientNum);
    
  } else if (command == "deep_sleep") {
    sendResponse(clientNum, "deep_sleep", "success", "Gehe in Deep Sleep...");
    delay(100);  // Message senden lassen
    enterDeepSleep();
    
  } else {
    sendResponse(clientNum, command, "error", "Unbekanntes Kommando");
  }
}

// =================== GEWICHTSMESSUNG ===================

void measureWeight() {
  if (!systemReady) return;
  
  // Alle 4 Ecken messen
  if (scale_1.is_ready()) currentWeight.corner_1 = scale_1.get_units(3);
  if (scale_2.is_ready()) currentWeight.corner_2 = scale_2.get_units(3);
  if (scale_3.is_ready()) currentWeight.corner_3 = scale_3.get_units(3);
  if (scale_4.is_ready()) currentWeight.corner_4 = scale_4.get_units(3);
  
  // Gesamt-Gewicht berechnen
  currentWeight.total = currentWeight.corner_1 + currentWeight.corner_2 + 
                       currentWeight.corner_3 + currentWeight.corner_4;
  
  // Akku-Spannung messen
  currentWeight.battery = readBatteryVoltage();
  
  // Timestamp setzen
  currentWeight.timestamp = millis();
}

void sendWeightData() {
  if (!wifiConnected) return;
  
  // JSON-Message erstellen
  StaticJsonDocument<300> doc;
  doc["type"] = "weight_data";
  doc["timestamp"] = currentWeight.timestamp;
  doc["total_kg"] = round(currentWeight.total * 100) / 100.0;  // 2 Dezimalstellen
  
  JsonArray corners = doc.createNestedArray("corners");
  corners.add(round(currentWeight.corner_1 * 100) / 100.0);
  corners.add(round(currentWeight.corner_2 * 100) / 100.0);
  corners.add(round(currentWeight.corner_3 * 100) / 100.0);
  corners.add(round(currentWeight.corner_4 * 100) / 100.0);
  
  doc["battery_v"] = round(currentWeight.battery * 100) / 100.0;
  doc["wifi_rssi"] = WiFi.RSSI();
  
  // An alle Clients senden
  String jsonString;
  serializeJson(doc, jsonString);
  webSocket.broadcastTXT(jsonString);
}

// =================== KALIBRIERUNG ===================

void performTare() {
  Serial.println("🎯 Waage wird genullt (Tare)...");
  
  scale_1.tare();
  scale_2.tare();
  scale_3.tare();
  scale_4.tare();
  
  // Neue Offsets speichern
  calibration.scale_1_offset = scale_1.get_offset();
  calibration.scale_2_offset = scale_2.get_offset();
  calibration.scale_3_offset = scale_3.get_offset();
  calibration.scale_4_offset = scale_4.get_offset();
  
  saveCalibration();
  
  Serial.println("✅ Tare abgeschlossen - Waage genullt");
}

void performCalibration(float knownWeight) {
  Serial.printf("📏 Kalibrierung mit %0.2f kg...\n", knownWeight);
  
  // Mehrere Messungen für Genauigkeit
  long raw_1 = scale_1.get_value(10);
  long raw_2 = scale_2.get_value(10);
  long raw_3 = scale_3.get_value(10);
  long raw_4 = scale_4.get_value(10);
  
  // Neue Kalibrierungs-Faktoren berechnen
  // Annahme: Gewicht gleichmäßig auf alle 4 Ecken verteilt
  float weightPerCorner = knownWeight / 4.0;
  
  if (raw_1 != 0) calibration.scale_1_factor = raw_1 / weightPerCorner;
  if (raw_2 != 0) calibration.scale_2_factor = raw_2 / weightPerCorner;
  if (raw_3 != 0) calibration.scale_3_factor = raw_3 / weightPerCorner;
  if (raw_4 != 0) calibration.scale_4_factor = raw_4 / weightPerCorner;
  
  // Neue Faktoren anwenden
  scale_1.set_scale(calibration.scale_1_factor);
  scale_2.set_scale(calibration.scale_2_factor);
  scale_3.set_scale(calibration.scale_3_factor);
  scale_4.set_scale(calibration.scale_4_factor);
  
  saveCalibration();
  
  Serial.println("✅ Kalibrierung abgeschlossen");
}

void loadCalibration() {
  preferences.begin("futterkarre", false);
  
  calibration.scale_1_factor = preferences.getFloat("scale_1_f", 1000.0);
  calibration.scale_2_factor = preferences.getFloat("scale_2_f", 1000.0);
  calibration.scale_3_factor = preferences.getFloat("scale_3_f", 1000.0);
  calibration.scale_4_factor = preferences.getFloat("scale_4_f", 1000.0);
  
  calibration.scale_1_offset = preferences.getLong("scale_1_o", 0);
  calibration.scale_2_offset = preferences.getLong("scale_2_o", 0);
  calibration.scale_3_offset = preferences.getLong("scale_3_o", 0);
  calibration.scale_4_offset = preferences.getLong("scale_4_o", 0);
  
  // Kalibrierung anwenden
  scale_1.set_scale(calibration.scale_1_factor);
  scale_2.set_scale(calibration.scale_2_factor);
  scale_3.set_scale(calibration.scale_3_factor);
  scale_4.set_scale(calibration.scale_4_factor);
  
  scale_1.set_offset(calibration.scale_1_offset);
  scale_2.set_offset(calibration.scale_2_offset);
  scale_3.set_offset(calibration.scale_3_offset);
  scale_4.set_offset(calibration.scale_4_offset);
  
  preferences.end();
  
  Serial.println("📋 Kalibrierung geladen");
}

void saveCalibration() {
  preferences.begin("futterkarre", false);
  
  preferences.putFloat("scale_1_f", calibration.scale_1_factor);
  preferences.putFloat("scale_2_f", calibration.scale_2_factor);
  preferences.putFloat("scale_3_f", calibration.scale_3_factor);
  preferences.putFloat("scale_4_f", calibration.scale_4_factor);
  
  preferences.putLong("scale_1_o", calibration.scale_1_offset);
  preferences.putLong("scale_2_o", calibration.scale_2_offset);
  preferences.putLong("scale_3_o", calibration.scale_3_offset);
  preferences.putLong("scale_4_o", calibration.scale_4_offset);
  
  preferences.end();
  
  Serial.println("💾 Kalibrierung gespeichert");
}

// =================== UTILITY FUNKTIONEN ===================

float readBatteryVoltage() {
  int rawValue = analogRead(BATTERY_PIN);
  float voltage = (rawValue / 4095.0) * 3.3 * BATTERY_FACTOR;
  return voltage;
}

void monitorWiFi() {
  if (WiFi.status() != WL_CONNECTED && wifiConnected) {
    wifiConnected = false;
    digitalWrite(LED_WIFI, LOW);
    digitalWrite(LED_ERROR, HIGH);
    Serial.println("❌ WiFi-Verbindung verloren");
    
    // Neuverbindung versuchen
    WiFi.reconnect();
  }
  
  if (WiFi.status() == WL_CONNECTED && !wifiConnected) {
    wifiConnected = true;
    digitalWrite(LED_WIFI, HIGH);
    digitalWrite(LED_ERROR, LOW);
    Serial.println("✅ WiFi wiederverbunden");
  }
}

void monitorBattery() {
  float voltage = readBatteryVoltage();
  
  // Niedrige Akku-Warnung (< 3.4V = ~20%)
  if (voltage < 3.4 && voltage > 2.0) {  // > 2.0 um Messfehler zu vermeiden
    // LED-Blinken bei niedrigem Akku
    static unsigned long lastBlink = 0;
    if (millis() - lastBlink > 1000) {
      digitalWrite(LED_ERROR, !digitalRead(LED_ERROR));
      lastBlink = millis();
    }
  }
}

void checkPowerManagement() {
  float voltage = readBatteryVoltage();
  
  // Kritischer Akku-Stand (< 3.2V = ~5%)
  if (voltage < 3.2 && voltage > 2.0) {
    Serial.println("🔋 Kritischer Akku-Stand - Deep Sleep aktiviert");
    
    // Warnung an Pi5 senden
    StaticJsonDocument<100> doc;
    doc["type"] = "battery_critical";
    doc["voltage"] = voltage;
    doc["message"] = "ESP32 geht in Deep Sleep wegen niedrigem Akku";
    
    String jsonString;
    serializeJson(doc, jsonString);
    webSocket.broadcastTXT(jsonString);
    
    delay(1000);  // Message senden lassen
    enterDeepSleep();
  }
}

void enterDeepSleep() {
  Serial.println("😴 Deep Sleep Mode aktiviert...");
  
  // Alle LEDs aus
  digitalWrite(LED_POWER, LOW);
  digitalWrite(LED_WIFI, LOW);
  digitalWrite(LED_ERROR, LOW);
  
  // WiFi ausschalten
  WiFi.disconnect();
  WiFi.mode(WIFI_OFF);
  
  // Deep Sleep für 1 Stunde oder bis Wake-Up
  esp_sleep_enable_timer_wakeup(60 * 60 * 1000000ULL);  // 1 Stunde in µs
  esp_deep_sleep_start();
}

// =================== WEBSOCKET HELPER ===================

void sendWelcomeMessage(uint8_t clientNum) {
  StaticJsonDocument<200> doc;
  doc["type"] = "welcome";
  doc["device"] = DEVICE_NAME;
  doc["version"] = "1.0";
  doc["features"] = "4x HX711, WiFi, Battery, Deep Sleep";
  
  String jsonString;
  serializeJson(doc, jsonString);
  webSocket.sendTXT(clientNum, jsonString);
}

void sendResponse(uint8_t clientNum, String command, String status, String message) {
  StaticJsonDocument<150> doc;
  doc["type"] = "response";
  doc["command"] = command;
  doc["status"] = status;
  doc["message"] = message;
  doc["timestamp"] = millis();
  
  String jsonString;
  serializeJson(doc, jsonString);
  webSocket.sendTXT(clientNum, jsonString);
}

void sendStatusData(uint8_t clientNum) {
  StaticJsonDocument<300> doc;
  doc["type"] = "status";
  doc["uptime_ms"] = millis();
  doc["wifi_connected"] = wifiConnected;
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["battery_voltage"] = readBatteryVoltage();
  doc["free_heap"] = ESP.getFreeHeap();
  doc["chip_model"] = ESP.getChipModel();
  
  JsonArray sensors = doc.createNestedArray("hx711_ready");
  sensors.add(scale_1.is_ready());
  sensors.add(scale_2.is_ready());
  sensors.add(scale_3.is_ready());
  sensors.add(scale_4.is_ready());
  
  String jsonString;
  serializeJson(doc, jsonString);
  webSocket.sendTXT(clientNum, jsonString);
}

// =================== ENDE ===================