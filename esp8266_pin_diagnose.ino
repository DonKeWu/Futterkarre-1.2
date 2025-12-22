/*
ESP8266 Pin-Diagnose für HX711-Kommunikation
Testet ob Signale auf D6/D7 ankommen und gibt detaillierte Pin-Informationen zurück
*/

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <HX711.h>

// HX711 Pins
const int LOADCELL_DOUT_PIN = D6;  // DT Pin
const int LOADCELL_SCK_PIN = D7;   // SCK Pin

// WiFi Konfiguration
const char* ssid = "FRITZ!Box 7590 EJ";
const char* password = "52618642761734340504";
const char* ap_ssid = "ESP8266-Waage";
const char* ap_password = "waage2024";

// HX711 und Server
HX711 scale;
ESP8266WebServer server(80);

// Diagnose-Variablen
unsigned long lastPinCheck = 0;
int d6_readings[10] = {0};
int d7_readings[10] = {0};
int reading_index = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("\n🔍 ESP8266 HX711 Pin-Diagnose gestartet");
  
  // Pins initialisieren
  pinMode(LOADCELL_DOUT_PIN, INPUT);
  pinMode(LOADCELL_SCK_PIN, OUTPUT);
  
  // HX711 initialisieren
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  Serial.println("📊 HX711 initialisiert");
  
  // WiFi-Verbindung
  setupWiFi();
  
  // Web-Endpunkte für Pin-Diagnose
  server.on("/status", handleStatus);
  server.on("/pin-status", handlePinStatus);
  server.on("/hx711-raw", handleHX711Raw);
  server.on("/pin-signals", handlePinSignals);
  
  server.begin();
  Serial.println("🌐 HTTP-Server gestartet für Pin-Diagnose");
  Serial.print("🔗 Diagnose-URL: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/pin-status");
}

void setupWiFi() {
  // Station Mode versuchen
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  Serial.print("📡 Verbindung zu WiFi");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.print("✅ WiFi verbunden! IP: ");
    Serial.println(WiFi.localIP());
  } else {
    // Access Point Mode als Fallback
    Serial.println();
    Serial.println("⚠️  Station Mode fehlgeschlagen, starte Access Point");
    WiFi.mode(WIFI_AP);
    WiFi.softAP(ap_ssid, ap_password);
    Serial.print("📶 Access Point gestartet: ");
    Serial.println(ap_ssid);
    Serial.print("🔗 IP-Adresse: ");
    Serial.println(WiFi.softAPIP());
  }
}

void handleStatus() {
  String json = "{";
  json += "\"device\":\"ESP8266-HX711-Diagnose\",";
  json += "\"uptime\":" + String(millis()) + ",";
  json += "\"wifi_connected\":" + String(WiFi.status() == WL_CONNECTED ? "true" : "false") + ",";
  json += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
  json += "\"hx711_connected\":" + String(scale.is_ready() ? "true" : "false");
  json += "}";
  
  server.send(200, "application/json", json);
}

void handlePinStatus() {
  // Pin-Zustände direkt lesen
  int d6_state = digitalRead(LOADCELL_DOUT_PIN);
  int d7_state = digitalRead(LOADCELL_SCK_PIN);
  bool hx711_ready = scale.is_ready();
  
  String json = "{";
  json += "\"d6_status\":\"" + String(d6_state ? "HIGH" : "LOW") + "\",";
  json += "\"d7_status\":\"" + String(d7_state ? "HIGH" : "LOW") + "\",";
  json += "\"d6_pin_number\":" + String(LOADCELL_DOUT_PIN) + ",";
  json += "\"d7_pin_number\":" + String(LOADCELL_SCK_PIN) + ",";
  json += "\"hx711_ready\":" + String(hx711_ready ? "true" : "false") + ",";
  json += "\"timestamp\":" + String(millis());
  json += "}";
  
  server.send(200, "application/json", json);
  
  // Debug-Ausgabe
  Serial.println("📊 Pin-Status abgefragt:");
  Serial.println("   D6 (DT): " + String(d6_state ? "HIGH" : "LOW"));
  Serial.println("   D7 (SCK): " + String(d7_state ? "HIGH" : "LOW"));
  Serial.println("   HX711 Ready: " + String(hx711_ready ? "JA" : "NEIN"));
}

