# Kabel-Dimensionierung für 1,5m HX711-Verbindung

## 🔌 **Kabelquerschnitt-Berechnung:**

### ⚡ **Stromanalyse:**
```
4x HX711 @ 3.3V Gesamtstrom:
├── HX711_1: ~10mA
├── HX711_2: ~10mA  
├── HX711_3: ~10mA (hinten)
├── HX711_4: ~10mA (hinten)
└── Gesamt hinten: 20mA (nur 2x HX711 über das Kabel)
```

### 📏 **Spannungsabfall-Vergleich:**

#### **6x0,5mm² Kabel:**
```
Widerstand 0,5mm² bei 1,5m:
├── Spezifischer Widerstand: 0.0344 Ω/m
├── Hin + Rück: 1.5m × 2 × 0.0344 = 0.103Ω
├── Spannungsabfall: 20mA × 0.103Ω = 2.06mV
├── Spannung hinten: 3.300V - 0.002V = 3.298V
└── ✅ Perfekt! (HX711 braucht >2.7V)
```

#### **6x0,75mm² Kabel:**
```
Widerstand 0,75mm² bei 1,5m:
├── Spezifischer Widerstand: 0.0229 Ω/m  
├── Hin + Rück: 1.5m × 2 × 0.0229 = 0.069Ω
├── Spannungsabfall: 20mA × 0.069Ω = 1.38mV
├── Spannung hinten: 3.300V - 0.001V = 3.299V
└── ✅ Minimal besser, aber unnötig
```

---

## 🎯 **Empfehlung: 6x0,5mm² reicht perfekt!**

### **Warum 0,5mm² ausreicht:**
- ✅ Spannungsverlust nur 2mV (vernachlässigbar)
- ✅ HX711 bekommt 3.298V (weit über Minimum 2.7V)
- ✅ Günstiger als 0,75mm²
- ✅ Flexibler/dünner → einfachere Verlegung
- ✅ Standardgröße → besser verfügbar

### **0,75mm² nur sinnvoll bei:**
- Kabellängen >3m
- Höheren Strömen (>50mA)
- Extrem kritischen Anwendungen

---

## 🛒 **Konkrete Kabel-Empfehlung:**

### **6x0,5mm² geschirmtes Kabel:**
```
🔌 Kabelspezifikation:
├── 6 Adern × 0.5mm² (AWG 20)
├── Geschirmt (Aluminiumfolie + Geflechtschirm)
├── Länge: 2m (Reserve für Anschlüsse)
├── Flexibel/Litze (nicht starrer Draht)
├── Mantel: PVC oder TPE (wetterbeständig)
└── Preis: ~12-15€

Ader-Belegung:
├── Rot:    +3.3V (dickste Ader für Strom)
├── Schwarz: GND (dickste Ader für Strom)
├── Blau:   CLK3 (HX711_3)
├── Grün:   DT3  (HX711_3)  
├── Gelb:   CLK4 (HX711_4)
├── Weiß:   DT4  (HX711_4)
└── Schirm: An GND (Störschutz)
```

### **Alternative - Einzeladern:**
```
Falls geschirmtes 6x0,5 nicht verfügbar:
├── 2x 0.75mm² für Strom (+3.3V, GND)
├── 4x 0.25mm² für Signale (CLK, DT)
├── Verdrillte Paare bilden
├── Alu-Folie als Schirmung
└── Gesamtpreis: ~10€
```

---

## 📊 **Preis-Leistungs-Vergleich:**

| Kabeltyp | Preis | Spannungsabfall | Verfügbarkeit | Empfehlung |
|----------|-------|-----------------|---------------|------------|
| 6x0,5mm² | 12€ | 2.06mV | ✅ Standard | ⭐⭐⭐⭐⭐ |
| 6x0,75mm² | 18€ | 1.38mV | ⚠️ Seltener | ⭐⭐⭐ |
| Einzeladern | 10€ | 1-3mV | ✅ Überall | ⭐⭐⭐⭐ |

---

## 🔧 **Praktische Montage:**

### **Anschluss-Schema:**
```
ESP8266 Seite:           Kabel (1.5m):          HX711 Seite:
├── D5 (GPIO14) ─────────── Blau ──────────── HX711_3 CLK
├── D6 (GPIO12) ─────────── Grün ──────────── HX711_3 DT
├── D7 (GPIO13) ─────────── Gelb ──────────── HX711_4 CLK  
├── D8 (GPIO15) ─────────── Weiß ──────────── HX711_4 DT
├── 3.3V ───────────────── Rot (0.5mm²) ──── HX711 VCC
├── GND ────────────────── Schwarz (0.5mm²) ─ HX711 GND
└── Schirm ─────────────── An GND beidseitig
```

### **Steckverbinder:**
```
🔌 JST-Stecker 6-polig:
├── Wasserdicht IP65
├── Verriegelung gegen Herausrutschen  
├── Farbkodierte Kontakte
└── Preis: ~8€ pro Paar
```

---

## 🎯 **Finale Kabel-Empfehlung:**

### **6x0,5mm² geschirmtes Kabel + JST-Stecker**

**Warum perfekt:**
- ✅ Ausreichender Querschnitt (2mV Verlust)
- ✅ Standard-Größe → günstig & verfügbar
- ✅ Geschirmt → störungsfrei
- ✅ Flexibel → einfache Montage
- ✅ Wasserdichte Stecker → wetterfest

**Gesamtkosten: ~20€** (Kabel + Stecker)

**0,75mm² wäre Overkill** für diese Anwendung! 🎯

Soll ich konkrete Produktlinks raussuchen? 🛒