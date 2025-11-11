# Detaillierte Hardware-Lösung für verteilte HX711

## 🎯 Problem gelöst: 1,5m HX711-Trennung mit stabiler Versorgung

### ⚡ **Empfohlene Lösung: LM2596 + 5V Rail System**

## 📦 Ergänzte Shopping-Liste:

### **Spannungsversorgung Komponenten:**
```
🔋 Stromversorgung:
├── LM2596S DC-DC Boost Modul        ~3€
│   ├── Input: 3.0-40V (18650 OK)
│   ├── Output: 1.25-35V einstellbar → 5.0V
│   ├── Max Strom: 3A (wir brauchen 0.1A)
│   └── Effizienz: 92% (sehr gut)
│
├── 2x AMS1117-3.3V Regulator        ~2€
│   ├── Input: 4.5-15V (5V Rail OK)
│   ├── Output: 3.3V/800mA
│   ├── Für lokale HX711 Versorgung
│   └── Sehr stabil und rauscharm
│
└── Spannungsteiler für Akku-Monitor ~1€
    ├── 2x 10kΩ Widerstände
    └── Kleine Platine/Steckbrett

💡 Zusatzkosten: nur 6€!
```

### **Kabel für 1,5m Entfernung:**
```
🔌 Verkabelung:
├── 6-adriges geschirmtes Kabel 2m   ~12€
│   ├── 4x Signal: CLK3,DT3,CLK4,DT4
│   ├── 1x GND (gemeinsame Masse)
│   └── 1x Schirmung (Störschutz)
│
├── 2-adriges Stromkabel 2m (0.75mm²) ~8€
│   ├── +5V Rail Versorgung
│   └── GND Rückleitung
│
└── JST wasserdichte Stecker Set     ~8€
    ├── 6-polig für Signale
    ├── 2-polig für Strom
    └── IP65 Schutzklasse

🔌 Kabel-Zusatzkosten: 28€
```

### **Neue Gesamtkalkulation:**
```
Basis ESP8266 Kit:              110€
+ Spannungsversorgung:           +6€  
+ 1,5m Kabel-System:           +28€
─────────────────────────────────────
Gesamt:                        144€

Vs. ESP32 System:              120€ (aber ohne Kabel-Lösung)
→ Nur 24€ Aufpreis für professionelle Lösung!
```

---

## ⚙️ **Hardware-Aufbau Schritt-für-Schritt:**

### **1. Zentrale Stromversorgung (am ESP8266):**
```
18650 Akku (3.7-4.2V)
    ↓
TP4056 USB-C Lademodul  
    ↓
LM2596S Boost → 5.0V eingestellt
    ↓
5V Rail (Verteilung)
    ├─→ ESP8266 (eigener 3.3V Regler)
    ├─→ AMS1117 #1 (vorne) → HX711_1+2
    └─→ AMS1117 #2 (hinten, 1.5m) → HX711_3+4
```

### **2. Vordere HX711-Gruppe (am ESP8266):**
```
ESP8266 NodeMCU:
├── D1,D2 → HX711_1 (vorne-links)   [10cm Kabel]
├── D3,D4 → HX711_2 (vorne-rechts)  [10cm Kabel]
└── 5V Rail → AMS1117 → 3.3V lokal
```

### **3. Hintere HX711-Gruppe (1,5m entfernt):**
```
Kabel-Strang (1.5m):
├── CLK3 (D5) ═══════════════→ HX711_3 CLK
├── DT3  (D6) ═══════════════→ HX711_3 DT
├── CLK4 (D7) ═══════════════→ HX711_4 CLK  
├── DT4  (D8) ═══════════════→ HX711_4 DT
├── GND       ═══════════════→ Gemeinsame Masse
└── +5V       ═══════════════→ AMS1117 → 3.3V lokal
```

---

## 🔧 **Praktische Montage:**

### **ESP8266 Zentrale (Steuerbox):**
```
┌─────────────────────────────┐
│  [18650] [TP4056] [LM2596] │ Akku + Boost
│                             │
│  [ESP8266 NodeMCU]         │ Hauptcontroller  
│                             │
│  [AMS1117] [HX711] [HX711] │ Vordere Waagen
│                             │
│  [JST Stecker] ════════════┼══ Kabel zu hinten
└─────────────────────────────┘
     Wasserdichtes Gehäuse
```

### **Hintere HX711-Box (1,5m entfernt):**
```
┌─────────────────────────────┐
│ ═══[JST Buchse]═══         │ Kabel von vorne
│                             │
│  [AMS1117] [HX711] [HX711] │ Hintere Waagen
│                             │  
│  Wägezellen-Anschlüsse     │ Zu den Sensoren
└─────────────────────────────┘
     Wasserdichtes Gehäuse
```

---

## 📊 **Elektrische Stabilität:**

### **Spannungsabfall-Berechnung:**
```
1,5m Kabel 0.75mm² bei 100mA (5V Rail):
Widerstand: 1.5m × 0.023Ω/m × 2 = 0.07Ω
Spannungsabfall: 0.1A × 0.07Ω = 7mV
Spannung hinten: 5.0V - 0.007V = 4.993V
→ Vernachlässigbar! ✅

Nach AMS1117: 4.993V → 3.300V (geregelt)
→ Perfekt stabil für HX711! ✅
```

### **Störungsunterdrückung:**
```
Geschirmtes Kabel für Signale:
├── Schirm an GND → Störungen ableiten
├── Verdrillte Paare → Gleichtaktunterdrückung  
└── Kurze Signallaufzeiten → Keine Probleme bei 10Hz HX711
```

---

## 🎯 **Vorteile dieser Lösung:**

### ✅ **Elektrisch perfekt:**
- Stabile 5V → bessere HX711-Performance
- Lokale 3.3V Regelung → keine Spannungsabfälle
- Geschirmte Signale → störungsfrei
- Gemeinsame Masse → keine Potentialunterschiede

### ✅ **Mechanisch robust:**
- Wasserdichte Stecker
- Flexible Kabel-Längen
- Modularer Aufbau  
- Einfache Wartung

### ✅ **Kostengünstig:**
- Nur 34€ Aufpreis für komplette Kabel-Lösung
- Standard-Komponenten verfügbar
- Keine teuren Spezial-HX711 nötig

### ✅ **Zukunftssicher:**
- 5V Rail kann mehr HX711 versorgen
- Kabel-System erweiterbar
- Höhere Genauigkeit durch stabilere Versorgung

---

## 🚀 **Fazit:**

**Die LM2596 + 5V Rail Lösung ist perfekt für Ihre Anforderung!**

- Problemlos 1,5m Kabel-Trennung
- Stabile, störungsfreie Versorgung  
- Nur 34€ Mehrkosten
- Professionelle, erweiterbare Lösung

**Der ESP8266 Arduino-Code bleibt unverändert** - nur die Hardware wird optimiert! 

**Bereit für Bestellung der Zusatz-Komponenten?** 🛒⚡