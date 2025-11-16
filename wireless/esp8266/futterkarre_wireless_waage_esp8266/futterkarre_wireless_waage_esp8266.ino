/*
 * ESP8266 Futterkarre Wireless Waage
 * 
 * Hardware: ESP8266 NodeMCU v3 + 4x HX711 + 4x Wägezellen
 * Funktion: WiFi WebSocket-Server für Gewichtsmessung
 * 
 * Features:
 * - 4x HX711 24-Bit ADC simultane Messung
 * - WiFi WebSocket-Server (Port 81)
 * - JSON-Kommunikationsprotokoll
 * - Tare & Kalibrierung per Remote-Kommando
 * - Akku-Monitoring (18650)
 * - Deep Sleep Power-Management
 * - Status-LEDs (Power/WiFi/Error)
 * 
 * Pin-Mapping ESP8266 NodeMCU (für verteilte HX711):
 * HX711_1 (vorne-links):  CLK=D1(GPIO5),  DT=D2(GPIO4)   [kurzes Kabel]
 * HX711_2 (vorne-rechts): CLK=D3(GPIO0),  DT=D4(GPIO2)   [kurzes Kabel]
 * HX711_3 (hinten-links): CLK=D5(GPIO14), DT=D6(GPIO12)  [1,5m Kabel]
 * HX711_4 (hinten-rechts):CLK=D7(GPIO13), DT=D8(GPIO15)  [1,5m Kabel]
 * 
 * Spannungsversorgung:
 * 18650 → LM2596 → 5V Rail → verteilte AMS1117 → 3.3V lokal
 * 
 * LEDs:
 * Power LED (grün):  D0 (GPIO16)
 * WiFi LED (blau):   Built-in LED (GPIO2) - bereits vorhanden
 * Error LED (rot):   wird über WiFi-LED simuliert (blinkt schnell)
 * 
 * Akku-Monitor: A0 (ADC, 3.3V max via Spannungsteiler)
 * 
 * Autor: Futterkarre-Team
 * Version: 1.0 ESP8266
 * Datum: 2025-11-09
 */

#include <ESP8266WiFi.h>
#include <WebSocketsServer.h>
#include <ArduinoJson.h>
#include <HX711.h>

// =================== KONFIGURATION ===================

// WiFi-Einstellungen - Hybrid-Modus
const char* HOME_WIFI_SSID = "IBIMSNOCH1MAL";        // Pi5 Heimnetz
const char* HOME_WIFI_PASSWORD = "G8pY4B8K56vF";     // Pi5 WiFi Passwort
const char* AP_SSID = "Futterkarre_WiFi";            // Eigenes Stall-Netz
const char* AP_PASSWORD = "FutterWaage2025";         // Stall-Netz Passwort
const char* DEVICE_NAME = "FutterWaage_ESP8266";

// WiFi-Modi - Verwende die ESP8266 Standard-Modi
int current_wifi_mode; // 0 = AP Mode, 1 = Station Mode

// WebSocket-Server
WebSocketsServer webSocket = WebSocketsServer(81);

// HX711 Pin-Definitionen (ESP8266 NodeMCU)
#define HX711_1_CLK  5   // D1
#define HX711_1_DT   4   // D2
#define HX711_2_CLK  0   // D3
#define HX711_2_DT   2   // D4  
#define HX711_3_CLK  14  // D5
#define HX711_3_DT   12  // D6
#define HX711_4_CLK  13  // D7
#define HX711_4_DT   15  // D8

// Status-LEDs
#define LED_POWER    16  // D0 - Power LED (grün)
#define LED_WIFI     2   // Built-in LED (blau, LOW = an)
#define LED_ERROR    2   // Gleiche wie WiFi, blinkt aber schnell

// Akku-Monitoring
#define BATTERY_PIN  A0  // ADC für Spannungsmessung
#define BATTERY_MIN  3.0 // Minimum Spannung (V)
#define BATTERY_MAX  4.2 // Maximum Spannung (V)

