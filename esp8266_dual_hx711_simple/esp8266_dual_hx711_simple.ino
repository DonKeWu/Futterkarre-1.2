/*
ESP8266 Dual-HX711 Einfacher Tester (OHNE JavaScript)
Direkter Browser-Test für 2 HX711-Module
*/

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <HX711.h>

// Quad HX711 Setup - ALLE 4 Module
const int HX711_VL_DT = D2;   // Vorne Links - Data
const int HX711_VL_SCK = D1;  // Vorne Links - Clock
const int HX711_VR_DT = D4;   // Vorne Rechts - Data  
const int HX711_VR_SCK = D3;  // Vorne Rechts - Clock
const int HX711_HL_DT = D6;   // Hinten Links - Data
const int HX711_HL_SCK = D5;  // Hinten Links - Clock
const int HX711_HR_DT = D8;   // Hinten Rechts - Data  
const int HX711_HR_SCK = D7;  // Hinten Rechts - Clock

// WiFi - ORIGINALE Zugangsdaten wiederhergestellt
const char* ssid = "IBIMSNOCH1MAL";
const char* password = "G8pY4B8K56vF";
const char* ap_ssid = "Futterkarre_WiFi";
const char* ap_password = "FutterWaage2025";

// HX711 Instanzen - ALLE 4
HX711 scale_VL;  // Vorne Links
HX711 scale_VR;  // Vorne Rechts
HX711 scale_HL;  // Hinten Links
HX711 scale_HR;  // Hinten Rechts
ESP8266WebServer server(80);

void setup() {
  Serial.begin(115200);
  Serial.println("\nESP8266 Quad-HX711 Tester gestartet");
  
  // HX711 initialisieren - ALLE 4
  scale_VL.begin(HX711_VL_DT, HX711_VL_SCK);
  scale_VR.begin(HX711_VR_DT, HX711_VR_SCK);
  scale_HL.begin(HX711_HL_DT, HX711_HL_SCK);
  scale_HR.begin(HX711_HR_DT, HX711_HR_SCK);
  
  Serial.println("Quad-HX711 initialisiert:");
  Serial.println("   VL (Vorne Links):  D2(DT) + D3(SCK)");
  Serial.println("   VR (Vorne Rechts): D4(DT) + D1(SCK)");
  Serial.println("   HL (Hinten Links): D6(DT) + D7(SCK)");
  Serial.println("   HR (Hinten Rechts): D8(DT) + D5(SCK)");
  
  setupWiFi();
  setupWebServer();
  
  server.begin();
  Serial.println("Web-Server gestartet");
  Serial.print("Browser-Test: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/");
}

void setupWiFi() {
  // STATISCHE IP für 192.168.2.20
  IPAddress local_IP(192, 168, 2, 20);
  IPAddress gateway(192, 168, 2, 1);
  IPAddress subnet(255, 255, 255, 0);
  IPAddress primaryDNS(8, 8, 8, 8);
  
  // Statische IP setzen
  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS)) {
    Serial.println("Statische IP fehlgeschlagen!");
  }
  
  // DUAL MODE: Station + Access Point
  WiFi.mode(WIFI_AP_STA);
  WiFi.begin(ssid, password);
  
  Serial.print("WiFi-Verbindung zu ");
  Serial.print(ssid);
  Serial.print(" -> 192.168.2.20");
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  // Access Point als Fallback
  WiFi.softAP(ap_ssid, ap_password);
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.print("SUCCESS! Station IP: http://");
    Serial.println(WiFi.localIP());
    Serial.print("Backup Access Point: http://");
    Serial.println(WiFi.softAPIP());
  } else {
    Serial.println();
    Serial.println("FEHLER: Station fehlgeschlagen!");
    Serial.print("Nur Access Point: http://");
    Serial.println(WiFi.softAPIP());
  }
}

void setupWebServer() {
  server.on("/", handleMainPage);
  server.on("/test-vl", handleTestVL);
  server.on("/test-vr", handleTestVR);
  server.on("/test-hl", handleTestHL);
  server.on("/test-hr", handleTestHR);
  server.on("/test-all", handleTestAll);
  server.on("/raw-data", handleRawData);
  server.on("/pin-check", handlePinCheck);
  server.on("/live-pins", handleLivePins);
  server.on("/hardware-test", handleHardwareTest);
  server.on("/live-values", handleLiveValues);  // Neue Live-Werte Anzeige
  server.on("/live-values-data", handleLiveValuesData);  // JSON API für Live-Daten  // ECHTER Hardware-Test
}

