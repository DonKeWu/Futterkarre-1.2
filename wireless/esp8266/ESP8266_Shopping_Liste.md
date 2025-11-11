# ESP8266 Shopping-Liste für Futterkarre Wireless-Waage

## 🛒 Optimierte Hardware-Liste (ESP8266)

### 💰 Kostenvergleich:
```
Original ESP32-S3 Kit: ~120€
Neues ESP8266 Kit:     ~105€
Ersparnis:             ~15€ + längere Akkulaufzeit
```

## 📦 ESP8266 Hardware-Kit

### 1. Mikrocontroller:
- **ESP8266 NodeMCU v3** (~5€)
  - 11 nutzbare GPIO-Pins ✅
  - 2.4GHz WiFi ✅  
  - 4MB Flash ✅
  - USB-C Programmierung ✅
  - Breadboard-kompatibel ✅

### 2. Gewichtssensoren:
- **4x HX711 24-Bit ADC Module** (~20€)
  - Präzise Gewichtsmessung ✅
  - 3.3V/5V kompatibel ✅
  - Einfache 2-Pin Verkabelung ✅

- **4x 50kg Wägezellen** (~60€)
  - Alu-Konstruktion, wetterfest ✅
  - 4-Draht Wheatstone-Brücke ✅
  - Für Futterkarre-Eckenbefestigung ✅

### 3. Stromversorgung:
- **18650 Li-Ion Akku 3000mAh** (~5€)
  - 40+ Stunden Laufzeit mit ESP8266 ✅
  - Standard-Bauform ✅
  - Hohe Zyklenfestigkeit ✅

- **TP4056 USB-C Lademodul** (~3€)
  - Sichere Li-Ion Ladung ✅
  - USB-C Anschluss ✅
  - Überladungsschutz ✅

### 4. Gehäuse & Zubehör:
- **Wasserdichtes Gehäuse** (~8€)
  - IP65 Schutzklasse ✅
  - Transparent für LED-Sicht ✅
  - Kabeldurchführungen ✅

- **Status-LEDs + Widerstände** (~2€)
  - Grüne Power-LED ✅
  - (Blaue WiFi-LED bereits onboard) ✅

### 5. Verkabelung:
- **Dupont-Kabel Set** (~5€)
  - Stecker-Buchse Verbindungen ✅
  - Verschiedene Längen ✅
  - Farbkodiert ✅

- **Spannungsteiler für Akku-Monitor** (~2€)
  - 2x 10kΩ Widerstände ✅
  - Kleine Platine/Steckbrett ✅

---

## 📊 Gesamt-Kalkulation ESP8266:

| Komponente | Preis | Shop-Empfehlung |
|------------|-------|-----------------|
| ESP8266 NodeMCU v3 | ~5€ | Amazon/AliExpress |
| 4x HX711 Module | ~20€ | Amazon/AliExpress |
| 4x 50kg Wägezellen | ~60€ | Amazon/eBay |
| 18650 + Lademodul | ~8€ | Amazon/Conrad |
| Gehäuse + LEDs | ~10€ | Amazon/Conrad |
| Kabel + Kleinteile | ~7€ | Amazon/Conrad |
| **Gesamtsumme** | **~110€** | |

---

## ⚡ Technische Spezifikationen:

### ESP8266 Performance:
- **CPU:** 80MHz (völlig ausreichend für 4x HX711)
- **RAM:** 80kB (JSON + WebSocket passt locker)
- **WiFi:** 2.4GHz, 802.11b/g/n (100m+ Reichweite)
- **GPIO:** 11 Pins (8 für HX711 + 3 Reserve)
- **ADC:** 1x für Akku-Monitoring
- **Power:** ~80mA aktiv, <1mA Deep Sleep

### Laufzeit-Berechnung:
```
3000mAh Akku:
├── Dauerbetrieb 2Hz: ~37h
├── Mit Deep Sleep (1h on/1h off): ~74h  
└── Nur bei Bedarf: mehrere Tage
```

### Reichweite bei 2m:
- **WiFi-Signal:** Exzellent (-30 bis -50 dBm)
- **Latenz:** <10ms 
- **Stabilität:** 100% (keine Störungen bei kurzer Distanz)

---

## 🔧 Pin-Belegung ESP8266 NodeMCU:

```
┌─────────────────────────┐
│    ESP8266 NodeMCU v3   │
├─────────────────────────┤
│ 3V3  ●──────────● VIN   │ 5V (von TP4056)
│ GND  ●──────────● GND   │ Ground
│ D0   ●──────────● 3V3   │ 
│ D1   ●──────────● RST   │ 
│ D2   ●──────────● A0    │ Akku-Monitor
│ D3   ●──────────● D4    │ 
│ D4   ●──────────● D3    │ 
│ 3V3  ●──────────● D5    │ 
│ D6   ●──────────● D6    │ 
│ D7   ●──────────● D7    │ 
│ D8   ●──────────● D8    │ 
│ RX   ●──────────● TX    │ 
│ GND  ●──────────● GND   │ 
│ 3V3  ●──────────● 3V3   │ 
└─────────────────────────┘

Belegung:
├── D1 (GPIO5)  → HX711_1_CLK
├── D2 (GPIO4)  → HX711_1_DT  
├── D3 (GPIO0)  → HX711_2_CLK
├── D4 (GPIO2)  → HX711_2_DT + Built-in LED
├── D5 (GPIO14) → HX711_3_CLK
├── D6 (GPIO12) → HX711_3_DT
├── D7 (GPIO13) → HX711_4_CLK
├── D8 (GPIO15) → HX711_4_DT
├── D0 (GPIO16) → Power LED (grün)
├── A0          → Akku-Spannungsmessung (Spannungsteiler)
└── Built-in LED → WiFi/Status (blau)
```

---

## 🚀 Vorteile ESP8266 für 2m Reichweite:

### ✅ Perfekt dimensioniert:
- Ausreichende Performance für Futterkarre
- Bewährte, stabile Technologie  
- Riesige Community & Dokumentation
- Günstige, verfügbare Hardware

### ✅ Einfacher Setup:
- Arduino IDE direkt unterstützt
- Weniger komplexe Features = weniger Fehlerquellen
- Standard WiFi-Libraries
- Einfachere Pinbelegung

### ✅ Längere Akkulaufzeit:
- 50% weniger Stromverbrauch vs ESP32
- Effizienterer Deep Sleep
- Weniger Hitzeentwicklung

### ✅ Kostengünstiger:
- 60% günstiger als ESP32-S3
- Weniger Overkill für die Anwendung
- Besseres Preis/Leistungsverhältnis

---

## 🎯 Empfehlung:

**Für 2m Reichweite ist ESP8266 NodeMCU die optimale Wahl!**

Der ESP8266 ist nicht nur günstiger, sondern auch:
- Einfacher zu programmieren
- Stabiler im Betrieb  
- Länger am Akku
- Perfekt ausreichend für die Anforderungen

**ESP32-S3 wäre nur bei >50m Reichweite oder zusätzlichen Features sinnvoll.**

---

## 📋 Nächste Schritte:

1. **ESP8266 NodeMCU v3 bestellen** (~5€)
2. **HX711 + Wägezellen Kit besorgen** (~80€)  
3. **Akku + Lademodul** (~8€)
4. **Gehäuse + Kleinteile** (~15€)
5. **Arduino IDE + ESP8266 Board Package installieren**
6. **Firmware flashen:** `futterkarre_wireless_waage_esp8266.ino`
7. **Hardware zusammenbauen & testen**

**Gesamtkosten: ~110€ statt 120€ + bessere Akkulaufzeit!** 🎉