// HX711 Objekte erstellen
HX711 scale1, scale2, scale3, scale4;

// =================== GLOBALE VARIABLEN ===================

// Kalibrierungsfaktoren (werden in EEPROM gespeichert)
float calibration_factor_1 = 1000.0;
float calibration_factor_2 = 1000.0;
float calibration_factor_3 = 1000.0;
float calibration_factor_4 = 1000.0;

// Tare-Werte (Nullpunkt)
long tare_offset_1 = 0;
long tare_offset_2 = 0;
long tare_offset_3 = 0;
long tare_offset_4 = 0;

// Gewichtsdaten
float weight_1 = 0.0, weight_2 = 0.0, weight_3 = 0.0, weight_4 = 0.0;
float total_weight = 0.0;

// System-Status
bool wifi_connected = false;
bool scales_initialized = false;
float battery_voltage = 0.0;
int wifi_rssi = 0;
unsigned long last_measurement = 0;
unsigned long last_battery_check = 0;
unsigned long last_status_led = 0;

// Timing-Konstanten
const unsigned long MEASUREMENT_INTERVAL = 500;   // 2Hz Messungen
const unsigned long BATTERY_CHECK_INTERVAL = 5000; // 5s Akku-Check
const unsigned long STATUS_LED_INTERVAL = 1000;   // 1s LED-Blink

// Deep Sleep
const unsigned long DEEP_SLEEP_DURATION = 3600000000; // 1h in Mikrosekunden
bool deep_sleep_requested = false;

// =================== SETUP ===================

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println();
  Serial.println("=================================");
  Serial.println("🚀 Futterkarre Wireless Waage");
  Serial.println("   ESP8266 NodeMCU Version");
  Serial.println("=================================");
  
  // GPIO initialisieren
  setupGPIO();
  
  // HX711 Waagen initialisieren  
  setupScales();
  
  // WiFi verbinden
  setupWiFi();
  
  // WebSocket-Server starten
  setupWebSocket();
  
  // Bereit-Signal
  blinkLED(LED_POWER, 3, 200);
  Serial.println("✅ System bereit!");
  Serial.println();
}

void setupGPIO() {
  Serial.print("🔧 GPIO initialisieren... ");
  
  // LED-Pins als Output
  pinMode(LED_POWER, OUTPUT);
  pinMode(LED_WIFI, OUTPUT);
  
  // LEDs initial ausschalten
  digitalWrite(LED_POWER, HIGH);  // Power LED an
  digitalWrite(LED_WIFI, HIGH);   // WiFi LED aus (LOW = an bei built-in)
  
  Serial.println("OK");
}

void setupScales() {
  Serial.print("⚖️  HX711 Waagen initialisieren... ");
  
  // HX711 initialisieren
  scale1.begin(HX711_1_DT, HX711_1_CLK);
  scale2.begin(HX711_2_DT, HX711_2_CLK);
  scale3.begin(HX711_3_DT, HX711_3_CLK);
  scale4.begin(HX711_4_DT, HX711_4_CLK);
  
  // Warten bis Waagen bereit
  int timeout = 50; // 5s timeout
  while (!scale1.is_ready() || !scale2.is_ready() || 
         !scale3.is_ready() || !scale4.is_ready()) {
    if (--timeout <= 0) {
      Serial.println("❌ FEHLER - HX711 nicht bereit!");
      return;
    }
    delay(100);
  }
  
  // Kalibrierungsfaktoren laden (TODO: aus EEPROM)
  scale1.set_scale(calibration_factor_1);
  scale2.set_scale(calibration_factor_2);
  scale3.set_scale(calibration_factor_3);
  scale4.set_scale(calibration_factor_4);
  
  // Tare (Nullpunkt setzen)
  performTare();
  
  scales_initialized = true;
  Serial.println("OK");
}

