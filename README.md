# Futterkarre-2
🚜 Intelligente Futterwaage für Pferde - PyQt5 + Raspberry Pi 5

## Übersicht

Futterkarre-2 ist eine industrietaugliche Futterwaage-Anwendung für den Pferdestall-Einsatz, optimiert für Raspberry Pi 5 mit 7" Touchscreen (1024x600).

### Features

- **Touch-optimierte GUI**: PyQt5-basierte Benutzeroberfläche für 1024x600 Auflösung
- **Pferdeverwaltung**: Verwaltung von bis zu 30 Pferden mit vollständigen Stammdaten
- **HX711-Integration**: Direkte Anbindung von Wägezellen mit HX711-Sensor
- **Simulation Mode**: Entwicklung und Test ohne Hardware möglich
- **CSV-Datenhaltung**: Robuste Datenspeicherung für Pferde und Fütterungshistorie
- **MVC-Architektur**: Saubere Trennung von Model, View und Controller
- **Hardware-Abstraktion**: Austauschbare Scale-Implementierungen
- **GPIO-Steuerung**: Native Raspberry Pi 5 GPIO-Unterstützung

### Unterstützte Futterarten

- Heu
- Heulage
- Pellets

## Systemanforderungen

### Hardware

- Raspberry Pi 5 (empfohlen) oder Raspberry Pi 4
- 7" Touchscreen Display (1024x600)
- HX711 Wägezellen-Modul
- Wägezelle(n) für gewünschten Messbereich
- MicroSD-Karte (min. 16GB)

### Software

- Raspberry Pi OS (Debian Bookworm oder neuer)
- Python 3.9+
- PyQt5
- GPIO-Bibliotheken (automatisch installiert)

## Installation

### 1. Repository klonen

```bash
git clone https://github.com/DonKeWu/Futterkarre-1.2.git
cd Futterkarre-1.2
```

### 2. Python-Abhängigkeiten installieren

```bash
pip3 install -r requirements.txt
```

Auf Raspberry Pi:
```bash
sudo apt-get update
sudo apt-get install python3-pyqt5
pip3 install -r requirements.txt
```

### 3. Konfiguration anpassen

Bearbeiten Sie `config/settings.py` für Ihre spezifischen Anforderungen:

```python
# Display-Einstellungen
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FULLSCREEN = True

# HX711-Pins (BCM-Nummerierung)
HX711_DATA_PIN = 5
HX711_CLOCK_PIN = 6

# Simulation für Entwicklung ohne Hardware
SIMULATION_MODE = False  # True für Entwicklung ohne Hardware
```

### 4. Hardware-Kalibrierung (nur bei echter Hardware)

Siehe Abschnitt "Hardware-Setup" für Details zur Kalibrierung der Waage.

## Verwendung

### Anwendung starten

```bash
python3 main.py
```

Oder ausführbar machen und direkt starten:
```bash
chmod +x main.py
./main.py
```

### Simulation Mode (Entwicklung ohne Hardware)

Für Entwicklung und Tests ohne Hardware:

1. Setzen Sie in `config/settings.py`:
   ```python
   SIMULATION_MODE = True
   ```

2. Starten Sie die Anwendung wie gewohnt

### Hauptfunktionen

#### 1. Wiegen (⚖️ Wiegen)
- Waage tarieren mit "Tarieren"-Button
- Pferd und Futterart auswählen
- Futter auflegen und Gewicht ablesen
- Mit "Speichern" die Messung aufzeichnen

#### 2. Pferdeverwaltung (🐴 Pferde)
- Pferde hinzufügen mit "+ Neues Pferd"
- Pferdedaten bearbeiten (✏️-Button)
- Pferde löschen (🗑️-Button)
- Unterstützt bis zu 30 Pferde

#### 3. Historie (📊 Historie)
- Fütterungshistorie einsehen
- Nach Pferd filtern
- Nach Zeitraum filtern (Heute, 7 Tage, Monat, Alle)
- Statistiken über Gesamtfütterungen und -mengen

## Projektstruktur

