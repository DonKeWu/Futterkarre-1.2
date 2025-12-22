/*
ESP8266 Dual-HX711 Web-Tester
Direkter Browser-Test für 2 HX711-Module (HL und HR)
*/

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <HX711.h>

// Dual HX711 Setup
const int HX711_HL_DT = D6;   // Links - Data
const int HX711_HL_SCK = D7;  // Links - Clock
const int HX711_HR_DT = D8;   // Rechts - Data  
const int HX711_HR_SCK = D5;  // Rechts - Clock

// WiFi
const char* ssid = "FRITZ!Box 7590 EJ";
const char* password = "52618642761734340504";
const char* ap_ssid = "ESP8266-DualWaage";
const char* ap_password = "waage2024";

// HX711 Instanzen
HX711 scale_HL;  // Links
HX711 scale_HR;  // Rechts
ESP8266WebServer server(80);

void setup() {
  Serial.begin(115200);
  Serial.println("\nESP8266 Dual-HX711 Web-Tester gestartet");
  
  // HX711 initialisieren
  scale_HL.begin(HX711_HL_DT, HX711_HL_SCK);
  scale_HR.begin(HX711_HR_DT, HX711_HR_SCK);
  
  Serial.println("Dual-HX711 initialisiert:");
  Serial.println("   HL (Links):  D6(DT) + D7(SCK)");
  Serial.println("   HR (Rechts): D8(DT) + D5(SCK)");
  
  setupWiFi();
  setupWebServer();
  
  server.begin();
  Serial.println("Web-Server gestartet");
  Serial.print("Browser-Test: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/");
}

void setupWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  Serial.print("WiFi-Verbindung");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.print("WiFi OK! IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println();
    Serial.println("Station fehlgeschlagen -> Access Point");
    WiFi.mode(WIFI_AP);
    WiFi.softAP(ap_ssid, ap_password);
    Serial.print("AP: ");
    Serial.print(ap_ssid);
    Serial.print(" → http://");
    Serial.println(WiFi.softAPIP());
  }
}

void setupWebServer() {
  // Haupt-Test-Seite
  server.on("/", handleMainPage);
  
  // API-Endpunkte
  server.on("/test-hl", handleTestHL);
  server.on("/test-hr", handleTestHR);
  server.on("/test-both", handleTestBoth);
  server.on("/raw-data", handleRawData);
  server.on("/pin-check", handlePinCheck);
}

