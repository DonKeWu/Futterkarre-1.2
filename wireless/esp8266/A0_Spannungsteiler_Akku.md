# ESP8266 A0 Spannungsteiler für Akku-Monitoring

## 🔋 **Spannungsteiler-Zweck: 18650 Akku-Überwachung**

### ⚡ **Problem:**
```
18650 Li-Ion Akku: 3.0V - 4.2V (Entladen bis Voll)
ESP8266 A0 (ADC):   0V - 3.3V max!

Bei 4.2V Akku → ESP8266 A0 würde beschädigt! ⚠️
```

### 🔧 **Lösung: Spannungsteiler 4.2V → 3.0V**

```
18650 Akku (3.0V - 4.2V)
    │
    ├── R1: 10kΩ ──┐
    │               │
    └── R2: 22kΩ ──┼── A0 (ESP8266)
                    │
                   GND

Teilerverhältnis: 22k/(10k+22k) = 22/32 = 0.69

Ausgangsspannungen:
├── Akku leer (3.0V):  3.0V × 0.69 = 2.07V → A0
├── Akku normal (3.7V): 3.7V × 0.69 = 2.55V → A0  
├── Akku voll (4.2V):  4.2V × 0.69 = 2.90V → A0
└── Alle Werte < 3.3V → ESP8266 sicher! ✅
```

---

## 📊 **Spannungsteiler-Berechnung:**

### **Widerstandswerte:**
```
🔧 Standard-Lösung (2:1 Teiler):
├── R1: 10kΩ (oben, zu +Akku)
├── R2: 10kΩ (unten, zu GND)  
├── Teilerverhältnis: 0.5
└── Max. Eingangsspannung: 3.3V × 2 = 6.6V

Ausgangsspannungen bei 2:1:
├── Akku leer (3.0V):  1.50V → A0
├── Akku normal (3.7V): 1.85V → A0
├── Akku voll (4.2V):  2.10V → A0  
└── Sicherer Bereich! ✅
```

### **Optimierte Lösung (für bessere Auflösung):**
```
🎯 Bessere Ausnutzung des A0-Bereichs:
├── R1: 4.7kΩ (oben)
├── R2: 10kΩ (unten)
├── Teilerverhältnis: 10/(4.7+10) = 0.68
└── Max. sicher: 3.3V / 0.68 = 4.85V

Ausgangsspannungen optimiert:
├── Akku leer (3.0V):  2.04V → A0 
├── Akku normal (3.7V): 2.52V → A0
├── Akku voll (4.2V):  2.86V → A0
└── Nutzt A0-Bereich besser aus! 📈
```

---

## 🔧 **Arduino Code für Akku-Monitoring:**

```cpp
// Akku-Spannungsmessung mit Spannungsteiler
void checkBattery() {
  // ADC lesen (0-1024 entspricht 0-3.3V)
  int adc_value = analogRead(A0);
  
  // Spannung am A0-Pin berechnen
  float voltage_a0 = (adc_value / 1024.0) * 3.3;
  
  // Echte Akku-Spannung zurückrechnen (Spannungsteiler 2:1)
  battery_voltage = voltage_a0 * 2.0;
  
  // Oder bei optimiertem Teiler (0.68):
  // battery_voltage = voltage_a0 / 0.68;
  
  // Akku-Status bewerten
  if (battery_voltage > 4.0) {
    Serial.println("🔋 Akku voll");
  } else if (battery_voltage > 3.6) {
    Serial.println("🔋 Akku OK");  
  } else if (battery_voltage > 3.2) {
    Serial.println("🔋 Akku schwach");
  } else {
    Serial.println("🔋 Akku kritisch!");
    // Deep Sleep oder Warnung
  }
}
```

---

## 🛒 **Bauteile für Spannungsteiler:**

### **Einfache 2:1 Lösung:**
```
🔧 Bauteile:
├── 2x 10kΩ Widerstände (1/4W)    ~0.50€
├── Kleine Lochrasterplatine       ~1.00€  
├── Stiftleisten/Anschlüsse       ~0.50€
└── Gesamt: ~2€

Vorteile: Standard-Werte, einfach zu rechnen
```

### **Optimierte Lösung:**
```
🎯 Bauteile:  
├── 1x 4.7kΩ Widerstand           ~0.25€
├── 1x 10kΩ Widerstand            ~0.25€
├── Kleine Lochrasterplatine      ~1.00€
├── Stiftleisten/Anschlüsse       ~0.50€  
└── Gesamt: ~2€

Vorteile: Bessere ADC-Auflösung
```

---

## ⚠️ **Wichtige Hinweise:**

### **Nicht direkt 5V an A0!**
- ESP8266 A0 verträgt max. 3.3V
- 5V würde den ADC beschädigen
- Immer Spannungsteiler verwenden

### **Hochohmige Widerstände:**
- 10kΩ+ verwenden (geringer Stromverbrauch)
- Niedrigere Werte = mehr Akkuverbrauch
- Zu hohe Werte = ADC-Ungenauigkeit

### **Kalibrierung:**
```cpp
// Spannungsteiler-Kalibrierung im Code:
float VOLTAGE_DIVIDER = 2.0;  // 2:1 Teiler
// oder
float VOLTAGE_DIVIDER = 1.47; // 4.7k + 10k Teiler

battery_voltage = voltage_a0 * VOLTAGE_DIVIDER;
```

---

## 🎯 **Empfehlung:**

### **2:1 Spannungsteiler (2x 10kΩ) - Einfach & Sicher**

**Warum diese Lösung:**
- ✅ Einfache Berechnung (× 2)
- ✅ Standard-Bauteile verfügbar  
- ✅ Sicher für Akku-Bereich 3.0-4.2V
- ✅ Geringer Stromverbrauch (~0.2mA)
- ✅ Nur 2€ Zusatzkosten

**Anschluss:**
```
18650 (+) ─── 10kΩ ─── A0 (ESP8266) ─── 10kΩ ─── GND
```

Das hat **nichts mit 5V zu tun** - nur Akku-Überwachung! 🔋