void setupWiFi() {
  Serial.println("📡 WiFi Hybrid-Setup wird gestartet...");
  
  // Erst versuchen: Heimnetz verbinden
  Serial.print("🏠 Versuche Heimnetz-Verbindung... ");
  WiFi.mode(WIFI_STA);
  WiFi.hostname(DEVICE_NAME);
  WiFi.begin(HOME_WIFI_SSID, HOME_WIFI_PASSWORD);
  
  int timeout = 100; // 10s timeout für Heimnetz
  while (WiFi.status() != WL_CONNECTED && timeout-- > 0) {
    delay(100);
    Serial.print(".");
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    // Heimnetz erfolgreich
    current_wifi_mode = 1; // Station Mode
    wifi_connected = true;
    digitalWrite(LED_WIFI, LOW); // WiFi LED an
    
    Serial.println(" OK");
    Serial.printf("   Heimnetz-Modus aktiv\n");
    Serial.printf("   IP: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("   RSSI: %d dBm\n", WiFi.RSSI());
    wifi_rssi = WiFi.RSSI();
  } else {
    // Fallback: Access Point Modus (Stall)
    Serial.println(" Timeout");
    Serial.print("📡 Starte Access Point Modus... ");
    
    WiFi.mode(WIFI_AP);
    bool ap_started = WiFi.softAP(AP_SSID, AP_PASSWORD);
    
    if (ap_started) {
      current_wifi_mode = 0; // AP Mode
      wifi_connected = true;
      digitalWrite(LED_WIFI, LOW); // WiFi LED an
      
      Serial.println("OK");
      Serial.printf("   Stall-Modus aktiv\n");
      Serial.printf("   AP-SSID: %s\n", AP_SSID);
      Serial.printf("   AP-IP: %s\n", WiFi.softAPIP().toString().c_str());
    } else {
      Serial.println(" ❌ FEHLER");
      wifi_connected = false;
    }
  }
}

void setupWebSocket() {
  Serial.print("🔌 WebSocket-Server starten... ");
  
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
  
  Serial.printf("OK (Port 81)\n");
}

// =================== MAIN LOOP ===================

void loop() {
  unsigned long now = millis();
  
  // WebSocket-Server verarbeiten
  webSocket.loop();
  
  // WiFi-Verbindung prüfen
  checkWiFiConnection();
  
  // Gewichtsmessungen (2Hz)
  if (now - last_measurement >= MEASUREMENT_INTERVAL) {
    measureWeights();
    sendWeightData();
    last_measurement = now;
  }
  
  // Akku-Status prüfen (alle 5s)
  if (now - last_battery_check >= BATTERY_CHECK_INTERVAL) {
    checkBattery();
    last_battery_check = now;
  }
  
  // Status-LED blinken (1Hz)
  if (now - last_status_led >= STATUS_LED_INTERVAL) {
    updateStatusLED();
    last_status_led = now;
  }
  
  // Deep Sleep prüfen
  if (deep_sleep_requested) {
    enterDeepSleep();
  }
  
  // Kurze Pause für Stabilität
  delay(10);
}

// =================== WEBSOCKET HANDLER ===================

void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.printf("🔌 Client #%u getrennt\n", num);
      break;
      
    case WStype_CONNECTED: {
      IPAddress ip = webSocket.remoteIP(num);
      Serial.printf("🔌 Client #%u verbunden von %s\n", num, ip.toString().c_str());
      
      // Willkommens-Message senden
      sendStatusMessage(num);
      break;
    }
    
    case WStype_TEXT:
      Serial.printf("📨 Nachricht von #%u: %s\n", num, payload);
      processCommand(num, (char*)payload);
      break;
      
    default:
      break;
  }
}

