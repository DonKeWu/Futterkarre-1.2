#!/bin/bash
# 🔧 ESP8266 IP-Adresse von 192.168.2.17 auf 192.168.2.20 aktualisieren

echo "🔄 Aktualisiere ESP8266 IP-Adressen von .17 auf .20 ..."

cd "/home/daniel/Dokumente/HOF/Futterwagen/Python/Futterkarre"

# Views aktualisieren
echo "📝 Aktualisiere views/..."
find views/ -name "*.py" -type f -exec sed -i 's/192\.168\.2\.17/192.168.2.20/g' {} \;

# Start-Script aktualisieren  
echo "📝 Aktualisiere start.sh..."
sed -i 's/192\.168\.2\.17/192.168.2.20/g' start.sh

# Test-Dateien aktualisieren
echo "📝 Aktualisiere Test-Dateien..."
find . -name "test_*.py" -type f -exec sed -i 's/192\.168\.2\.17/192.168.2.20/g' {} \;

# Debug-Dateien aktualisieren
echo "📝 Aktualisiere Debug-Dateien..."
find . -name "debug_*.py" -type f -exec sed -i 's/192\.168\.2\.17/192.168.2.20/g' {} \;

# Dokumentation aktualisieren
echo "📝 Aktualisiere Dokumentation..."
find . -name "*.md" -type f -exec sed -i 's/192\.168\.2\.17/192.168.2.20/g' {} \;

echo "✅ IP-Adresse von 192.168.2.17 → 192.168.2.20 aktualisiert!"
echo ""
echo "🔍 Teste ESP8266-Verbindung:"
if ping -c 1 192.168.2.20 >/dev/null 2>&1; then
    echo "✅ ESP8266 unter 192.168.2.20 erreichbar!"
else
    echo "❌ ESP8266 192.168.2.20 nicht erreichbar - WiFi prüfen!"
fi

echo ""
echo "🚀 Starte Futterkarre neu..."
./start.sh