void handleMainPage() {
  String html = "<!DOCTYPE html>";
  html += "<html>";
  html += "<head>";
  html += "<title>ESP8266 Dual-HX711 Tester</title>";
  html += "<meta charset='utf-8'>";
  html += "<style>";
  html += "body { font-family: Arial; margin: 20px; }";
  html += ".container { max-width: 800px; margin: auto; }";
  html += ".button { ";
  html += "background: #4CAF50; color: white; padding: 15px 25px; ";
  html += "border: none; border-radius: 5px; font-size: 16px; ";
  html += "margin: 10px 5px; text-decoration: none; display: inline-block; ";
  html += "}";
  html += ".button:hover { background: #45a049; }";
  html += "</style>";
  html += "</head>";
  html += "<body>";
  html += "<div class='container'>";
  html += "<h1>ESP8266 Quad-HX711 Tester</h1>";
  
  html += "<h2>Hardware-Status</h2>";
  html += "<p><strong>VL (Vorne Links):</strong> D2(DT) + D1(SCK)</p>";
  html += "<p><strong>VR (Vorne Rechts):</strong> D4(DT) + D3(SCK)</p>";
  html += "<p><strong>HL (Hinten Links):</strong> D6(DT) + D5(SCK)</p>";
  html += "<p><strong>HR (Hinten Rechts):</strong> D8(DT) + D7(SCK)</p>";
  
  html += "<h2>Tests (Links klicken)</h2>";
  html += "<a href='/test-vl' class='button'>Test VL (Vorne Links)</a>";
  html += "<a href='/test-vr' class='button'>Test VR (Vorne Rechts)</a>";
  html += "<a href='/test-hl' class='button'>Test HL (Hinten Links)</a>";
  html += "<a href='/test-hr' class='button'>Test HR (Hinten Rechts)</a>";
  html += "<a href='/test-all' class='button' style='background:#ff9800;'>Test ALLE 4</a>";
  html += "<a href='/raw-data' class='button'>Raw-Daten</a>";
  html += "<a href='/pin-check' class='button'>Pin-Check</a>";
  html += "<a href='/live-pins' class='button' style='background:#e91e63;'>LIVE Pin-Monitor</a>";
  html += "<a href='/hardware-test' class='button' style='background:#f44336;'>ECHTER Hardware-Test</a>";
  html += "<a href='/live-values' class='button' style='background:#ff9800;'>🔴 LIVE WERTE (ALLE 4)</a>";
  html += "<br><br>";
  html += "<a href='/' class='button' style='background:#2196F3;'>Aktualisieren</a>";
  
  html += "<h2>Diagnose-Checkliste</h2>";
  html += "<ul>";
  html += "<li>[OK] ALLE 4 HX711 auf 5V (VIN)</li>";
  html += "<li>[OK] GND gemeinsam verbunden</li>";
  html += "<li>[?] Waegezellen angeschlossen an ALLE 4?</li>";
  html += "<li>[?] Pin-Zuordnung: VL=D2/D1, VR=D4/D3, HL=D6/D5, HR=D8/D7?</li>";
  html += "</ul>";
  
  html += "</div>";
  html += "</body>";
  html += "</html>";
  
  server.send(200, "text/html", html);
}

void handleTestVL() {
  String result = "HX711-VL (Vorne Links) Test\n";
  result += "============================\n";
  
  bool ready = scale_VL.is_ready();
  result += "Ready: " + String(ready ? "OK" : "NEIN") + "\n";
  
  if (ready) {
    long raw = scale_VL.read();
    result += "Raw-Wert: " + String(raw) + "\n";
    
    result += "\n5 Messungen:\n";
    for (int i = 0; i < 5; i++) {
      if (scale_VL.wait_ready_timeout(1000)) {
        long value = scale_VL.read();
        result += "  " + String(i+1) + ": " + String(value) + "\n";
      } else {
        result += "  " + String(i+1) + ": TIMEOUT\n";
      }
      delay(100);
    }
  } else {
    result += "HX711-VL antwortet nicht!\n";
    result += "Pruefe:\n";
    result += "- Stromversorgung 5V\n";
    result += "- Kabel D2->DT, D1->SCK\n";
    result += "- Waegezelle angeschlossen\n";
  }
  
  result += "\n<br><a href='/'>Zurueck zur Hauptseite</a>";
  
  server.send(200, "text/html", "<pre>" + result + "</pre>");
}

void handleTestVR() {
  String result = "HX711-VR (Vorne Rechts) Test\n";
  result += "=============================\n";
  
  bool ready = scale_VR.is_ready();
  result += "Ready: " + String(ready ? "OK" : "NEIN") + "\n";
  
  if (ready) {
    long raw = scale_VR.read();
    result += "Raw-Wert: " + String(raw) + "\n";
    
    result += "\n5 Messungen:\n";
    for (int i = 0; i < 5; i++) {
      if (scale_VR.wait_ready_timeout(1000)) {
        long value = scale_VR.read();
        result += "  " + String(i+1) + ": " + String(value) + "\n";
      } else {
        result += "  " + String(i+1) + ": TIMEOUT\n";
      }
      delay(100);
    }
  } else {
    result += "HX711-VR antwortet nicht!\n";
    result += "Pruefe:\n";
    result += "- Stromversorgung 5V\n";
    result += "- Kabel D4->DT, D3->SCK\n";
    result += "- Waegezelle angeschlossen\n";
  }
  
  result += "\n<br><a href='/'>Zurueck zur Hauptseite</a>";
  
  server.send(200, "text/html", "<pre>" + result + "</pre>");
}

