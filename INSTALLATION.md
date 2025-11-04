# Detaillierte Installationsanleitung für Futterkarre-2

## Raspberry Pi 5 Setup von Grund auf

### 1. Raspberry Pi OS installieren

1. Laden Sie den Raspberry Pi Imager herunter: https://www.raspberrypi.com/software/
2. Installieren Sie Raspberry Pi OS (64-bit) auf eine microSD-Karte
3. Aktivieren Sie SSH und konfigurieren Sie WLAN (optional)
4. Stecken Sie die SD-Karte in den Raspberry Pi und starten Sie ihn

### 2. System aktualisieren

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 3. Python und Entwicklungs-Tools installieren

```bash
sudo apt-get install -y python3 python3-pip python3-dev
sudo apt-get install -y git
```

### 4. PyQt5 und GUI-Abhängigkeiten

```bash
sudo apt-get install -y python3-pyqt5 python3-pyqt5.qtwidgets
sudo apt-get install -y libqt5gui5
```

### 5. GPIO-Bibliotheken

```bash
sudo apt-get install -y python3-rpi.gpio python3-gpiozero
```

### 6. Repository klonen

```bash
cd ~
git clone https://github.com/DonKeWu/Futterkarre-1.2.git
cd Futterkarre-1.2
```

### 7. Python-Abhängigkeiten installieren

```bash
pip3 install -r requirements.txt
```

### 8. Erste Tests im Simulation Mode

```bash
# Konfiguration für Simulation anpassen
nano config/settings.py
# Setzen Sie: SIMULATION_MODE = True

# Anwendung testen
python3 main.py
```

## Hardware-Installation

### HX711 Wägezellen-Modul

#### Benötigte Komponenten

- HX711 Amplifier Modul
- Wägezelle (z.B. 20kg oder 50kg Kapazität)
- Jumperkabel (Female-Female)
- Mechanischer Aufbau für die Wägezelle

#### Verkabelung

```
HX711 VCC  → RPi Pin 2  (5V)
HX711 GND  → RPi Pin 6  (GND)
HX711 DT   → RPi Pin 29 (GPIO 5 / BCM 5)
HX711 SCK  → RPi Pin 31 (GPIO 6 / BCM 6)

Wägezelle E+ (Rot)    → HX711 E+
Wägezelle E- (Schwarz) → HX711 E-
Wägezelle A+ (Weiß)    → HX711 A+
Wägezelle A- (Grün)    → HX711 A-
```

#### Pin-Übersicht Raspberry Pi 5

```
         3V3  (1) (2)  5V  ← HX711 VCC
    GPIO 2    (3) (4)  5V
    GPIO 3    (5) (6)  GND ← HX711 GND
    GPIO 4    (7) (8)  GPIO 14
         GND  (9) (10) GPIO 15
    ...
    GPIO 5   (29) (30) GND  ← HX711 DT (Data)
    GPIO 6   (31) (32) GPIO 12  ← HX711 SCK (Clock)
    ...
```

### 7" Touchscreen

#### Offizielles Raspberry Pi Display

Das offizielle 7" Display wird über die DSI-Schnittstelle angeschlossen:

1. Verbinden Sie das Display-Kabel mit dem DSI-Port
2. Verbinden Sie die Stromversorgung über GPIO-Pins oder USB

#### Konfiguration

```bash
# Display-Rotation falls nötig
sudo nano /boot/config.txt

# Fügen Sie hinzu (für 180° Rotation):
lcd_rotate=2
```

#### Touchscreen-Kalibrierung

```bash
sudo apt-get install -y xinput-calibrator
DISPLAY=:0 xinput_calibrator
```

## Kalibrierung der Waage

### Vorbereitung

1. Besorgen Sie bekannte Gewichte (z.B. 1kg, 5kg, 10kg)
2. Stellen Sie sicher, dass die Waage stabil montiert ist
3. Starten Sie die Anwendung

### Kalibrierungs-Prozess

#### Methode 1: Über die GUI (in Entwicklung)

1. Entfernen Sie alle Lasten von der Waage
2. Klicken Sie auf "Tarieren"
3. Legen Sie ein bekanntes Gewicht auf
4. Notieren Sie die Anzeige

#### Methode 2: Manuelle Kalibrierung