void handleHX711Raw() {
  // HX711 Raw-Daten lesen
  bool is_ready = scale.is_ready();
  long raw_value = 0;
  
  if (is_ready) {
    raw_value = scale.read();
  }
  
  // Pin-Zustände
  int pin_dt = digitalRead(LOADCELL_DOUT_PIN);
  int pin_sck = digitalRead(LOADCELL_SCK_PIN);
  
  String json = "{";
  json += "\"raw_value\":" + String(raw_value) + ",";
  json += "\"is_ready\":" + String(is_ready ? "true" : "false") + ",";
  json += "\"pin_dt_state\":\"" + String(pin_dt ? "HIGH" : "LOW") + "\",";
  json += "\"pin_sck_state\":\"" + String(pin_sck ? "HIGH" : "LOW") + "\",";
  json += "\"scale_units\":" + String(scale.get_units()) + ",";
  json += "\"timestamp\":" + String(millis());
  json += "}";
  
  server.send(200, "application/json", json);
  
  Serial.println("🔧 HX711-Raw abgefragt:");
  Serial.println("   Raw-Wert: " + String(raw_value));
  Serial.println("   Ready: " + String(is_ready ? "JA" : "NEIN"));
  Serial.println("   DT-Pin: " + String(pin_dt ? "HIGH" : "LOW"));
  Serial.println("   SCK-Pin: " + String(pin_sck ? "HIGH" : "LOW"));
}

void handlePinSignals() {
  // Pin-Signale für Wellenform-Analyse
  int d6_level = digitalRead(LOADCELL_DOUT_PIN);
  int d7_level = digitalRead(LOADCELL_SCK_PIN);
  bool hx711_ready = scale.is_ready();
  
  // In Ringpuffer speichern
  d6_readings[reading_index] = d6_level;
  d7_readings[reading_index] = d7_level;
  reading_index = (reading_index + 1) % 10;
  
  // Aktivität berechnen
  bool d6_activity = false;
  bool d7_activity = false;
  int first_d6 = d6_readings[0];
  int first_d7 = d7_readings[0];
  
  for (int i = 1; i < 10; i++) {
    if (d6_readings[i] != first_d6) d6_activity = true;
    if (d7_readings[i] != first_d7) d7_activity = true;
  }
  
  String json = "{";
  json += "\"d6_level\":" + String(d6_level) + ",";
  json += "\"d7_level\":" + String(d7_level) + ",";
  json += "\"hx711_ready\":" + String(hx711_ready ? "true" : "false") + ",";
  json += "\"d6_activity\":" + String(d6_activity ? "true" : "false") + ",";
  json += "\"d7_activity\":" + String(d7_activity ? "true" : "false") + ",";
  json += "\"timestamp\":" + String(millis());
  json += "}";
  
  server.send(200, "application/json", json);
}

void loop() {
  server.handleClient();
  
  // Kontinuierliche Pin-Überwachung (alle 5 Sekunden)
  if (millis() - lastPinCheck > 5000) {
    lastPinCheck = millis();
    
    int d6 = digitalRead(LOADCELL_DOUT_PIN);
    int d7 = digitalRead(LOADCELL_SCK_PIN);
    bool ready = scale.is_ready();
    
    Serial.println("🔄 Pin-Monitor:");
    Serial.println("   D6: " + String(d6 ? "HIGH" : "LOW") + " | D7: " + String(d7 ? "HIGH" : "LOW") + " | HX711: " + String(ready ? "READY" : "NOT READY"));
    
    if (!ready && d6 == HIGH) {
      Serial.println("⚠️  HX711 zeigt NOT READY aber DT-Pin ist HIGH - mögliche Verkabelung OK");
    } else if (!ready && d6 == LOW) {
      Serial.println("❌ HX711 NOT READY und DT-Pin LOW - prüfe Stromversorgung/Verkabelung");
    }
  }
}