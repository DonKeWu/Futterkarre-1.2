/*
  Arduino Uno als ESP8266 Serial Monitor Bridge
  
  1. Diesen leeren Sketch auf Arduino Uno hochladen
  2. Arduino mit PC per USB verbinden  
  3. ESP8266 an Arduino anschließen:
     - Arduino GND → ESP8266 GND
     - Arduino Pin 0 (RX) → ESP8266 TX (GPIO1)
     - Arduino Pin 1 (TX) → ESP8266 RX (GPIO3)
  4. Arduino IDE: Serial Monitor 115200 Baud öffnen
  
  Der Arduino fungiert dann als "USB-zu-Serial Brücke"
*/

void setup() {
  // Nichts zu tun - Arduino ist nur Serial Bridge
}

void loop() {
  // Nichts zu tun - Arduino ist nur Serial Bridge
}