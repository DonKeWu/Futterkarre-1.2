# 🚜 Futterkarre 1.4.0 - Intelligente Futterwaage für Pferde

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Raspberry Pi](https://img.shields.io/badge/Hardware-Raspberry_Pi_5-red.svg)](https://www.raspberrypi.org)

Ein **PyQt5-basiertes Steuerungssystem** für eine mobile Futterwaage zur präzisen Pferdefütterung. Das System kombiniert **Hardware-Sensorik** mit einer **Touch-optimierten Benutzeroberfläche** für den professionellen Einsatz im Pferdestall.

## 📋 **Projektstatus: Work in Progress** 

**Aktuelle Version:** 1.4.0  
**Zielplattform:** Raspberry Pi 5  
**Letzte Analyse:** 4. November 2025

---

## 🏗️ **Systemarchitektur**

### **Hauptkomponenten:**
```
📁 Futterkarre-2/
├── 🔧 main.py              # Einstiegspunkt & Hardware-Init
├── ⚙️ config/              # Konfiguration & Logging
├── 🎮 controllers/         # Geschäftslogik (MVC)
├── 💾 data/                # CSV-Daten (30 Pferde, Futtersorten)
├── 🔌 hardware/            # Sensor-Abstraktion & Simulation
├── 📊 models/              # Datenmodelle (Pferd, Futter, Fütterung)
├── 🧰 utils/               # Daten-Loader & Validierung
└── 🖥️ views/               # PyQt5 UI-Komponenten
```

### **Design-Pattern:**
- **MVC-Architektur** für saubere Trennung
- **Hardware-Abstraction-Layer** (Simulation ↔ Real Hardware)  
- **Zentrale Navigation** mit Context-Management
- **Dataclass-basierte** Datenmodelle

---

## ⚡ **Features**

### ✅ **Implementiert:**
- **Touch-optimierte UI** (1024x600, große Buttons)
- **30 Pferde-Verwaltung** aus CSV-Daten
- **Mehrere Futtersorten** (Heu, Heulage, Pellets)
- **Echtzeit-Gewichtsmessung** mit HX711-Sensoren
- **Dual-Simulation-System** für Entwicklung/Testing
- **Intelligente Navigation** mit Back-Button Support
- **Robuste Fehlerbehandlung** und Logging

### 🚧 **In Entwicklung:**
- **Futter-Konfiguration** (UI vorhanden, Integration läuft)
- **Nährwert-Berechnung** (erweiterte Algorithmen)
- **Raspberry Pi 5** Hardware-Integration
- **Daten-Persistierung** (Fütterungshistorie)

---

## 🎯 **Analysierte Baustellen**

### **🔴 Kritisch:**
1. **Import-Fehler** - `StartSeite` Import fehlt in `main_window.py`
2. **Gewichtssynchronisation** - Inkonsistenzen zwischen Modulen
3. **CSV-Validierung** - Fehlende Struktur-Prüfung

### **🟡 Mittelfristig:**
1. **Timer-Management** - Mehrfache Timer ohne Koordination
2. **Hardware-Detection** - Raspberry Pi Erkennung verbessern
3. **Error-Handling** - UI-Fallbacks erweitern

### **🟢 Langfristig:**
1. **Performance-Optimierung** - Speicher & CPU-Nutzung
2. **Accessibility** - Multi-DPI Support
3. **Testing** - Unit-Tests erweitern

---

## 🔧 **Hardware-Spezifikationen**

### **Aktuell Geplant:**
- **Raspberry Pi 5** (8GB RAM empfohlen)
- **HX711-Wägezellen** (4x für Karren-Ecken)
- **7" Touchscreen** (1024x600)
- **Industriegehäuse** (IP65-Schutz)

### **Sensoren:**
```python
# Gewichtsmessung
SmartSensorManager()
├── Simulation: hx711_sim.py + fu_sim.py  
└── Hardware: hx711_real.py (Raspberry Pi)
```

---

## 🚀 **Quick Start**

### **Entwicklungsumgebung:**
```bash
# Repository klonen
git clone https://github.com/DonKeWu/Futterkarre-2.git
cd Futterkarre-2

# Abhängigkeiten installieren
pip install PyQt5 pandas

# Simulation starten
python main.py
```

### **Raspberry Pi 5 Setup:**
```bash
# Abhängigkeiten für Hardware
sudo apt update
sudo apt install python3-pyqt5 python3-pip
pip3 install RPi.GPIO hx711

# Hardware-Modus aktivieren
# config/app_config.py: DEBUG_MODE = False
```

---

## 📊 **Datenstruktur**

### **Pferde-Daten (30 Pferde):**
```csv
Folge,Name,Gewicht,Alter
1,Midnight,350,12
2,Delight,280,3
...
```

### **Futter-Sorten:**
- **Heu:** `heu_eigen_2025.csv`, `heu_frd_2025.csv`
- **Heulage:** `heulage_eigen_2025.csv`  
- **Pellets:** `Pellets_deukavallo_Top_E.csv`

---

## 🛣️ **Entwicklungs-Fahrplan**

### **Phase 1: Stabilisierung (bis Ende Nov 2025)**
- [ ] Import-Fehler beheben
- [ ] Gewichtssynchronisation korrigieren
- [ ] CSV-Validierung implementieren
- [ ] Timer-Management zentralisieren

### **Phase 2: Raspberry Pi 5 Integration (Dez 2025)**
- [ ] Hardware-Abstraktionsschicht optimieren
- [ ] GPIO-Konfiguration für HX711
- [ ] Touchscreen-Kalibrierung
- [ ] Performance-Tests auf RPi5

### **Phase 3: Produktionsvorbereitung (Jan 2026)**
- [ ] Futter-Konfiguration vollständig integrieren
- [ ] Nährwert-Algorithmen implementieren
- [ ] Daten-Backup & -Restore
- [ ] Benutzerhandbuch erstellen

---

## 🔬 **Technische Details**

### **Framework Stack:**
- **GUI:** PyQt5 mit .ui Designer-Dateien
- **Hardware:** GPIO/I2C über RPi.GPIO
- **Daten:** CSV mit pandas/dataclasses
- **Logging:** Python logging mit Rotation

### **Code-Qualität:**
- **Type Hints** in kritischen Funktionen
- **Dataclasses** für Datenstrukturen  
- **Exception Handling** mit detailliertem Logging
- **Modular Design** für einfache Erweiterung

---

## 🤝 **Entwicklung**

### **Git Workflow:**
```bash
# Feature-Branch erstellen
git checkout -b feature/rpi5-integration

# Änderungen committen
git commit -m "✨ RPi5: GPIO-Konfiguration für HX711"

# Pull Request erstellen
git push origin feature/rpi5-integration
```

### **Testing:**
```bash
# Unit Tests
python -m pytest tests/

# Simulation testen
python main.py --debug
```

---

## � **Aktueller Deployment-Status**

### **📡 SSH-Verbindung zu Raspberry Pi 5 (4. Nov 2025)**
```bash
# Aktuelle Sitzung:
daniel@Ubuntu24041LTS → ssh daniel@raspberry5
# Status: ✅ Verbunden
# Pi-Version: Linux raspberry5 6.12.47+rpt-rpi-2712 (Debian Bookworm)
# Python: 3.11.2 ✅ | Git: 2.39.5 ✅
```

### **🔄 Repository-Synchronisation:**
- **Ubuntu-Entwicklung:** aktueller Stand (main branch)
- **Raspberry Pi:** Repository vorhanden, aber divergiert (30 vs 1 commits)
- **Nächste Schritte:** Git-Synchronisation + virtuelle Umgebung + Dependencies

### **💻 Deployment-Pipeline:**
1. **Ubuntu ↔ RPi5 Git-Sync** (aktuell in Arbeit)
2. **Python venv Setup** auf Raspberry Pi
3. **PyQt5 + Dependencies** Installation  
4. **Hardware-Tests** mit echten HX711-Sensoren
5. **Autostart-Konfiguration** für Produktiveinsatz

---

## �📝 **Changelog**

### **v2.0.x - Aktuelle Entwicklung**
- ✨ Hardware-Simulation verbessert
- 🐛 Gewichtssynchronisation korrigiert  
- 📝 Umfassende Code-Analyse
- 🔧 .gitignore optimiert
- 🚀 **SSH-Deployment** zu Raspberry Pi 5 eingeleitet

### **v1.x - Legacy**
- 🎯 Grundlegende PyQt5-Implementation
- 📊 CSV-Datenintegration
- 🔌 HX711-Sensor-Support

---

## 📞 **Kontakt & Support**

**Entwickler:** DonKeWu  
**Repository:** [GitHub - Futterkarre-2](https://github.com/DonKeWu/Futterkarre-2)  
**Hardware-Ziel:** Raspberry Pi 5 (geplant)

---

*Dieses Projekt befindet sich in aktiver Entwicklung. Beiträge und Feedback sind willkommen!* 🐴✨
