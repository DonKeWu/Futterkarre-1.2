# PiTouch2 Display-Optimierung für nächtliche Pferde-Fütterung

## 🌙 **Problem: Helles Display stört Pferde bei Nacht-Fütterung**

### ⚠️ **Aktuelle Situation:**
- Display sehr hell → blendet Benutzer
- Weißer Hintergrund → stört Pferde im Dunkeln
- Keine Helligkeits-Anpassung → unkomfortabel
- Wissenschaftlich: Blaues Licht → Schlafstörung

### 🎯 **Ziel: Pferde-freundliche Nacht-Tauglichkeit**
- Dunkles Theme für wenig Licht
- Rotes/Orange Licht → stört Pferde weniger
- Helligkeits-Kontrolle
- Augen-schonende Farben

---

## 🔆 **Display-Helligkeit einstellen (Pi5):**

### **1. Systemebene (Backlight-Kontrolle):**
```bash
# Aktuelle Helligkeit anzeigen (0-255)
cat /sys/class/backlight/rpi_backlight/brightness

# Helligkeit setzen (z.B. 50 = ~20%)
echo 50 | sudo tee /sys/class/backlight/rpi_backlight/brightness

# Dauerhaft in /boot/config.txt:
echo "backlight=50" | sudo tee -a /boot/config.txt
```

### **2. GUI-Helligkeits-Regler (in Futterkarre-App):**
```python
# In views/einstellungen_seite.py
import os

class HelligkeitsRegler(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        # Helligkeit-Slider (0-255)
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(10, 255)  # Min 10 (nicht komplett dunkel)
        self.brightness_slider.setValue(self.get_current_brightness())
        self.brightness_slider.valueChanged.connect(self.set_brightness)
        
        # Labels
        layout.addWidget(QLabel("🔅"))
        layout.addWidget(self.brightness_slider)
        layout.addWidget(QLabel("🔆"))
        
        # Wert-Anzeige
        self.brightness_label = QLabel(f"{self.brightness_slider.value()}")
        layout.addWidget(self.brightness_label)
        
        self.setLayout(layout)
    
    def get_current_brightness(self):
        try:
            with open("/sys/class/backlight/rpi_backlight/brightness", "r") as f:
                return int(f.read().strip())
        except:
            return 128  # Default
    
    def set_brightness(self, value):
        try:
            # Systembefehl für Helligkeit
            os.system(f"echo {value} | sudo tee /sys/class/backlight/rpi_backlight/brightness > /dev/null")
            self.brightness_label.setText(f"{value}")
            
            # In Settings speichern
            from utils.settings_manager import SettingsManager
            settings = SettingsManager()
            settings.set_setting("display", "brightness", value)
            
        except Exception as e:
            print(f"Helligkeit setzen fehlgeschlagen: {e}")
```

---

## 🎨 **Nacht-Modus Farbschemas (wissenschaftlich optimiert):**

### **Schema 1: Rot-Nacht-Modus (Empfehlung für Pferde)**
```python
# Rotes Licht stört Pferde am wenigsten
NIGHT_MODE_RED = {
    'background': '#1a0000',      # Sehr dunkles Rot
    'surface': '#330000',         # Dunkles Rot  
    'primary': '#ff6b6b',         # Helles Rot für Text
    'secondary': '#ff9999',       # Blassrosa für sekundären Text
    'text': '#ffcccc',            # Sehr helles Rosa
    'accent': '#ff4444',          # Akzent-Rot
    'border': '#660000'           # Dunkelrote Grenzen
}

Wissenschaft:
✅ Rotes Licht → minimale Melatonin-Störung
✅ Pferde sehen Rot schlechter → weniger Irritation  
✅ Erhält Nachtsicht beim Menschen
✅ Wenig blaues Licht → augen-schonend
```

### **Schema 2: Bernstein/Orange (Alternativ)**
```python
# Warmes Orange/Bernstein
NIGHT_MODE_AMBER = {
    'background': '#1a1100',      # Sehr dunkles Braun
    'surface': '#332200',         # Dunkles Bernstein
    'primary': '#ffaa00',         # Orange Text
    'secondary': '#ffcc66',       # Helles Bernstein  
    'text': '#ffe6cc',            # Cremefarbener Text
    'accent': '#ff8800',          # Orange Akzent
    'border': '#664400'           # Dunkle Bernstein-Grenze
}

Vorteile:
✅ Sehr augen-schonend
✅ Warmes Licht → entspannend
✅ Guter Kontrast für Lesbarkeit
✅ Pferde-neutral
```

---

## 🐴 **Pferde-Wissenschaft: Farbwahrnehmung**

### **Was Pferde sehen können:**
```
Pferde-Farbwahrnehmung (Dichromat):
├── Blau-Violett: ✅ Sehr gut sichtbar
├── Grün-Gelb: ✅ Gut sichtbar  
├── Rot: ⚠️ Schlecht sichtbar (wie Grauton)
├── Orange: ⚠️ Reduzierte Wahrnehmung
└── Infrarot: ❌ Nicht sichtbar

Empfehlung: ROT für minimale Störung! 🔴
```

### **Lichtintensität für Pferde:**
```
Pferde-Lichtempfindlichkeit:
├── 10x empfindlicher als Menschen bei wenig Licht
├── Plötzliche Helligkeit → Schreckreaktion  
├── Gleichmäßiges, schwaches Licht → OK
├── Rotes Licht → kaum wahrgenommen
└── Blaues/weißes Licht → sehr störend

Ziel: <50 Lux, warme Farben 🌙
```

---

## 🎯 **Empfehlung für Pferde-Fütterung:**

### **Optimale Nacht-Konfiguration:**
```
🌙 Beste Einstellung für Pferde:
├── Theme: Nacht-Rot (minimal störend für Pferde)
├── Helligkeit: 20-30 (8-12% von Maximum)
├── Auto-Modus: 20:00-06:00 Uhr automatisch
├── Quick-Button: Für manuellen Wechsel
└── Smooth Transitions: Sanfte Übergänge

Wissenschaftlich optimal:
✅ Rotes Licht → Pferde sehen es kaum
✅ Niedrige Helligkeit → keine Schreckreaktion  
✅ Konstant → keine plötzlichen Änderungen
✅ Augen-schonend → Benutzer-Komfort
```

**Soll ich den Nacht-Modus in die Futterkarre-UI implementieren?** 🌙🐴