void handleMainPage() {
  String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>ESP8266 Dual-HX711 Tester</title>
    <meta charset='utf-8'>
    <style>
        body { font-family: Arial; margin: 20px; }
        .container { max-width: 800px; margin: auto; }
        .button { 
            background: #4CAF50; color: white; padding: 15px 25px; 
            border: none; border-radius: 5px; font-size: 16px; 
            margin: 10px 5px; cursor: pointer; 
        }
        .button:hover { background: #45a049; }
        .result { 
            background: #f9f9f9; padding: 15px; margin: 10px 0; 
            border-left: 4px solid #2196F3; font-family: monospace;
        }
        .error { border-left-color: #f44336; }
        .success { border-left-color: #4CAF50; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ESP8266 Dual-HX711 Web-Tester</h1>
        
        <h2>Hardware-Status</h2>
        <p><strong>HL (Links):</strong> D6(DT) + D7(SCK)</p>
        <p><strong>HR (Rechts):</strong> D8(DT) + D5(SCK)</p>
        
        <h2>Tests</h2>
        <button class="button" onclick="testHL()">Test HL (Links)</button>
        <button class="button" onclick="testHR()">Test HR (Rechts)</button>
        <button class="button" onclick="testBoth()">Test Beide</button>
        <button class="button" onclick="getRawData()">Raw-Daten</button>
        <button class="button" onclick="checkPins()">Pin-Check</button>
        
        <div id="result"></div>
        
        <h2>Diagnose-Checkliste</h2>
        <ul>
            <li>[OK] Beide HX711 auf 5V (VIN)</li>
            <li>[OK] GND gemeinsam verbunden</li>
            <li>[?] Waegezellen angeschlossen (E+/E-/A+/A-)?</li>
            <li>[?] Richtige Pin-Zuordnung D6/D7 und D8/D5?</li>
        </ul>
    </div>

    <script>
        function showResult(data, success = true) {
            const div = document.getElementById('result');
            div.className = 'result ' + (success ? 'success' : 'error');
            div.innerHTML = '<pre>' + data + '</pre>';
        }

        function testHL() {
            fetch('/test-hl')
                .then(response => response.text())
                .then(data => showResult('HL (Links) Test:\n' + data))
                .catch(err => showResult('Fehler: ' + err, false));
        }

        function testHR() {
            fetch('/test-hr')
                .then(response => response.text())
                .then(data => showResult('HR (Rechts) Test:\n' + data))
                .catch(err => showResult('Fehler: ' + err, false));
        }

        function testBoth() {
            fetch('/test-both')
                .then(response => response.text())
                .then(data => showResult('Beide HX711 Test:\n' + data))
                .catch(err => showResult('Fehler: ' + err, false));
        }

        function getRawData() {
            fetch('/raw-data')
                .then(response => response.text())
                .then(data => showResult('Raw-Daten:\n' + data))
                .catch(err => showResult('Fehler: ' + err, false));
        }

        function checkPins() {
            fetch('/pin-check')
                .then(response => response.text())
                .then(data => showResult('Pin-Status:\n' + data))
                .catch(err => showResult('Fehler: ' + err, false));
        }
    </script>
</body>
</html>
)";
  
  server.send(200, "text/html", html);
}

void handleTestHL() {
  String result = "HX711-HL (Links) Test\n";
  result += "========================\n";
  
  bool ready = scale_HL.is_ready();
  result += "Ready: " + String(ready ? "OK" : "NEIN") + "\n";
  
  if (ready) {
    long raw = scale_HL.read();
    result += "Raw-Wert: " + String(raw) + "\n";
    
    // 5 Messungen
    result += "\n📊 5 Messungen:\n";
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
    result += "Prüfe:\n";
    result += "- Stromversorgung 5V\n";
    result += "- Kabel D6→DT, D7→SCK\n";
    result += "- Wägezelle angeschlossen\n";
  }
  
  server.send(200, "text/plain", result);
}

void handleTestHR() {
  String result = "🔧 HX711-HR (Rechts) Test\n";
  result += "=========================\n";
  
  bool ready = scale_HR.is_ready();
  result += "Ready: " + String(ready ? "✅ JA" : "❌ NEIN") + "\n";
  
  if (ready) {
    long raw = scale_HR.read();
    result += "Raw-Wert: " + String(raw) + "\n";
    
    // 5 Messungen
    result += "\n📊 5 Messungen:\n";
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
    result += "❌ HX711-HR antwortet nicht!\n";
    result += "Prüfe:\n";
    result += "- Stromversorgung 5V\n";
    result += "- Kabel D8→DT, D5→SCK\n";
    result += "- Wägezelle angeschlossen\n";
  }
  
  server.send(200, "text/plain", result);
}

void handleTestBoth() {
  String result = "🔧 Dual-HX711 Test\n";
  result += "==================\n";
  
  bool hl_ready = scale_HL.is_ready();
  bool hr_ready = scale_HR.is_ready();
  
  result += "HL (Links):  " + String(hl_ready ? "✅ READY" : "❌ NOT READY") + "\n";
  result += "HR (Rechts): " + String(hr_ready ? "✅ READY" : "❌ NOT READY") + "\n";
  
  if (hl_ready || hr_ready) {
    result += "\n📊 Simultane Messungen:\n";
    
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
    result += "\n❌ BEIDE HX711 antworten nicht!\n";
    result += "Kritische Probleme:\n";
    result += "- Keine 5V Stromversorgung?\n";
    result += "- Falsche Pin-Verdrahtung?\n";
    result += "- Wägezellen nicht verbunden?\n";
  }
  
  server.send(200, "text/plain", result);
}

void handleRawData() {
  String result = "📊 Raw-Daten Analyse\n";
  result += "====================\n";
  
  // Pin-Zustände direkt lesen
  result += "Pin-Zustände:\n";
  result += "D6 (HL-DT):  " + String(digitalRead(HX711_HL_DT) ? "HIGH" : "LOW") + "\n";
  result += "D7 (HL-SCK): " + String(digitalRead(HX711_HL_SCK) ? "HIGH" : "LOW") + "\n";
  result += "D8 (HR-DT):  " + String(digitalRead(HX711_HR_DT) ? "HIGH" : "LOW") + "\n";
  result += "D5 (HR-SCK): " + String(digitalRead(HX711_HR_SCK) ? "HIGH" : "LOW") + "\n";
  
  result += "\nHX711 Status:\n";
  result += "HL Ready: " + String(scale_HL.is_ready() ? "JA" : "NEIN") + "\n";
  result += "HR Ready: " + String(scale_HR.is_ready() ? "JA" : "NEIN") + "\n";
  
  server.send(200, "text/plain", result);
}

void handlePinCheck() {
  String result = "📌 Pin-Konfiguration Check\n";
  result += "==========================\n";
  
  result += "Konfigurierte Pins:\n";
  result += "HX711-HL: D6(" + String(HX711_HL_DT) + ") + D7(" + String(HX711_HL_SCK) + ")\n";
  result += "HX711-HR: D8(" + String(HX711_HR_DT) + ") + D5(" + String(HX711_HR_SCK) + ")\n";
  
  result += "\nPin-Modi:\n";
  result += "D6: INPUT  (DT)\n";
  result += "D7: OUTPUT (SCK)\n";
  result += "D8: INPUT  (DT)\n";
  result += "D5: OUTPUT (SCK)\n";
  
  result += "\nVerkabelung sollte sein:\n";
  result += "ESP8266 → HX711-HL → ESP8266 → HX711-HR\n";
  result += "   D6   →    DT    →    D8   →    DT\n";
  result += "   D7   →   SCK    →    D5   →   SCK\n";
  result += "  VIN   →   VCC    →   VIN   →   VCC\n";
  result += "  GND   →   GND    →   GND   →   GND\n";
  
  server.send(200, "text/plain", result);
}

void loop() {
  server.handleClient();
  
  // Debug-Output alle 10 Sekunden
  static unsigned long lastDebug = 0;
  if (millis() - lastDebug > 10000) {
    lastDebug = millis();
    
    Serial.println("🔄 Status-Check:");
    Serial.println("  HL Ready: " + String(scale_HL.is_ready() ? "JA" : "NEIN"));
    Serial.println("  HR Ready: " + String(scale_HR.is_ready() ? "JA" : "NEIN"));
  }
}