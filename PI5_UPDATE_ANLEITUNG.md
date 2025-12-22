# 🚀 Pi5 NEUAUFSETZEN für ESP8266 ↔ Pi5 Integration

## 🧹 GRUND FÜR NEUAUFSETZEN:
- Repository ist zugemüllt mit ESP8266-Dateien (gehören nicht auf Pi5)
- Import-Probleme durch chaotische Struktur  
- Zu viele Test-Dateien und Development-Reste

## 🔧 NEUAUFSETZEN-SCHRITTE AUF DEM PI5:

### 1. Altes Verzeichnis komplett löschen
```bash
cd /home/daniel
rm -rf Futterkarre
```

### 2. Repository neu clonen
```bash
cd /home/daniel
git clone https://github.com/DonKeWu/Futterkarre.git
cd Futterkarre
```

### 3. ESP8266-Zeug löschen (gehört nicht auf Pi5!)
```bash
# ESP8266-Verzeichnisse entfernen
rm -rf esp8266_*
rm -rf wireless/esp8266/
rm -rf wireless/esp32/

# ESP8266-Test-Dateien entfernen
rm -f *esp8266*
rm -f test_dual_*
rm -f test_hx711_*
rm -f diagnose_*
rm -f pi5_*test*

# Entwicklungs-Zeug entfernen
rm -f *.ino
rm -f *.pdf
rm -f install_*
rm -f PCB.pdf
rm -f Schema.pdf

# Nur das Wichtige behalten!
echo "Bereinige Pi5-Installation..."
```

### 4. Dependencies installieren
```bash
pip3 install -r requirements.txt
```

### 5. Start-Script executable machen
```bash
chmod +x start.sh
```

### 6. Futterkarre starten
```bash
./start.sh
```

## ✅ WAS BLEIBT AUF DEM PI5:
- **main.py** - Hauptprogramm
- **views/** - GUI-Interface  
- **models/** - Datenmodelle
- **utils/** - Hilfsfunktionen
- **hardware/** - Pi5-Hardware-Abstraktionen
- **config/** - Konfigurationsdateien
- **data/** - CSV-Daten
- **logs/** - Log-Dateien
- **requirements.txt** - Python-Dependencies
- **start.sh** - Start-Script

## 🚫 WAS WEGKOMMT:
- **esp8266_*** - ESP8266-Entwicklungszeug
- **wireless/esp8266/** - ESP8266-Firmware  
- **test_*esp8266*** - ESP8266-Tests
- **diagnose_*** - Hardware-Diagnose-Scripts
- **Alle *.ino Dateien** - Arduino-Code
- **PDF-Dateien** - Dokumentation

## 📊 INTEGRATION TESTEN:

### In der Futterkarre-GUI:
1. **Einstellungen** → **Wägezellen-Kalibrierung**
2. **"ESP8266-Test"** Button klicken
3. **Sollte zeigen:** Alle 4 HX711-Werte (VL, VR, HL, HR)
4. **Live-Updates aktivieren:** Checkbox ankreuzen

### Erwartetes Ergebnis:
```
✅ ESP8266 Integration unter 192.168.2.20 erfolgreich!

📊 HX711 Hardware-Status:
  • VL (D2/D1): ✅ Ready - Raw: 12345
  • VR (D4/D3): ❌ Not Ready - Raw: 0  
  • HL (D6/D5): ✅ Ready - Raw: 67890
  • HR (D8/D7): ✅ Ready - Raw: 54321

⚖️ Pi5 Gewichts-Integration:
  • Gesamtgewicht: 1.234 kg
  • Einzelzellen: VL=0.123, VR=0.000, HL=0.679, HR=0.432
```

## 🚨 TROUBLESHOOTING:

### Wenn ESP8266 nicht gefunden:
```bash
# WiFi-Verbindung prüfen
iwconfig

# ESP8266 direkt testen
curl -v http://192.168.2.20/

# IP-Scan im Netzwerk
nmap -sn 192.168.2.0/24
```

### Wenn HX711-Werte "0" sind:
- **Hardware prüfen:** 5V Stromversorgung, nicht 3.3V
- **ESP8266 Web-UI:** http://192.168.2.20/hardware-test
- **Verkabelung:** D2/D1, D4/D3, D6/D5, D8/D7 korrekt?

### Wenn Futterkarre nicht startet:
```bash
# Dependencies prüfen
pip3 list | grep PyQt5

# Logs anschauen
tail -f logs/futterkarre.log

# Virtual Environment neu erstellen falls nötig
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

## 🎯 ERFOLG-KRITERIEN:

✅ **ESP8266 unter 192.168.2.20 erreichbar**  
✅ **Pi5-Futterkarre startet ohne Fehler**  
✅ **Wägezellen-Kalibrierung zeigt ESP8266-Test erfolgreich**  
✅ **Live-Updates zeigen echte HX711-Werte**  
✅ **HL und HR zeigen Werte > 0 (falls Wägezellen angeschlossen)**

## 🔗 LINKS:
- **ESP8266 Web-UI:** http://192.168.2.20/
- **Live-Werte:** http://192.168.2.20/live-values  
- **Hardware-Test:** http://192.168.2.20/hardware-test

---
**🎉 Nach erfolgreichem Update: ESP8266 und Pi5 arbeiten zusammen! 🚀**