void handleTestHL() {
  String result = "HX711-HL (Hinten Links) Test\n";
  result += "=============================\n";
  
  bool ready = scale_HL.is_ready();
  result += "Ready: " + String(ready ? "OK" : "NEIN") + "\n";
  
  if (ready) {
    long raw = scale_HL.read();
    result += "Raw-Wert: " + String(raw) + "\n";
    
    result += "\n5 Messungen:\n";
    for (int i = 0; i < 5; i++) {
      if (scale_HL.wait_ready_timeout(1000)) {
        long value = scale_HL.read();
        result += "  " + String(i+1) + ": " + String(value) + "\n";
      } else {
        result += "  " + String(i+1) + ": TIMEOUT\n";
      }
      delay(100);
    }
  } else {
    result += "HX711-HL antwortet nicht!\n";
    result += "Pruefe:\n";
    result += "- Stromversorgung 5V\n";
    result += "- Kabel D6->DT, D5->SCK\n";
    result += "- Waegezelle angeschlossen\n";
  }
  
  result += "\n<br><a href='/'>Zurueck zur Hauptseite</a>";
  
  server.send(200, "text/html", "<pre>" + result + "</pre>");
}

void handleTestHR() {
  String result = "HX711-HR (Hinten Rechts) Test\n";
  result += "==============================\n";
  
  bool ready = scale_HR.is_ready();
  result += "Ready: " + String(ready ? "OK" : "NEIN") + "\n";
  
  if (ready) {
    long raw = scale_HR.read();
    result += "Raw-Wert: " + String(raw) + "\n";
    
    result += "\n5 Messungen:\n";
    for (int i = 0; i < 5; i++) {
      if (scale_HR.wait_ready_timeout(1000)) {
        long value = scale_HR.read();
        result += "  " + String(i+1) + ": " + String(value) + "\n";
      } else {
        result += "  " + String(i+1) + ": TIMEOUT\n";
      }
      delay(100);
    }
  } else {
    result += "HX711-HR antwortet nicht!\n";
    result += "Pruefe:\n";
    result += "- Stromversorgung 5V\n";
    result += "- Kabel D8->DT, D7->SCK\n";
    result += "- Waegezelle angeschlossen\n";
  }
  
  result += "\n<br><a href='/'>Zurueck zur Hauptseite</a>";
  
  server.send(200, "text/html", "<pre>" + result + "</pre>");
}

void handleTestAll() {
  String result = "QUAD-HX711 Test - ALLE 4 Module\n";
  result += "=================================\n";
  
  bool vl_ready = scale_VL.is_ready();
  bool vr_ready = scale_VR.is_ready();
  bool hl_ready = scale_HL.is_ready();
  bool hr_ready = scale_HR.is_ready();
  
  result += "VL (Vorne Links):   " + String(vl_ready ? "READY" : "NOT READY") + "\n";
  result += "VR (Vorne Rechts):  " + String(vr_ready ? "READY" : "NOT READY") + "\n";
  result += "HL (Hinten Links):  " + String(hl_ready ? "READY" : "NOT READY") + "\n";
  result += "HR (Hinten Rechts): " + String(hr_ready ? "READY" : "NOT READY") + "\n";
  
  int ready_count = vl_ready + vr_ready + hl_ready + hr_ready;
  result += "\nVerfuegbare Module: " + String(ready_count) + " von 4\n";
  
  if (ready_count > 0) {
    result += "\nSimultane Messungen:\n";
    
    for (int i = 0; i < 3; i++) {
      result += "Messung " + String(i+1) + ":\n";
      
      if (vl_ready) {
        long vl_val = scale_VL.read();
        result += "  VL: " + String(vl_val) + "\n";
      }
      
      if (vr_ready) {
        long vr_val = scale_VR.read();
        result += "  VR: " + String(vr_val) + "\n";
      }
      
      if (hl_ready) {
        long hl_val = scale_HL.read();
        result += "  HL: " + String(hl_val) + "\n";
      }
      
      if (hr_ready) {
        long hr_val = scale_HR.read();
        result += "  HR: " + String(hr_val) + "\n";
      }
      
      result += "\n";
      delay(500);
    }
  } else {
    result += "\nKEINE HX711 antworten!\n";
    result += "Kritische Probleme:\n";
    result += "- Keine 5V Stromversorgung?\n";
    result += "- Falsche Pin-Verdrahtung?\n";
    result += "- Waegezellen nicht verbunden?\n";
  }
  
  result += "\n<br><a href='/'>Zurueck zur Hauptseite</a>";
  
  server.send(200, "text/html", "<pre>" + result + "</pre>");
}