```
Futterkarre-1.2/
├── main.py                 # Haupteinstiegspunkt
├── requirements.txt        # Python-Abhängigkeiten
├── config/                 # Konfiguration
│   ├── __init__.py
│   └── settings.py         # Zentrale Einstellungen
├── src/
│   ├── models/             # Datenmodelle (MVC-Model)
│   │   ├── __init__.py
│   │   ├── horse.py        # Pferd-Datenmodell
│   │   ├── feed_record.py  # Fütterungs-Datenmodell
│   │   └── data_manager.py # CSV-Datenverwaltung
│   ├── views/              # GUI-Komponenten (MVC-View)
│   │   ├── __init__.py
│   │   ├── main_window.py  # Hauptfenster
│   │   ├── weighing_view.py         # Wiege-Ansicht
│   │   ├── horse_management_view.py # Pferde-Ansicht
│   │   └── history_view.py          # Historie-Ansicht
│   ├── controllers/        # Anwendungslogik (MVC-Controller)
│   │   ├── __init__.py
│   │   └── app_controller.py # Hauptcontroller
│   ├── hardware/           # Hardware-Abstraktion
│   │   ├── __init__.py
│   │   ├── scale_interface.py    # Interface für Waagen
│   │   ├── hx711_scale.py        # HX711-Implementierung
│   │   └── simulated_scale.py    # Simulations-Implementierung
│   └── utils/              # Hilfsfunktionen
│       └── __init__.py
└── data/                   # Daten-Verzeichnis
    ├── horses.csv          # Pferdedaten (wird erstellt)
    ├── feed_records.csv    # Fütterungshistorie (wird erstellt)
    ├── example_horses.csv      # Beispieldaten
    └── example_feed_records.csv # Beispieldaten
```

## Hardware-Setup

### HX711 Verkabelung (Raspberry Pi 5)

Standardkonfiguration (BCM-Pin-Nummerierung):

| HX711-Pin | RPi5-Pin | BCM-Pin | Beschreibung |
|-----------|----------|---------|--------------|
| VCC       | Pin 2    | 5V      | Stromversorgung |
| GND       | Pin 6    | GND     | Masse |
| DT (Data) | Pin 29   | GPIO 5  | Datenleitung |
| SCK (Clock)| Pin 31  | GPIO 6  | Taktleitung |

### Wägezellen-Anschluss

Verbinden Sie die Wägezelle(n) mit dem HX711:
- E+ (Excitation+): Rote Leitung
- E- (Excitation-): Schwarze Leitung
- A+ (Signal+): Weiße Leitung
- A- (Signal-): Grüne Leitung

### Kalibrierung

1. Starten Sie die Anwendung
2. Wählen Sie "⚖️ Wiegen"
3. Entfernen Sie alle Lasten von der Waage
4. Klicken Sie "Tarieren"
5. Legen Sie ein bekanntes Gewicht auf (z.B. 5kg)
6. Notieren Sie die Referenzeinheit für `HX711_REFERENCE_UNIT` in `config/settings.py`

## Datensicherung

Die Anwendung speichert alle Daten in CSV-Dateien im `data/`-Verzeichnis:

- `horses.csv`: Pferdedaten
- `feed_records.csv`: Fütterungshistorie

**Empfehlung**: Erstellen Sie regelmäßige Backups dieser Dateien!

```bash
# Backup erstellen
cp -r data/ backup_$(date +%Y%m%d)/
```

## Entwicklung

### MVC-Architektur

Die Anwendung folgt dem Model-View-Controller-Pattern:

- **Model** (`src/models/`): Datenstrukturen und Persistenz
- **View** (`src/views/`): PyQt5-GUI-Komponenten
- **Controller** (`src/controllers/`): Geschäftslogik und Koordination

### Hardware-Abstraktion

Die `ScaleInterface` ermöglicht verschiedene Waagen-Implementierungen:

- `HX711Scale`: Echte Hardware-Anbindung
- `SimulatedScale`: Simulation für Entwicklung

Eigene Implementierungen können durch Ableitung von `ScaleInterface` erstellt werden.

### Erweiterungen

- Weitere Futterarten: Ergänzen Sie `FEED_TYPES` in `config/settings.py`
- Weitere Sensoren: Implementieren Sie `ScaleInterface` für neue Hardware
- Export-Funktionen: Nutzen Sie die CSV-Daten für weitere Analysen

## Troubleshooting

### Waage wird nicht erkannt

- Überprüfen Sie die GPIO-Verkabelung
- Stellen Sie sicher, dass GPIO-Bibliotheken installiert sind
- Testen Sie mit `SIMULATION_MODE = True`

### Touchscreen reagiert nicht

- Kalibrieren Sie den Touchscreen im Raspberry Pi OS
- Überprüfen Sie die Display-Einstellungen in `config/settings.py`

### Fehler beim Import von PyQt5

```bash
sudo apt-get install python3-pyqt5
```

### Berechtigungen für GPIO

Fügen Sie Ihren Benutzer zur GPIO-Gruppe hinzu:
```bash
sudo usermod -a -G gpio $USER
```

## Lizenz

Dieses Projekt ist für den Einsatz in Pferdestall-Umgebungen optimiert.

## Kontakt

Bei Fragen oder Problemen erstellen Sie bitte ein Issue im GitHub-Repository.

---

**Futterkarre-2** - Industrietaugliche Futterwaage für professionelle Pferdehaltung 🐴🚜
