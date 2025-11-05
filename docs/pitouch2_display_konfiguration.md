# PiTouch2 Display-Konfiguration - Futterkarre Projekt

## 🖥️ Hardware-Spezifikationen

### **PiTouch2 Display:**
- **Native Auflösung:** 1280x720 Pixel
- **Touchscreen:** Kapazitiv, Multi-Touch
- **Anschluss:** DSI (Direct Serial Interface)
- **Raspberry Pi:** Kompatibel mit RPi 4/5

## 📐 Fenster-Konfiguration

### **Raspberry Pi Desktop-Layout:**
```
┌─────────────────────────────────────┐ ← Y: 0
│     Raspberry Pi Statusleiste       │ ← Höhe: 60px
│  🍇 [WiFi] [Bluetooth] [Zeit] [Menü] │ ← (Logo + System-Icons)
├─────────────────────────────────────┤ ← Y: 60
│                                     │
│        Futterkarre-Anwendung        │ ← Höhe: 660px
│           (1280x660)                │ ← (720 - 60 = 660)
│                                     │
│                                     │
└─────────────────────────────────────┘ ← Y: 720
```

### **PyQt5 Fenster-Einstellungen:**
```python
# Feste Fenstergröße für PiTouch2
self.setFixedSize(1280, 660)

# Position: unter der Raspberry Pi Statusleiste
self.move(0, 60)
```

## 🎯 Implementierung

### **Alle View-Dateien verwenden:**
- **Breite:** 1280px (volle Display-Breite)
- **Höhe:** 660px (720px - 60px Statusleiste)
- **X-Position:** 0 (linksbündig)
- **Y-Position:** 60 (unter der Statusleiste)

### **Geänderte Dateien:**
1. `views/start.py`
2. `views/auswahl_seite.py`
3. `views/beladen_seite.py`
4. `views/fuettern_seite.py`
5. `views/einstellungen_seite.py`
6. `views/fuetterung_abschluss.py`
7. `views/futter_konfiguration.py`

### **UI-Dateien (falls vorhanden):**
- `views/start.ui`
- `views/auswahl_seite.ui`
- `views/beladen_seite.ui`
- `views/fuettern_seite.ui`
- `views/einstellungen_seite.ui`
- `views/fuetterung_abschluss.ui`
- `views/futter_konfiguration.ui`

## 🔧 Technische Details

### **Vorteile der Konfiguration:**
- ✅ **Statusleiste bleibt sichtbar** (System-Funktionen zugänglich)
- ✅ **Maximale Nutzfläche** für die Anwendung
- ✅ **Touchscreen-optimiert** (große Touch-Bereiche)
- ✅ **Konsistente Darstellung** auf allen Seiten

### **Display-Eigenschaften:**
- **Pixeldichte:** Hoch (scharf für Touchscreen-Bedienung)
- **Seitenverhältnis:** 16:9 (Standard HD-Format)
- **Touch-Genauigkeit:** Hoch (kapazitiv)

## 🚀 Deployment

### **Automatische Anpassung:**
```python
# In jeder View-Klasse __init__():
def __init__(self, parent=None):
    super().__init__(parent)
    
    # UI laden...
    
    # PiTouch2 Display-Optimierung
    self.setFixedSize(1280, 660)  # Volle Breite, unter Statusleiste
    self.move(0, 60)              # Position unter Raspberry Pi Leiste
```

### **Testen:**
```bash
# Auf dem Raspberry Pi:
cd /home/daniel/Futterkarre-2/
python3 main.py

# Erwartetes Verhalten:
# - Fenster füllt den Bildschirm aus (außer Statusleiste)
# - Raspberry Pi Logo bleibt oben sichtbar
# - Alle Touch-Bereiche sind gut erreichbar
```

## 📝 Versionshistorie

**Version 1.0 (5. November 2025):**
- Initiale Konfiguration für PiTouch2
- Fenstergröße: 1280x660
- Position: (0, 60)
- Alle 7 View-Dateien angepasst

---

**Hardware:** PiTouch2 (1280x720)  
**Projekt:** Futterkarre-2  
**Datum:** 5. November 2025