void handleTestBoth() {
  String result = "Dual-HX711 Test\n";
  result += "==================\n";
  
  bool hl_ready = scale_HL.is_ready();
  bool hr_ready = scale_HR.is_ready();
  
  result += "HL (Links):  " + String(hl_ready ? "READY" : "NOT READY") + "\n";
  result += "HR (Rechts): " + String(hr_ready ? "READY" : "NOT READY") + "\n";
  
  if (hl_ready || hr_ready) {
    result += "\nSimultane Messungen:\n";
    
    for (int i = 0; i < 3; i++) {
      result += "Messung " + String(i+1) + ":\n";
      
      if (hl_ready) {
        long hl_val = scale_HL.read();
        result += "  HL: " + String(hl_val) + "\n";
      }
      
      if (hr_ready) {
        long hr_val = scale_HR.read();
        result += "  HR: " + String(hr_val) + "\n";
      }
      
      result += "\n";
      delay(500);
    }
  } else {
    result += "\nBEIDE HX711 antworten nicht!\n";
    result += "Kritische Probleme:\n";
    result += "- Keine 5V Stromversorgung?\n";
    result += "- Falsche Pin-Verdrahtung?\n";
    result += "- Waegezellen nicht verbunden?\n";
  }
  
  result += "\n<br><a href='/'>Zurueck zur Hauptseite</a>";
  
  server.send(200, "text/html", "<pre>" + result + "</pre>");
}

void handleRawData() {
  String result = "Raw-Daten Analyse\n";
  result += "====================\n";
  
  result += "Pin-Zustaende:\n";
  result += "D2 (VL-DT):  " + String(digitalRead(HX711_VL_DT) ? "HIGH" : "LOW") + "\n";
  result += "D1 (VL-SCK): " + String(digitalRead(HX711_VL_SCK) ? "HIGH" : "LOW") + "\n";
  result += "D4 (VR-DT):  " + String(digitalRead(HX711_VR_DT) ? "HIGH" : "LOW") + "\n";
  result += "D3 (VR-SCK): " + String(digitalRead(HX711_VR_SCK) ? "HIGH" : "LOW") + "\n";
  result += "D6 (HL-DT):  " + String(digitalRead(HX711_HL_DT) ? "HIGH" : "LOW") + "\n";
  result += "D5 (HL-SCK): " + String(digitalRead(HX711_HL_SCK) ? "HIGH" : "LOW") + "\n";
  result += "D8 (HR-DT):  " + String(digitalRead(HX711_HR_DT) ? "HIGH" : "LOW") + "\n";
  result += "D7 (HR-SCK): " + String(digitalRead(HX711_HR_SCK) ? "HIGH" : "LOW") + "\n";
  
  result += "\nHX711 Status:\n";
  result += "VL Ready: " + String(scale_VL.is_ready() ? "JA" : "NEIN") + "\n";
  result += "VR Ready: " + String(scale_VR.is_ready() ? "JA" : "NEIN") + "\n";
  result += "HL Ready: " + String(scale_HL.is_ready() ? "JA" : "NEIN") + "\n";
  result += "HR Ready: " + String(scale_HR.is_ready() ? "JA" : "NEIN") + "\n";
  
  result += "\n<br><a href='/'>Zurueck zur Hauptseite</a>";
  
  server.send(200, "text/html", "<pre>" + result + "</pre>");
}

void handlePinCheck() {
  String result = "Pin-Konfiguration Check\n";
  result += "==========================\n";
  
  result += "Konfigurierte Pins:\n";
  result += "HX711-VL: D2(" + String(HX711_VL_DT) + ") + D1(" + String(HX711_VL_SCK) + ")\n";
  result += "HX711-VR: D4(" + String(HX711_VR_DT) + ") + D3(" + String(HX711_VR_SCK) + ")\n";
  result += "HX711-HL: D6(" + String(HX711_HL_DT) + ") + D5(" + String(HX711_HL_SCK) + ")\n";
  result += "HX711-HR: D8(" + String(HX711_HR_DT) + ") + D7(" + String(HX711_HR_SCK) + ")\n";
  
  result += "\nPin-Modi:\n";
  result += "D2: INPUT  (VL-DT)    D1: OUTPUT (VL-SCK)\n";
  result += "D4: INPUT  (VR-DT)    D3: OUTPUT (VR-SCK)\n";
  result += "D6: INPUT  (HL-DT)    D5: OUTPUT (HL-SCK)\n";
  result += "D8: INPUT  (HR-DT)    D7: OUTPUT (HR-SCK)\n";
  
  result += "\nVerkabelung sollte sein:\n";
  result += "ESP8266 -> HX711-VL -> HX711-VR -> HX711-HL -> HX711-HR\n";
  result += "   D2   ->    DT          D4   ->    DT          D6   ->    DT          D8   ->    DT\n";
  result += "   D1   ->   SCK          D3   ->   SCK          D5   ->   SCK          D7   ->   SCK\n";
  result += "  VIN   ->   VCC         VIN   ->   VCC         VIN   ->   VCC         VIN   ->   VCC\n";
  result += "  GND   ->   GND         GND   ->   GND         GND   ->   GND         GND   ->   GND\n";
  
  result += "\n<br><a href='/'>Zurueck zur Hauptseite</a>";
  
  server.send(200, "text/html", "<pre>" + result + "</pre>");
}

