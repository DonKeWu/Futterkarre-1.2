# ESP8266 Spannungsversorgung für verteilte HX711 Module

## ⚡ Problem: 1,5m Spannungsversorgung für HX711

### 🔍 Technische Analyse:

**ESP8266 3.3V Ausgang:**
- Max. Strom: ~200mA
- Innenwiderstand: ~1Ω
- Spannung bei Last: 3.1-3.2V

**4x HX711 Stromverbrauch:**
- Je HX711: ~10mA (aktiv)  
- Gesamt: ~40mA
- ✅ Strom OK, aber...

**Spannungsabfall bei 1,5m Kabel:**
```
Draht 0.5mm² (24AWG): ~0.034Ω/m
Bei 1,5m: 0.05Ω Widerstand
Bei 40mA: 0.05Ω × 0.04A = 2mV Verlust
→ Noch OK bei kurzen Kabeln
```

**ABER: HX711 braucht stabile 2.7-5.5V**
- Bei 3.3V System: Wenig Reserve
- Längere Kabel = mehr Störungen
- Spannungsschwankungen = Messfehler

---

## 🎯 Empfohlene Lösung: Lokale 5V Versorgung

### **Option 1: 5V Rail mit LM2596 Step-Down (Empfohlung)**

```
18650 Akku (3.7-4.2V) → LM2596 → 5V Rail → Verteilung
                     ↓
                ESP8266 (3.3V)
                     ↓  
         HX711 vorne (5V) + HX711 hinten (5V)
```

**Hardware:**
- LM2596S DC-DC Step-Up Modul (3€)
- Input: 3.7-4.2V (18650)
- Output: 5V/1A
- Effizienz: 92%
- Geringe Größe: 43×21×14mm

**Vorteile:**
- ✅ Stabile 5V für alle HX711 
- ✅ Bessere Störfestigkeit
- ✅ Längere Kabel möglich (1,5m kein Problem)
- ✅ Höhere Genauigkeit
- ✅ ESP8266 läuft trotzdem mit 3.3V

---

### **Option 2: Lokale 3.3V Regler an beiden Enden**

```
Akku → ESP8266 (3.3V) ─┬─ 5V Rail (über Boost)
                       │
     ┌─────────────────┼─────────────────┐
     │                 │                 │
   HX711 #1+2      Local 3.3V       HX711 #3+4
   (vorne)         Regulator         (hinten)
                   AMS1117
```

**Hardware pro Standort:**
- AMS1117-3.3 Regulator (1€)
- Input: 5V Rail
- Output: 3.3V/800mA (reicht für 2x HX711)

---

### **Option 3: 5V direkt vom Akku (mit TP4056 Boost)**

```
18650 → TP4056 + Boost → 5V Rail → Verteilung
                       ↓
                   ESP8266 (mit 3.3V Regler)
                       ↓
              HX711 Module (alle 5V)
```

**Hardware:**
- TP4056 + MT3608 Boost Kombination (5€)
- Stabile 5V aus 18650
- Separate 3.3V für ESP8266

---

## 📐 Praktische Verkabelung:

### **Pin-Anpassung für geteilte HX711:**

```cpp
// ESP8266 NodeMCU Pin-Mapping (überarbeitet)
// Vorne (näher zum ESP8266):
#define HX711_1_CLK  5   // D1 → HX711 vorne-links
#define HX711_1_DT   4   // D2 → HX711 vorne-links
#define HX711_2_CLK  0   // D3 → HX711 vorne-rechts  
#define HX711_2_DT   2   // D4 → HX711 vorne-rechts

// Hinten (1,5m Kabel):
#define HX711_3_CLK  14  // D5 → HX711 hinten-links (1,5m)
#define HX711_3_DT   12  // D6 → HX711 hinten-links (1,5m)
#define HX711_4_CLK  13  // D7 → HX711 hinten-rechts (1,5m)
#define HX711_4_DT   15  // D8 → HX711 hinten-rechts (1,5m)

// Spannungsversorgung:
// 5V Rail → beide Standorte
// GND → gemeinsame Masse
```

### **Kabel-Dimensionen für 1,5m:**

**Signalleitungen (CLK/DT):**
- 0.25mm² (28AWG) reicht
- Geschirmtes Kabel empfohlen
- Max. Frequenz: 10MHz (HX711 = 10Hz → kein Problem)

**Spannungsversorgung:**
- 0.75mm² (20AWG) für 5V Rail
- Dickeres Kabel = weniger Verlust
- Verdrillte Leitungen gegen Störungen

---

## 🛒 Shopping-Liste Ergänzung:

```
Spannungsversorgung für verteilte HX711:
├── LM2596S Step-Up Modul (3.7V→5V)     ~3€
├── 2x AMS1117-3.3V Regulator           ~2€  
├── 0.75mm² Kabel für 5V (3m)           ~5€
├── 0.25mm² geschirmtes Kabel (6m)      ~8€
├── Steckverbinder wasserdicht          ~10€
└── Zusatzkosten: ~28€

Neue Gesamtsumme: 110€ + 28€ = ~138€
```

---

## ⚡ Stromverbrauch-Analyse:

**Mit 5V Rail System:**
```
LM2596 Effizienz: 92%
4x HX711 @ 5V: 4 × 15mA = 60mA
ESP8266 @ 3.3V: 80mA
Gesamt: 140mA @ 5V = ~180mA @ 3.7V

18650 3000mAh: 3000/180 = ~17h Laufzeit
Mit Deep Sleep (50% duty): ~34h Laufzeit
```

**Vs. direkte 3.3V Versorgung:**
```
ESP8266 + 4x HX711 @ 3.3V: ~120mA
18650 direkt: 3000/120 = 25h
Aber: Spannungsprobleme bei langen Kabeln!
```

---

## 🎯 Empfehlung:

### **Beste Lösung: LM2596 + 5V Rail**

1. **LM2596S Boost-Modul** (18650 → 5V)
2. **5V Rail zu beiden HX711-Gruppen**
3. **ESP8266 mit eigenem 3.3V Regler**
4. **Geschirmte Kabel für 1,5m Signale**

**Vorteile:**
- ✅ Stabile, störfreie 5V Versorgung
- ✅ 1,5m Kabel kein Problem
- ✅ Bessere Messgenauigkeit
- ✅ Zukunftssicher für längere Distanzen
- ✅ Nur 28€ Mehrkosten

**Das System wird stabiler und genauer!** 📏⚡

---

## 🔧 Code-Anpassungen:

**Keine Änderungen nötig!** Der ESP8266-Code funktioniert identisch, nur die Hardware-Versorgung ändert sich.

Soll ich die detaillierte Schaltplan-Skizze für die 5V-Rail-Lösung erstellen?