# HX711 Spannungsversorgung: 3.3V vs 5V Klarstellung

## 🔍 **HX711 Spezifikationen - Wichtige Korrektur:**

### ⚡ **HX711 Spannungsbereich:**
```
Offizieller Spannungsbereich: 2.7V - 5.5V
├── 2.7V: Minimum (funktioniert, aber nicht optimal)
├── 3.3V: Standard für ESP8266/ESP32 ✅
├── 5.0V: Optimal für beste Performance ✅
└── 5.5V: Maximum (nicht überschreiten!)
```

### 📊 **Performance-Vergleich 3.3V vs 5V:**

| Aspekt | @ 3.3V | @ 5V | Unterschied |
|--------|--------|------|-------------|
| **Funktionsfähigkeit** | ✅ Voll | ✅ Voll | Beide OK |
| **Genauigkeit** | 24-Bit | 24-Bit | Gleich |
| **Stabilität** | Gut | Besser | 5V rauschärmer |
| **Stromverbrauch** | ~10mA | ~15mA | +50% bei 5V |
| **Messrate** | 10/80Hz | 10/80Hz | Gleich |
| **Störfestigkeit** | OK | Besser | Höhere Spannung = weniger empfindlich |

## 🎯 **Fazit: 3.3V reicht völlig aus!**

### ✅ **3.3V Lösung ist ausreichend:**
- HX711 funktioniert einwandfrei bei 3.3V
- 24-Bit Auflösung bleibt voll erhalten
- Genauigkeit für Futterkarre-Anwendung perfekt
- **Einfacher und günstiger!**

### ⚠️ **5V nur sinnvoll bei:**
- Sehr langen Kabeln (>3m)
- Extrem störender Umgebung (Motoren, etc.)
- Höchste Präzision erforderlich (Labor-Anwendung)

---

## 🔧 **Vereinfachte Lösungen für 1,5m Kabel:**

### **Option A: Direkte 3.3V (Einfachste Lösung)**
```
ESP8266 3.3V → 1,5m Kabel → HX711 hinten
├── Kabel: 0.5mm² (dickeres Kabel gegen Spannungsabfall)
├── Spannungsabfall: ~50mV (vernachlässigbar)
├── Kosten: +15€ (nur dickeres Kabel)
└── Funktioniert einwandfrei! ✅
```

### **Option B: 5V Rail (Premium-Lösung)**
```
18650 → LM2596 → 5V → lokale 3.3V Regler
├── Beste Störfestigkeit
├── Höchste Stabilität  
├── Kosten: +34€
└── Professioneller Standard ✅
```

### **Option C: Power Bank USB (Pragmatisch)**
```
5V USB Power Bank → beide HX711-Gruppen
├── ESP8266: eigene 3.3V
├── HX711: 5V vom USB
├── Kosten: +20€ (Power Bank + Kabel)
└── Sehr einfach! ✅
```

---

## 💡 **Neue Empfehlung für 1,5m:**

### **Einfachste Lösung: Dickeres 3.3V Kabel**

**Warum das reicht:**
```
Spannungsabfall-Rechnung (realistisch):
├── 1,5m Kabel 0.5mm² (20AWG)
├── 4x HX711 = 40mA Strom
├── Widerstand: 1.5m × 0.034Ω/m × 2 = 0.1Ω
├── Spannungsabfall: 0.04A × 0.1Ω = 4mV
└── Spannung hinten: 3.3V - 0.004V = 3.296V ✅

HX711 braucht minimum 2.7V → 3.296V ist perfekt!
```

**Shopping-Liste vereinfacht:**
```
🛒 3.3V Direkt-Lösung:
├── ESP8266 NodeMCU Kit: 110€ (wie geplant)
├── 6-adriges Kabel 0.5mm² 2m: 15€
├── Wasserdichte Stecker: 8€
└── Gesamt: 133€ (statt 144€)

Ersparnis: 11€ + viel einfacher! 🎉
```

---

## 🎯 **Korrigierte Empfehlung:**

### **Für 2m Reichweite + 1,5m HX711-Trennung:**

**Beste Lösung: ESP8266 + direkte 3.3V Versorgung**
- ✅ HX711 läuft einwandfrei bei 3.3V
- ✅ Dickeres Kabel (0.5mm²) verhindert Spannungsabfall  
- ✅ 23€ günstiger als 5V-Lösung
- ✅ Einfacher Aufbau, weniger Fehlerquellen
- ✅ Perfekt ausreichend für Futterkarre-Genauigkeit

**5V-Lösung nur nötig bei:**
- Kabellängen >3m  
- Extrem störende Umgebung
- Labor-Präzision erforderlich

---

## 🔧 **Vereinfachter Schaltplan:**

```
18650 Akku → TP4056 → ESP8266 (3.3V)
                         ├─→ HX711_1+2 (vorne, kurz)
                         └─→ 1.5m Kabel (0.5mm²) → HX711_3+4 (hinten)

Kabel-Inhalt:
├── CLK3, DT3, CLK4, DT4 (Signale)
├── +3.3V (dickerer Draht)
└── GND (dickerer Draht + Schirm)
```

**Viel einfacher und günstiger!** 🎉

Soll ich die Shopping-Liste entsprechend anpassen?