void processCommand(uint8_t clientNum, const char* message) {
  // JSON parsen
  JsonDocument doc;
  DeserializationError error = deserializeJson(doc, message);
  
  if (error) {
    Serial.printf("❌ JSON-Fehler: %s\n", error.c_str());
    return;
  }
  
  String command = doc["command"].as<String>();
  
  // Kommando verarbeiten
  if (command == "tare") {
    handleTareCommand(clientNum);
  }
  else if (command == "calibrate") {
    float weight = doc["weight"].as<float>();
    handleCalibrateCommand(clientNum, weight);
  }
  else if (command == "get_status") {
    sendStatusMessage(clientNum);
  }
  else if (command == "deep_sleep") {
    handleDeepSleepCommand(clientNum);
  }
  else {
    Serial.printf("❓ Unbekanntes Kommando: %s\n", command.c_str());
  }
}

void handleTareCommand(uint8_t clientNum) {
  Serial.println("🔄 Tare-Kommando empfangen");
  
  bool success = performTare();
  
  // Antwort senden
  JsonDocument response;
  response["type"] = "response";
  response["command"] = "tare";
  response["status"] = success ? "success" : "error";
  response["message"] = success ? "Waage erfolgreich genullt" : "Tare fehlgeschlagen";
  
  String responseStr;
  serializeJson(response, responseStr);
  webSocket.sendTXT(clientNum, responseStr);
  
  Serial.printf("✅ Tare-Response gesendet: %s\n", success ? "OK" : "FEHLER");
}

void handleCalibrateCommand(uint8_t clientNum, float referenceWeight) {
  Serial.printf("🎯 Kalibrierung mit %.2f kg\n", referenceWeight);
  
  if (referenceWeight <= 0) {
    sendErrorResponse(clientNum, "calibrate", "Ungültiges Gewicht");
    return;
  }
  
  bool success = performCalibration(referenceWeight);
  
  // Antwort senden
  JsonDocument response;
  response["type"] = "response";
  response["command"] = "calibrate";
  response["status"] = success ? "success" : "error";
  response["message"] = success ? "Kalibrierung erfolgreich" : "Kalibrierung fehlgeschlagen";
  
  String responseStr;
  serializeJson(response, responseStr);
  webSocket.sendTXT(clientNum, responseStr);
  
  Serial.printf("✅ Kalibrierungs-Response: %s\n", success ? "OK" : "FEHLER");
}

void handleDeepSleepCommand(uint8_t clientNum) {
  Serial.println("😴 Deep Sleep angefordert");
  
  // Bestätigung senden
  JsonDocument response;
  response["type"] = "response";
  response["command"] = "deep_sleep";
  response["status"] = "success";
  response["message"] = "Deep Sleep wird aktiviert";
  
  String responseStr;
  serializeJson(response, responseStr);
  webSocket.sendTXT(clientNum, responseStr);
  
  delay(100); // Message senden lassen
  deep_sleep_requested = true;
}

void sendErrorResponse(uint8_t clientNum, const char* command, const char* error) {
  JsonDocument response;
  response["type"] = "response";
  response["command"] = command;
  response["status"] = "error";
  response["message"] = error;
  
  String responseStr;
  serializeJson(response, responseStr);
  webSocket.sendTXT(clientNum, responseStr);
}

// =================== GEWICHTSMESSUNG ===================

void measureWeights() {
  if (!scales_initialized) return;
  
  // Alle 4 Waagen gleichzeitig lesen
  weight_1 = scale1.get_units(1);
  weight_2 = scale2.get_units(1);
  weight_3 = scale3.get_units(1);
  weight_4 = scale4.get_units(1);
  
  // Gesamtgewicht berechnen
  total_weight = weight_1 + weight_2 + weight_3 + weight_4;
  
  // Negative Werte auf 0 setzen (Rauschen)
  if (weight_1 < 0) weight_1 = 0;
  if (weight_2 < 0) weight_2 = 0;
  if (weight_3 < 0) weight_3 = 0;
  if (weight_4 < 0) weight_4 = 0;
  if (total_weight < 0) total_weight = 0;
}

