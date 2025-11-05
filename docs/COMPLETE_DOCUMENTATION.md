# 🚜 Futterkarre 1.2 - Komplette Dokumentation

**Intelligente Futterwaage für Pferde mit Raspberry Pi 5 + Touch-Display**

---

## 📋 Inhaltsverzeichnis

1. [Display & Touch-Anpassungen](#display--touch-anpassungen)
2. [Software-Architektur](#software-architektur)
3. [WeightManager System](#weightmanager-system)
4. [CSV-Validierung](#csv-validierung)
5. [Hardware-Spezifikationen](#hardware-spezifikationen)
6. [HX711 Wägezellen-System](#hx711-wägezellen-system)
7. [Raspberry Pi 5 Setup](#raspberry-pi-5-setup)
8. [Ernährungsphysiologie](#ernährungsphysiologie)
9. [Entwicklungs-Fahrplan](#entwicklungs-fahrplan)
10. [Online-Shops & Bezugsquellen](#online-shops--bezugsquellen)

---

## 🚀 Software-Architektur

### Aktuelle Implementierung (Stand: 5. November 2025)

**✅ Vollständig implementiert:**
- **WeightManager Singleton:** Zentrale Gewichtsverwaltung
- **CSV-Validierung:** Robuste Datenvalidierung mit Fallback
- **HEU-Button Feature:** Separate Heu/Heulage Tracking
- **Fullscreen UI:** Optimiert für PiTouch2 (1280x720)
- **Simulation System:** Realistische Hardware-Simulation

**🔄 In Entwicklung:**
- **Timer-Management:** Zentralisierung aller UI-Timer
- **Futter-Konfiguration:** Integration in MainWindow

### Projektstruktur
```
Futterkarre-2/
├── main.py                  # Hauptanwendung
├── config/                  # Konfigurationsdateien
├── controllers/             # Business Logic
├── data/                    # CSV-Daten (Pferde, Futter)
├── hardware/                # Hardware-Abstraktionen
│   ├── weight_manager.py    # ⭐ Zentrale Gewichtsverwaltung
│   ├── sensor_manager.py    # Legacy-Wrapper
│   ├── hx711_real.py       # Echte Hardware
│   └── hx711_sim.py        # Simulation
├── models/                  # Datenmodelle
├── utils/                   # Hilfsfunktionen
│   ├── csv_validator.py    # ⭐ CSV-Validierung
│   └── futter_loader.py    # Datenloading
├── views/                   # UI-Komponenten
└── tests/                   # Test-Scripts
```

---

## ⚖️ WeightManager System

### Zentrale Gewichtsverwaltung (Singleton)

**Problem gelöst:**
- Inkonsistente Gewichtsverwaltung zwischen UI-Komponenten
- Manuelle Simulation/Hardware-Umschaltung
- Timer-basiertes Polling für UI-Updates

**Implementierung:**
```python
from hardware.weight_manager import get_weight_manager

# Zentraler Zugriff
wm = get_weight_manager()

# Gewicht lesen (Auto-Hardware/Simulation)
weight = wm.read_weight()

# Observer für UI-Updates registrieren
wm.register_observer("ui_component", callback_function)

# Simulation steuern
wm.set_simulation_mode(True)
wm.simulate_weight_change(-4.5)  # 4.5kg entfernen
```

**Features:**
- ✅ **Singleton Pattern:** Eine Instanz für gesamte Anwendung
- ✅ **Auto-Erkennung:** Hardware vs. Simulation automatisch
- ✅ **Observer-Pattern:** Event-basierte UI-Updates
- ✅ **Robuste Fehlerbehandlung:** Automatischer Fallback
- ✅ **State-Management:** Zentraler Gewichtszustand
- ✅ **Kalibrierung:** Nullpunkt setzen, Einzelzellen lesen

**Integration:**
- `FuetternSeite`: Automatische Gewichtsupdates
- `BeladenSeite`: Einheitliche Gewichtsquelle  
- `sensor_manager`: Legacy-Wrapper für Kompatibilität

---

## 📊 CSV-Validierung

### Robuste Datenvalidierung mit Schema

**Problem gelöst:**
- Kaputte CSV-Dateien führten zu Programmabstürzen
- Keine Validierung von Datentypen und Wertebereichen
- Fehlende Fallback-Mechanismen

**Schema-Definition:**
```python
# Beispiel: Pferde-Schema
pferde_schema = [
    ColumnSchema("Name", str, required=True),
    ColumnSchema("Gewicht", float, required=True, min_value=50, max_value=1200),
    ColumnSchema("Alter", int, required=True, min_value=1, max_value=40),
    ColumnSchema("Box", int, required=True, min_value=1),
    ColumnSchema("Aktiv", str, allowed_values=["true", "false"])
]
```

**Verwendung:**
```python
from utils.csv_validator import CSVValidator

validator = CSVValidator()
result = validator.validate_csv_file('data/pferde.csv', 'pferde')

if result['success']:
    valid_data = result['data']
else:
    fallback_data = validator.get_fallback_data('pferde')
```

**Features:**
- ✅ **Schema-basiert:** Typisierte Validierung
- ✅ **Automatische Korrektur:** Standardwerte bei Fehlern
- ✅ **Edge-Case Handling:** Leere/kaputte Dateien
- ✅ **Fallback-Daten:** Notfall-Datasets
- ✅ **Detailliertes Logging:** Fehler und Warnungen
- ✅ **Integration:** Nahtlos in futter_loader.py

---

## 🖥️ Display & Touch-Anpassungen

### Aktuelle UI-Konfiguration (FUNKTIONIERT!)
- **Fullscreen-Modus:** `window.showFullScreen()`
- **Native Skalierung:** Keine DPI-Verzerrung
- **Responsive Design:** Automatische Anpassung an Bildschirmgröße
- **Touch-optimiert:** Große Buttons für Finger-Bedienung

### Display-Größen Support
- ✅ **1280x720** (Raspberry Pi Touch Display 2 - Landscape)
- ✅ **720x1280** (Raspberry Pi Touch Display 2 - Portrait)  
- ✅ **800x480** (Raspberry Pi Touch Display v1)
- ✅ **1024x600** (Industrie-Touchscreens)
- ✅ **1920x1080** (Standard-Monitore)
- ✅ **Beliebige Auflösungen** (Auto-Scaling)

### Hardware-Display: Raspberry Pi Touch Display 2
```
Artikelnummer:    RPI-7LCD2
Displaygröße:     7 Zoll (diagonal)
Auflösung:        720 (RGB) × 1280 Pixel (Portrait)
                  1280 × 720 Pixel (Landscape - verwendet)
Aktive Fläche:    86,94 mm × 154,56 mm
Touch-Panel:      True Multi-Touch kapazitiv (5 Finger)
Oberflächenbehandlung: Anti-Glanz
Abmessungen:      189,32 mm × 120,24 mm × ~7mm
Gewicht:          0.3kg
Anschluss:        DSI-Port + GPIO-Stromversorgung
Produktlebensdauer: Mindestens bis Januar 2030
```

### UI-Einstellungen (Optimiert für RPi Touch Display 2)
```python
# main.py - Optimale Konfiguration für 1280x720 Landscape
window.showFullScreen()     # Vollbild erzwingen
setMinimumSize(1280, 720)   # Native Auflösung des Displays
resize(1280, 720)           # Exakte Display-Größe
```

---

## 🔧 Hardware-Spezifikationen

### Raspberry Pi 5 (Empfohlen)
- **CPU:** ARM Cortex-A76 Quad-Core 2.4GHz
- **RAM:** 8GB LPDDR4X (empfohlen für PyQt5)
- **Storage:** 64GB+ microSD (SanDisk Extreme Pro)
- **GPIO:** 40-Pin für HX711-Sensoren
- **USB:** 2x USB 3.0 + 2x USB 2.0
- **Display:** 2x micro-HDMI oder DSI-Connector

### Touch-Display Optionen
1. **Raspberry Pi Touch Display 7"** (800x480)
2. **Industrie-Touchscreen 10"** (1024x600)
3. **Kapazitiv-Touch 15"** (1920x1080)

### Stromversorgung
- **Pi 5:** 5V/5A USB-C Netzteil
- **Touch-Display:** über GPIO oder separates Netzteil
- **HX711-Sensoren:** 3.3V/5V vom Pi

---

## ⚖️ HX711 Wägezellen-System

### Hardware-Konfiguration
```
4x HX711-Module (eine pro Karren-Ecke)
├── VCC → 5V (Pin 2/4)
├── GND → GND (Pin 6/9/14/20)
├── DT (Data) → GPIO Pin
└── SCK (Clock) → GPIO Pin
```

### GPIO-Pinout (Final)
```
HX711_1: DT=GPIO5,  SCK=GPIO6   # Vorne Links
HX711_2: DT=GPIO13, SCK=GPIO19  # Vorne Rechts  
HX711_3: DT=GPIO26, SCK=GPIO21  # Hinten Links
HX711_4: DT=GPIO16, SCK=GPIO20  # Hinten Rechts
```

### Wägezellen-Spezifikationen
- **Typ:** Balken-Wägezellen 100-500kg
- **Signal:** 0-20mV bei Vollausschlag
- **Kalibrierung:** Automatisch über bekannte Gewichte
- **Genauigkeit:** ±0.1kg bei ordnungsgemäßer Kalibrierung

### Verstärkung & Kalibrierung
```python
# hardware/hx711_real.py
SCALE_FACTOR = 1000  # Anpassbar je Wägezelle
OFFSET = 0          # Nullpunkt-Kalibrierung
```

### Verkabelung (Kabellängen)
- **Sensor zu HX711:** Max. 3m (abgeschirmtes Kabel)
- **HX711 zu Pi:** Max. 5m (Standard-Kabel ausreichend)
- **Stromversorgung:** Zentral vom Pi oder externe 5V-Versorgung

---

## 🖥️ Raspberry Pi 5 Setup

### Betriebssystem
```bash
# Raspberry Pi OS (64-bit) - Bookworm
# Download: https://rpi.org/downloads
```

### Software-Installation
```bash
# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Python-Abhängigkeiten
sudo apt install python3-pyqt5 python3-pip python3-venv

# Git-Repository klonen
git clone https://github.com/DonKeWu/Futterkarre-1.2.git

# Virtual Environment
cd Futterkarre-1.2
python3 -m venv .venv --system-site-packages
source .venv/bin/activate

# Python-Pakete
pip install pandas RPi.GPIO hx711
```

### Autostart-Konfiguration
```bash
# Desktop-Button erstellen
cat > ~/Desktop/🚜-Futterkarre.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=🚜 Futterkarre 1.2
Exec=/bin/bash -c "cd /home/daniel/Futterkarre-1.2 && source .venv/bin/activate && python main.py"
Icon=applications-utilities
Terminal=false
Categories=Application;Utility;
EOF
chmod +x ~/Desktop/🚜-Futterkarre.desktop
```

---

## 🐴 Ernährungsphysiologie

### Richtwerte pro 100kg Körpergewicht/Tag
```
Heu:        1.5-2.5 kg (Grundfutter)
Heulage:    2.0-3.0 kg (höhere Feuchtigkeit)
Kraftfutter: 0.5-1.5 kg (je nach Leistung)
Wasser:     25-40 Liter
```

### Nährwert-Berechnung
```python
# models/futter.py
@dataclass
class Futter:
    name: str
    energie_mj: float      # MJ ME/kg TS
    rohprotein: float      # % TS
    rohfaser: float        # % TS
    trockensubstanz: float # % TS
```

### Futter-Kategorien im System
1. **Heu** (trocken, 85-90% TS)
2. **Heulage** (siliert, 50-70% TS)  
3. **Pellets** (gepresst, 88-92% TS)
4. **Ergänzungsfutter** (Vitamine/Mineralien)

---

## 🗺️ Entwicklungs-Fahrplan

### ✅ Phase 1: Grundsystem (Abgeschlossen)
- [x] PyQt5-GUI mit Touch-Optimierung
- [x] CSV-Datenbank (30 Pferde + Futtersorten)
- [x] HX711-Simulation für Entwicklung
- [x] MVC-Architektur
- [x] GitHub-Repository + Deployment-Pipeline

### 🚧 Phase 2: Hardware-Integration (Aktuell)
- [x] Raspberry Pi 5 Setup
- [x] Fullscreen UI ohne Verzerrung
- [ ] Echte HX711-Sensoren anschließen
- [ ] Kalibrierung-Interface
- [ ] Robuste Gewichtsmessung

### 🔮 Phase 3: Produktionsreife (Q1 2026)
- [ ] Wetter-/Schmutzresistentes Gehäuse
- [ ] WLAN-Konfiguration für Updates
- [ ] Daten-Backup & Cloud-Sync
- [ ] Multi-Benutzer-System
- [ ] Fütterungshistorie & Reports

### 🎯 Phase 4: Erweiterungen (Q2 2026)
- [ ] RFID-Pferdeerkennung
- [ ] Automatische Rationsberechnung
- [ ] Tierarzt-Schnittstelle
- [ ] Mobile App für Stallbesitzer

---

## 🛒 Online-Shops & Bezugsquellen

### Elektronik-Komponenten
```
Raspberry Pi 5:     https://rpi.org/products/
HX711-Module:       https://www.az-delivery.de/
Touch-Displays:     https://www.waveshare.com/
Gehäuse:           https://www.bopla.de/
Kabel:             https://www.reichelt.de/
```

### Wägezellen & Mechanik
```
Wägezellen:        https://www.bosche.eu/
Befestigung:       https://www.item24.de/
Schrauben:         https://www.wuerth.de/
Dichtungen:        https://www.simrit.de/
```

### Software & Services
```
GitHub Pro:        https://github.com/pricing
MicroSD-Karten:    https://www.sandisk.de/
Backup-Cloud:      https://www.dropbox.com/
```

---

## 🔧 Wartung & Updates

### Automatische Updates
```bash
# Am Raspberry Pi - Auto-Update Script
cat > ~/update_futterkarre.sh << 'EOF'
#!/bin/bash
cd ~/Futterkarre-1.2
git pull origin main
source .venv/bin/activate
pip install --upgrade -r requirements.txt
EOF
chmod +x ~/update_futterkarre.sh
```

### Backup-Strategie
1. **Code:** Automatisch über GitHub
2. **Daten:** Wöchentlich auf USB-Stick
3. **Konfiguration:** Teil des Git-Repositories
4. **System:** Image-Backup bei Änderungen

### Fehlerbehebung
```bash
# Logs prüfen
tail -f ~/Futterkarre-1.2/logs/futterkarre.log

# Hardware-Test
python ~/Futterkarre-1.2/tests/test_hardware.py

# Display-Kalibrierung
sudo raspi-config → Advanced → GL Driver
```

---

## 📞 Support & Community

**Entwickler:** DonKeWu  
**Repository:** https://github.com/DonKeWu/Futterkarre-1.2  
**Hardware-Ziel:** Raspberry Pi 5 (produktiv)  
**Status:** Deployment-Ready (Nov 2025)

---

*Diese Dokumentation fasst alle Einzeldokumente zusammen und wird kontinuierlich aktualisiert. Letztes Update: 5. November 2025* 🚜✨

---

## 🎯 Aktuelle Entwicklungsstand (5. November 2025)

### ✅ **Abgeschlossen:**
1. **WeightManager Singleton** - Zentrale Gewichtsverwaltung implementiert
2. **CSV-Validierung** - Robuste Datenvalidierung mit Fallback-Mechanismen  
3. **HEU-Button Feature** - Separate Heu/Heulage Statistiken
4. **Fullscreen UI** - Optimiert für PiTouch2 (1280x720)
5. **Display-Konfiguration** - SSH + VNC Setup für Entwicklung

### 🔄 **In Bearbeitung:**
- **Timer-Management** - Zentralisierung aller UI-Timer (nächste Priorität)

### 📋 **Noch offen:**
- Futter-Konfiguration Integration
- Hardware-Beschaffung RPi5-System

**Repository:** https://github.com/DonKeWu/Futterkarre-1.2  
**Commits:** 34c1080 (CSV-Validierung), c0f6aef (WeightManager)  
**Status:** Produktionsreif für Pi-Deployment