```python
# Testskript erstellen: test_calibration.py
from src.hardware import HX711Scale

scale = HX711Scale()
scale.initialize()

# Schritt 1: Tare
input("Entfernen Sie alle Lasten und drücken Sie Enter...")
scale.tare()

# Schritt 2: Referenzmessung
input("Legen Sie 5kg auf und drücken Sie Enter...")
scale.calibrate(5.0)

# Schritt 3: Test
input("Legen Sie verschiedene Gewichte auf...")
for i in range(10):
    weight = scale.get_weight()
    print(f"Gewicht: {weight:.2f} kg")
    time.sleep(1)
```

Führen Sie aus:
```bash
python3 test_calibration.py
```

### Referenzeinheit eintragen

Nach erfolgreicher Kalibrierung tragen Sie die Referenzeinheit ein:

```bash
nano config/settings.py
```

Ändern Sie:
```python
HX711_REFERENCE_UNIT = IHREN_WERT_HIER  # z.B. 429.5
```

## Autostart konfigurieren

### Desktop-Autostart

Erstellen Sie eine Desktop-Datei:

```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/futterkarre.desktop
```

Inhalt:
```
[Desktop Entry]
Type=Application
Name=Futterkarre-2
Exec=python3 /home/pi/Futterkarre-1.2/main.py
Terminal=false
```

### Systemd-Service (für headless Betrieb)

```bash
sudo nano /etc/systemd/system/futterkarre.service
```

Inhalt:
```
[Unit]
Description=Futterkarre-2 Futterwaage
After=graphical.target

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority
WorkingDirectory=/home/pi/Futterkarre-1.2
ExecStart=/usr/bin/python3 /home/pi/Futterkarre-1.2/main.py
Restart=on-failure

[Install]
WantedBy=graphical.target
```

Aktivieren:
```bash
sudo systemctl daemon-reload
sudo systemctl enable futterkarre.service
sudo systemctl start futterkarre.service
```

## Optimierungen für Produktivbetrieb

### Display-Screensaver deaktivieren

```bash
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```

Fügen Sie hinzu:
```
@xset s off
@xset -dpms
@xset s noblank
```

### Cursor ausblenden (für Touchscreen)

```bash
sudo apt-get install -y unclutter
```

In autostart hinzufügen:
```bash
nano ~/.config/lxsession/LXDE-pi/autostart
```

Ergänzen:
```
@unclutter -idle 0.1 -root
```

### Performance-Optimierung

```bash
# GPU-Speicher erhöhen für flüssigere GUI
sudo nano /boot/config.txt
```

Setzen Sie:
```
gpu_mem=128
```

## Backup-Strategie

### Automatisches Backup einrichten

```bash
# Backup-Skript erstellen
nano ~/backup_futterkarre.sh
```

Inhalt:
```bash
#!/bin/bash
BACKUP_DIR=~/futterkarre_backups
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp -r ~/Futterkarre-1.2/data/ $BACKUP_DIR/data_$DATE/
echo "Backup erstellt: $BACKUP_DIR/data_$DATE/"
```

Ausführbar machen:
```bash
chmod +x ~/backup_futterkarre.sh
```

Cron-Job einrichten (täglich um 23:00):
```bash
crontab -e
```

Hinzufügen:
```
0 23 * * * /home/pi/backup_futterkarre.sh
```

## Troubleshooting

### Fehler: "No module named 'PyQt5'"

```bash
sudo apt-get install python3-pyqt5 python3-pyqt5.qtwidgets
```

### Fehler: "Permission denied" bei GPIO

```bash
sudo usermod -a -G gpio pi
# Dann neu einloggen oder neu starten
```

### Display zeigt nichts an

1. Überprüfen Sie die Display-Verbindung
2. Testen Sie mit `DISPLAY=:0 xclock` ob X11 läuft
3. Prüfen Sie die Einstellungen in `config/settings.py`

### Waage zeigt unrealistische Werte

1. Überprüfen Sie die Verkabelung
2. Führen Sie eine neue Kalibrierung durch
3. Stellen Sie sicher, dass die Wägezelle korrekt montiert ist

### Anwendung startet nicht automatisch

1. Prüfen Sie die Autostart-Konfiguration
2. Überprüfen Sie Berechtigungen der Dateien
3. Schauen Sie in die Logs: `journalctl -u futterkarre.service`

## Support

Bei weiteren Fragen oder Problemen:
- GitHub Issues: https://github.com/DonKeWu/Futterkarre-1.2/issues
- Überprüfen Sie die Dokumentation im Repository