void sendWeightData() {
  if (!wifi_connected) return;
  
  // JSON-Message erstellen
  JsonDocument doc;
  doc["type"] = "weight_data";
  doc["timestamp"] = millis();
  doc["total_kg"] = round(total_weight * 100) / 100.0; // 2 Dezimalstellen
  
  JsonArray corners = doc["corners"].to<JsonArray>();
  corners.add(round(weight_1 * 100) / 100.0);
  corners.add(round(weight_2 * 100) / 100.0);
  corners.add(round(weight_3 * 100) / 100.0);
  corners.add(round(weight_4 * 100) / 100.0);
  
  doc["battery_v"] = round(battery_voltage * 10) / 10.0;
  doc["wifi_rssi"] = wifi_rssi;
  
  // Als String serialisieren und senden
  String message;
  serializeJson(doc, message);
  webSocket.broadcastTXT(message);
}

bool performTare() {
  if (!scales_initialized) return false;
  
  Serial.print("🔄 Tare wird durchgeführt... ");
  
  // Alle Waagen nullen
  scale1.tare();
  scale2.tare();
  scale3.tare();
  scale4.tare();
  
  // Kurz warten und prüfen
  delay(500);
  measureWeights();
  
  bool success = (abs(total_weight) < 0.1); // < 100g nach Tare
  Serial.println(success ? "OK" : "FEHLER");
  
  return success;
}

bool performCalibration(float referenceWeight) {
  if (!scales_initialized || referenceWeight <= 0) return false;
  
  Serial.printf("🎯 Kalibriere mit %.2f kg... ", referenceWeight);
  
  // Mehrere Messungen für Stabilität
  float sum1=0, sum2=0, sum3=0, sum4=0;
  int samples = 10;
  
  for (int i = 0; i < samples; i++) {
    sum1 += scale1.get_value();
    sum2 += scale2.get_value();
    sum3 += scale3.get_value();
    sum4 += scale4.get_value();
    delay(100);
  }
  
  // Durchschnitt berechnen
  float avg1 = sum1 / samples;
  float avg2 = sum2 / samples;
  float avg3 = sum3 / samples;
  float avg4 = sum4 / samples;
  
  // Neue Kalibrierungsfaktoren berechnen
  // Annahme: Gewicht gleichmäßig auf alle 4 Ecken verteilt
  float target_per_corner = referenceWeight / 4.0;
  
  calibration_factor_1 = avg1 / target_per_corner;
  calibration_factor_2 = avg2 / target_per_corner;
  calibration_factor_3 = avg3 / target_per_corner;
  calibration_factor_4 = avg4 / target_per_corner;
  
  // Faktoren anwenden
  scale1.set_scale(calibration_factor_1);
  scale2.set_scale(calibration_factor_2);
  scale3.set_scale(calibration_factor_3);
  scale4.set_scale(calibration_factor_4);
  
  // TODO: Faktoren in EEPROM speichern
  
  // Verifikation
  delay(500);
  measureWeights();
  float error = abs(total_weight - referenceWeight);
  bool success = (error < 0.1); // < 100g Abweichung
  
  Serial.printf("%s (Ist: %.2f kg, Soll: %.2f kg)\n", 
                success ? "OK" : "FEHLER", total_weight, referenceWeight);
  
  return success;
}

// =================== STATUS & MONITORING ===================

void sendStatusMessage(uint8_t clientNum) {
  JsonDocument doc;
  doc["type"] = "status";
  doc["device"] = DEVICE_NAME;
  doc["wifi_mode"] = (current_wifi_mode == 1) ? "HOME" : "AP";
  doc["wifi_ssid"] = (current_wifi_mode == 1) ? HOME_WIFI_SSID : AP_SSID;
  doc["ip_address"] = (current_wifi_mode == 1) ? WiFi.localIP().toString() : WiFi.softAPIP().toString();
  doc["wifi_rssi"] = wifi_rssi;
  doc["battery_v"] = battery_voltage;
  doc["scales_ok"] = scales_initialized;
  doc["uptime_ms"] = millis();
  doc["free_heap"] = ESP.getFreeHeap();
  doc["total_weight"] = total_weight;
  
  String message;
  serializeJson(doc, message);
  webSocket.sendTXT(clientNum, message);
}