void handleLivePins() {
  String html = "<!DOCTYPE html>";
  html += "<html>";
  html += "<head>";
  html += "<title>LIVE Pin-Monitor</title>";
  html += "<meta charset='utf-8'>";
  html += "<meta http-equiv='refresh' content='1'>";  // Auto-refresh jede Sekunde
  html += "<style>";
  html += "body { font-family: monospace; margin: 20px; background: black; color: lime; }";
  html += ".high { color: red; font-weight: bold; }";
  html += ".low { color: cyan; }";
  html += ".ready { color: lime; font-weight: bold; }";
  html += ".not-ready { color: yellow; }";
  html += "</style>";
  html += "</head>";
  html += "<body>";
  html += "<h1>LIVE PIN-MONITOR (Auto-Refresh)</h1>";
  html += "<p>Aktualisiert sich automatisch jede Sekunde...</p>";
  html += "<hr>";
  
  // Aktuelle Zeit
  html += "<p>Zeitstempel: " + String(millis()/1000) + " Sekunden</p>";
  
  // Pin-Zustände live lesen
  int vl_dt = digitalRead(HX711_VL_DT);
  int vl_sck = digitalRead(HX711_VL_SCK);
  bool vl_ready = scale_VL.is_ready();
  
  int vr_dt = digitalRead(HX711_VR_DT);
  int vr_sck = digitalRead(HX711_VR_SCK);
  bool vr_ready = scale_VR.is_ready();
  
  int hl_dt = digitalRead(HX711_HL_DT);
  int hl_sck = digitalRead(HX711_HL_SCK);
  bool hl_ready = scale_HL.is_ready();
  
  int hr_dt = digitalRead(HX711_HR_DT);
  int hr_sck = digitalRead(HX711_HR_SCK);
  bool hr_ready = scale_HR.is_ready();
  
  html += "<h2>VL (Vorne Links) - D2/D1:</h2>";
  html += "<p>DT (D2): <span class='" + String(vl_dt ? "high" : "low") + "'>" + String(vl_dt ? "HIGH" : "LOW") + "</span></p>";
  html += "<p>SCK (D1): <span class='" + String(vl_sck ? "high" : "low") + "'>" + String(vl_sck ? "HIGH" : "LOW") + "</span></p>";
  html += "<p>Ready: <span class='" + String(vl_ready ? "ready" : "not-ready") + "'>" + String(vl_ready ? "JA" : "NEIN") + "</span></p>";
  
  html += "<h2>VR (Vorne Rechts) - D4/D3:</h2>";
  html += "<p>DT (D4): <span class='" + String(vr_dt ? "high" : "low") + "'>" + String(vr_dt ? "HIGH" : "LOW") + "</span></p>";
  html += "<p>SCK (D3): <span class='" + String(vr_sck ? "high" : "low") + "'>" + String(vr_sck ? "HIGH" : "LOW") + "</span></p>";
  html += "<p>Ready: <span class='" + String(vr_ready ? "ready" : "not-ready") + "'>" + String(vr_ready ? "JA" : "NEIN") + "</span></p>";
  
  html += "<h2>HL (Hinten Links) - D6/D5:</h2>";
  html += "<p>DT (D6): <span class='" + String(hl_dt ? "high" : "low") + "'>" + String(hl_dt ? "HIGH" : "LOW") + "</span></p>";
  html += "<p>SCK (D5): <span class='" + String(hl_sck ? "high" : "low") + "'>" + String(hl_sck ? "HIGH" : "LOW") + "</span></p>";
  html += "<p>Ready: <span class='" + String(hl_ready ? "ready" : "not-ready") + "'>" + String(hl_ready ? "JA" : "NEIN") + "</span></p>";
  
  html += "<h2>HR (Hinten Rechts) - D8/D7:</h2>";
  html += "<p>DT (D8): <span class='" + String(hr_dt ? "high" : "low") + "'>" + String(hr_dt ? "HIGH" : "LOW") + "</span></p>";
  html += "<p>SCK (D7): <span class='" + String(hr_sck ? "high" : "low") + "'>" + String(hr_sck ? "HIGH" : "LOW") + "</span></p>";
  html += "<p>Ready: <span class='" + String(hr_ready ? "ready" : "not-ready") + "'>" + String(hr_ready ? "JA" : "NEIN") + "</span></p>";
  
  html += "<hr>";
  html += "<h2>SIGNAL-INTERPRETATION:</h2>";
  html += "<p>DT LOW + Ready=JA = HX711 bereit fuer Messung</p>";
  html += "<p>DT wechselt HIGH/LOW = HX711 sendet Daten</p>";
  html += "<p>DT HIGH dauerhaft = HX711 nicht bereit/Problem</p>";
  html += "<p>SCK sollte normalerweise LOW sein</p>";
  
  html += "<br><a href='/' style='color:white;'>Zurueck zur Hauptseite</a>";
  html += "</body>";
  html += "</html>";
  
  server.send(200, "text/html", html);
}