void checkWiFiConnection() {
  bool was_connected = wifi_connected;
  wifi_connected = (WiFi.status() == WL_CONNECTED);
  
  if (!wifi_connected && was_connected) {
    Serial.println("📡 WiFi-Verbindung verloren - Reconnect...");
    digitalWrite(LED_WIFI, HIGH); // LED aus
    WiFi.reconnect();
  }
  else if (wifi_connected && !was_connected) {
    Serial.println("📡 WiFi-Verbindung wiederhergestellt");
    digitalWrite(LED_WIFI, LOW); // LED an
  }
  
  if (wifi_connected) {
    wifi_rssi = WiFi.RSSI();
  }
}

void checkBattery() {
  // ADC lesen (0-1024 entspricht 0-3.3V)
  int adc_value = analogRead(BATTERY_PIN);
  
  // Spannung am A0-Pin berechnen
  float voltage_a0 = (adc_value / 1024.0) * 3.3;
  
  // Echte Akku-Spannung zurückrechnen (2:1 Spannungsteiler)
  // 18650 Akku → 10kΩ → A0 → 10kΩ → GND
  battery_voltage = voltage_a0 * 2.0;
  
  // Niedrige Spannung prüfen
  if (battery_voltage < BATTERY_MIN) {
    Serial.printf("🔋 Niedrige Akku-Spannung: %.1fV\n", battery_voltage);
    
    // Warnung über WebSocket senden
    JsonDocument warning;
    warning["type"] = "battery_warning";
    warning["voltage"] = battery_voltage;
    warning["message"] = "Akku schwach - bitte aufladen";
    
    String warningStr;
    serializeJson(warning, warningStr);
    webSocket.broadcastTXT(warningStr);
    
    // Automatischer Deep Sleep bei kritischer Spannung - DEAKTIVIERT FÜR TESTS
    // if (battery_voltage < (BATTERY_MIN - 0.2)) {
    //   Serial.println("🔋 Kritische Spannung - Deep Sleep aktiviert");
    //   deep_sleep_requested = true;
    // }
    Serial.println("🧪 Deep Sleep deaktiviert für Tests");
  }
}

void updateStatusLED() {
  static bool led_state = false;
  
  if (wifi_connected && scales_initialized) {
    // Normal: Power LED konstant an
    digitalWrite(LED_POWER, HIGH);
  } else {
    // Problem: Power LED blinkt
    led_state = !led_state;
    digitalWrite(LED_POWER, led_state ? HIGH : LOW);
  }
}

void enterDeepSleep() {
  Serial.println("😴 Deep Sleep wird aktiviert...");
  
  // Status-Message senden
  JsonDocument msg;
  msg["type"] = "deep_sleep";
  msg["message"] = "ESP8266 geht in Deep Sleep";
  msg["duration_h"] = DEEP_SLEEP_DURATION / 3600000000;
  
  String msgStr;
  serializeJson(msg, msgStr);
  webSocket.broadcastTXT(msgStr);
  
  delay(1000); // Message senden lassen
  
  // LEDs ausschalten
  digitalWrite(LED_POWER, LOW);
  digitalWrite(LED_WIFI, HIGH);
  
  // Deep Sleep aktivieren
  ESP.deepSleep(DEEP_SLEEP_DURATION);
}

// =================== HILFSFUNKTIONEN ===================

void blinkLED(int pin, int count, int duration) {
  for (int i = 0; i < count; i++) {
    digitalWrite(pin, LOW);
    delay(duration);
    digitalWrite(pin, HIGH);
    delay(duration);
  }
}