void handleHardwareTest() {
  String result = "ECHTER HARDWARE-TEST\n";
  result += "=====================\n";
  result += "Testet ob WIRKLICH HX711 + Waegezellen angeschlossen sind!\n\n";
  
  result += "THEORIE:\n";
  result += "--------\n";
  result += "- HX711: 24-Bit ADC (16.777.216 Stufen)\n";
  result += "- Waegezelle: Wheatstone-Bruecke mit 4 Dehnungsmessstreifen\n";
  result += "- Signal: Millivolt pro Kilogramm\n";
  result += "- OHNE Waegezelle: Keine echten Messwerte moeglich!\n\n";
  
  // Test-Methode: DT-Pin-Verhalten analysieren
  result += "METHODE 1: DT-Pin Verhalten analysieren\n";
  result += "----------------------------------------\n";
  
  bool vl_real = testRealHX711(HX711_VL_DT, HX711_VL_SCK, "VL");
  bool vr_real = testRealHX711(HX711_VR_DT, HX711_VR_SCK, "VR");
  bool hl_real = testRealHX711(HX711_HL_DT, HX711_HL_SCK, "HL");
  bool hr_real = testRealHX711(HX711_HR_DT, HX711_HR_SCK, "HR");
  
  result += "\nMETHODE 2: Wheatstone-Bruecken-Test\n";
  result += "-----------------------------------\n";
  
  bool vl_cell = testLoadCell("VL", vl_real);
  bool vr_cell = testLoadCell("VR", vr_real);
  bool hl_cell = testLoadCell("HL", hl_real);
  bool hr_cell = testLoadCell("HR", hr_real);
  
  result += "\nERGEBNIS:\n";
  result += "=========\n";
  result += "VL (D2/D1): HX711=" + String(vl_real ? "JA" : "NEIN") + " | Waegezelle=" + String(vl_cell ? "JA" : "NEIN") + "\n";
  result += "VR (D4/D3): HX711=" + String(vr_real ? "JA" : "NEIN") + " | Waegezelle=" + String(vr_cell ? "JA" : "NEIN") + "\n";
  result += "HL (D6/D5): HX711=" + String(hl_real ? "JA" : "NEIN") + " | Waegezelle=" + String(hl_cell ? "JA" : "NEIN") + "\n";
  result += "HR (D8/D7): HX711=" + String(hr_real ? "JA" : "NEIN") + " | Waegezelle=" + String(hr_cell ? "JA" : "NEIN") + "\n";
  
  int hx711_count = vl_real + vr_real + hl_real + hr_real;
  int cell_count = vl_cell + vr_cell + hl_cell + hr_cell;
  
  result += "\nZUSAMMENFASSUNG:\n";
  result += "HX711-Module: " + String(hx711_count) + " von 4\n";
  result += "Waegezellen:  " + String(cell_count) + " von 4\n";
  
  if (hx711_count == 0 && cell_count == 0) {
    result += "\nSTATUS: KEINE HARDWARE ANGESCHLOSSEN!\n";
    result += "Alle 'Ready'-Signale sind FALSCH-POSITIV!\n";
    result += "ESP8266 zeigt nur interne Pullup/Pulldown-Zustaende.\n";
  } else if (hx711_count > 0 && cell_count == 0) {
    result += "\nSTATUS: HX711 OHNE WAEGEZELLEN!\n";
    result += "Module reagieren, aber keine Wheatstone-Bruecken.\n";
    result += "Messwerte waeren unbrauchbar (nur Rauschen).\n";
  } else {
    result += "\nSTATUS: FUNKTIONSFAEHIGE WAAGE!\n";
    result += "HX711 + Waegezellen korrekt angeschlossen.\n";
  }
  
  result += "\n<br><a href='/'>Zurueck zur Hauptseite</a>";
  
  server.send(200, "text/html", "<pre>" + result + "</pre>");
}

void handleLiveValues() {
  String html = "<!DOCTYPE html>";
  html += "<html><head>";
  html += "<meta charset='UTF-8'>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1.0'>";
  html += "<title>🔴 LIVE WERTE - ALLE 4 HX711</title>";
  html += "<style>";
  html += "body { font-family: Arial; margin: 20px; background: #1a1a1a; color: #fff; }";
  html += ".container { max-width: 1000px; margin: 0 auto; }";
  html += ".grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }";
  html += ".value-box { background: #2c2c2c; border: 2px solid #444; border-radius: 10px; padding: 20px; }";
  html += ".vl-box { border-color: #4CAF50; }";
  html += ".vr-box { border-color: #2196F3; }";
  html += ".hl-box { border-color: #FF9800; }";
  html += ".hr-box { border-color: #E91E63; }";
  html += ".value { font-size: 2em; font-weight: bold; text-align: center; margin: 10px 0; }";
  html += ".vl-value { color: #4CAF50; }";
  html += ".vr-value { color: #2196F3; }";
  html += ".hl-value { color: #FF9800; }";
  html += ".hr-value { color: #E91E63; }";
  html += ".label { font-size: 1.1em; text-align: center; margin-bottom: 10px; font-weight: bold; }";
  html += ".status { text-align: center; margin: 10px 0; }";
  html += ".ready { color: #4CAF50; }";
  html += ".not-ready { color: #f44336; }";
  html += ".button { background: #444; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; margin: 5px; }";
  html += ".auto-refresh { color: #ff9800; text-align: center; margin: 10px 0; }";
  html += "@media (max-width: 600px) { .grid { grid-template-columns: 1fr; } }";
  html += "</style>";
  
  // Auto-Refresh alle 500ms
  html += "<script>";
  html += "setInterval(function() {";
  html += "  fetch('/live-values-data')";
  html += "    .then(response => response.json())";
  html += "    .then(data => {";
  html += "      document.getElementById('vl-value').innerText = data.vl_value;";
  html += "      document.getElementById('vr-value').innerText = data.vr_value;";
  html += "      document.getElementById('hl-value').innerText = data.hl_value;";
  html += "      document.getElementById('hr-value').innerText = data.hr_value;";
  html += "      document.getElementById('vl-status').innerText = data.vl_ready ? 'READY ✓' : 'NOT READY ✗';";
  html += "      document.getElementById('vr-status').innerText = data.vr_ready ? 'READY ✓' : 'NOT READY ✗';";
  html += "      document.getElementById('hl-status').innerText = data.hl_ready ? 'READY ✓' : 'NOT READY ✗';";
  html += "      document.getElementById('hr-status').innerText = data.hr_ready ? 'READY ✓' : 'NOT READY ✗';";
  html += "      document.getElementById('vl-status').className = 'status ' + (data.vl_ready ? 'ready' : 'not-ready');";
  html += "      document.getElementById('vr-status').className = 'status ' + (data.vr_ready ? 'ready' : 'not-ready');";
  html += "      document.getElementById('hl-status').className = 'status ' + (data.hl_ready ? 'ready' : 'not-ready');";
  html += "      document.getElementById('hr-status').className = 'status ' + (data.hr_ready ? 'ready' : 'not-ready');";
  html += "    });";
  html += "}, 500);";
  html += "</script>";
  
  html += "</head><body>";
  html += "<div class='container'>";
  html += "<h1>🔴 LIVE WERTE - ALLE 4 HX711</h1>";
  html += "<div class='auto-refresh'>⚡ Auto-Update alle 500ms</div>";
  
  html += "<div class='grid'>";
  
  // VL Box
  html += "<div class='value-box vl-box'>";
  html += "<div class='label'>📍 VL - VORNE LINKS (D2/D1)</div>";
  html += "<div class='value vl-value' id='vl-value'>Laden...</div>";
  html += "<div class='status' id='vl-status'>-</div>";
  html += "</div>";
  
  // VR Box  
  html += "<div class='value-box vr-box'>";
  html += "<div class='label'>📍 VR - VORNE RECHTS (D4/D3)</div>";
  html += "<div class='value vr-value' id='vr-value'>Laden...</div>";
  html += "<div class='status' id='vr-status'>-</div>";
  html += "</div>";
  
  // HL Box
  html += "<div class='value-box hl-box'>";
  html += "<div class='label'>📍 HL - HINTEN LINKS (D6/D5)</div>";
  html += "<div class='value hl-value' id='hl-value'>Laden...</div>";
  html += "<div class='status' id='hl-status'>-</div>";
  html += "</div>";
  
  // HR Box  
  html += "<div class='value-box hr-box'>";
  html += "<div class='label'>📍 HR - HINTEN RECHTS (D8/D7)</div>";
  html += "<div class='value hr-value' id='hr-value'>Laden...</div>";
  html += "<div class='status' id='hr-status'>-</div>";
  html += "</div>";
  
  html += "</div>"; // End grid
  
  html += "<div style='text-align: center; margin: 30px 0;'>";
  html += "<a href='/' class='button'>🏠 Hauptseite</a>";
  html += "<a href='/live-pins' class='button'>📊 Pin-Monitor</a>";
  html += "</div>";
  
  html += "</div></body></html>";
  
  server.send(200, "text/html", html);
}

void handleLiveValuesData() {
  // VL Werte lesen
  bool vl_ready = scale_VL.is_ready();
  long vl_raw = 0;
  if (vl_ready && scale_VL.wait_ready_timeout(50)) {
    vl_raw = scale_VL.read();
  }
  
  // VR Werte lesen
  bool vr_ready = scale_VR.is_ready();
  long vr_raw = 0;
  if (vr_ready && scale_VR.wait_ready_timeout(50)) {
    vr_raw = scale_VR.read();
  }
  
  // HL Werte lesen
  bool hl_ready = scale_HL.is_ready();
  long hl_raw = 0;
  if (hl_ready && scale_HL.wait_ready_timeout(50)) {
    hl_raw = scale_HL.read();
  }
  
  // HR Werte lesen  
  bool hr_ready = scale_HR.is_ready();
  long hr_raw = 0;
  if (hr_ready && scale_HR.wait_ready_timeout(50)) {
    hr_raw = scale_HR.read();
  }
  
  // JSON Response erstellen
  String json = "{";
  json += "\"vl_ready\":" + String(vl_ready ? "true" : "false") + ",";
  json += "\"vr_ready\":" + String(vr_ready ? "true" : "false") + ",";
  json += "\"hl_ready\":" + String(hl_ready ? "true" : "false") + ",";
  json += "\"hr_ready\":" + String(hr_ready ? "true" : "false") + ",";
  json += "\"vl_value\":\"" + String(vl_raw) + "\",";
  json += "\"vr_value\":\"" + String(vr_raw) + "\",";
  json += "\"hl_value\":\"" + String(hl_raw) + "\",";
  json += "\"hr_value\":\"" + String(hr_raw) + "\",";
  json += "\"timestamp\":" + String(millis());
  json += "}";
  
  server.sendHeader("Access-Control-Allow-Origin", "*");  // CORS für AJAX
  server.send(200, "application/json", json);
}

bool testLoadCell(String name, bool hx711_present) {
  Serial.println("WAEGEZELLEN-TEST fuer " + name);
  
  if (!hx711_present) {
    Serial.println("  Kein HX711 -> Keine Waegezelle moeglich");
    return false;
  }
  
  // Simuliere Belastungstest durch Messwert-Variation
  // ECHTE Wägezellen zeigen:
  // 1. Schwankungen auch ohne Belastung (Rauschen der Wheatstone-Brücke)
  // 2. Drift durch Temperatur
  // 3. Nicht-null Basis-Offset
  
  HX711* scale = nullptr;
  if (name == "VL") scale = &scale_VL;
  else if (name == "VR") scale = &scale_VR;
  else if (name == "HL") scale = &scale_HL;
  else if (name == "HR") scale = &scale_HR;
  
  if (!scale) return false;
  
  // Teste 5 schnelle Messungen
  long values[5];
  
  for (int i = 0; i < 5; i++) {
    if (scale->is_ready()) {
      values[i] = scale->read();
      delay(10);
    } else {
      values[i] = 0;
    }
  }
  
  // Analysiere Variation
  long min_val = values[0];
  long max_val = values[0];
  
  for (int i = 1; i < 5; i++) {
    if (values[i] < min_val) min_val = values[i];
    if (values[i] > max_val) max_val = values[i];
  }
  
  long variation = max_val - min_val;
  
  Serial.println("  Min: " + String(min_val) + ", Max: " + String(max_val) + ", Variation: " + String(variation));
  
  // ECHTE Wägezellen haben immer eine Grundvariation (Rauschen)
  // Ohne Wägezelle: Immer gleicher Wert oder nur digitales Rauschen
  if (variation > 50) {  // Mehr als 50 LSB Variation = echte Wheatstone-Brücke
    Serial.println("  WAEGEZELLE ERKANNT (Natuerliche Variation)");
    return true;
  } else {
    Serial.println("  KEINE WAEGEZELLE (Kein natuerliches Rauschen)");
    return false;
  }
}

// Teste ob WIRKLICH HX711-Hardware angeschlossen ist
bool testRealHX711(int dt_pin, int sck_pin, String name) {
  Serial.println("HX711-Test " + name + ":");
  
  // DT-Pin als Input, SCK als Output konfigurieren
  pinMode(dt_pin, INPUT);
  pinMode(sck_pin, OUTPUT);
  
  // Test 1: DT-Pin Grundzustand
  int initial_dt = digitalRead(dt_pin);
  int reactions = 0;
  
  // Test 2: SCK-Pulse senden und DT-Reaktion prüfen
  for (int i = 0; i < 5; i++) {
    digitalWrite(sck_pin, HIGH);
    delayMicroseconds(1);
    int dt_after_sck_high = digitalRead(dt_pin);
    
    digitalWrite(sck_pin, LOW);
    delayMicroseconds(1);
    int dt_after_sck_low = digitalRead(dt_pin);
    
    // Echte HX711 reagieren auf SCK-Pulse
    if (dt_after_sck_high != initial_dt || dt_after_sck_low != initial_dt) {
      reactions++;
    }
    delay(2);
  }
  
  Serial.println("  Initial DT: " + String(initial_dt));
  Serial.println("  Reaktionen: " + String(reactions) + "/5");
  Serial.println("  Bewertung: " + String(reactions >= 2 ? "HARDWARE" : "FAKE"));
  
  return (reactions >= 2);  // Mindestens 2 von 5 Reaktionen = echte Hardware
}

void loop() {
  server.handleClient();
  
  static unsigned long lastDebug = 0;
  if (millis() - lastDebug > 10000) {
    lastDebug = millis();
    
    Serial.println("Status-Check:");
    Serial.println("  VL Ready: " + String(scale_VL.is_ready() ? "JA" : "NEIN"));
    Serial.println("  VR Ready: " + String(scale_VR.is_ready() ? "JA" : "NEIN"));
    Serial.println("  HL Ready: " + String(scale_HL.is_ready() ? "JA" : "NEIN"));
    Serial.println("  HR Ready: " + String(scale_HR.is_ready() ? "JA" : "NEIN"));
  }
}
