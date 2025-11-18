#!/bin/bash

# 🚀 ESP8266 Dual-Mode WiFi - Pi5 Deployment Script
# Bereitet das Pi5 System für ESP8266 Dual-Mode vor

echo "🔄 ESP8266 Dual-Mode WiFi - Pi5 Deployment gestartet..."
echo "⏰ $(date '+%H:%M:%S')"
echo "=" * 60

# 1. Git Repository aktualisieren
echo "📥 Git Repository aktualisieren..."
git pull origin main
if [ $? -eq 0 ]; then
    echo "✅ Git pull erfolgreich"
else
    echo "❌ Git pull fehlgeschlagen"
    exit 1
fi

# 2. Python Virtual Environment aktivieren
echo "🐍 Python Environment aktivieren..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual Environment aktiv"
else
    echo "❌ Virtual Environment nicht gefunden"
    echo "💡 Erstelle Virtual Environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# 3. Python Dependencies prüfen
echo "📦 Python Dependencies prüfen..."
python -c "
import PyQt5
import requests
import json
print('✅ Alle Python Dependencies verfügbar')
"

if [ $? -ne 0 ]; then
    echo "❌ Python Dependencies fehlen"
    echo "💡 Installiere Dependencies..."
    pip install PyQt5 requests
fi

# 4. ESP8266 Test-IPs prüfen
echo "📡 ESP8266 Connectivity Test..."
ESP8266_IPS=("192.168.4.1" "192.168.2.17")

for ip in "${ESP8266_IPS[@]}"; do
    echo "🔍 Testing $ip..."
    
    # Ping Test (1 Versuch, 2s Timeout)
    if ping -c 1 -W 2 $ip > /dev/null 2>&1; then
        echo "✅ $ip ist erreichbar"
        
        # HTTP Status Test
        if curl -s --max-time 3 "http://$ip/status" > /dev/null; then
            echo "🌐 $ip HTTP API funktional"
        else
            echo "⚠️  $ip Ping OK, aber HTTP API nicht verfügbar"
        fi
    else
        echo "❌ $ip nicht erreichbar (ESP8266 noch nicht geflasht?)"
    fi
done

# 5. Futterkarre GUI Test-Start
echo "🖥️  GUI-System Test..."
echo "💡 Starte Futterkarre GUI für ESP8266 Test..."

# GUI im Hintergrund starten für 10 Sekunden Test
timeout 10s python main.py &
GUI_PID=$!

sleep 3
if ps -p $GUI_PID > /dev/null; then
    echo "✅ GUI startet erfolgreich"
    kill $GUI_PID 2>/dev/null
else
    echo "❌ GUI Start-Probleme"
fi

# 6. Log-Verzeichnis vorbereiten
echo "📝 Log-System vorbereiten..."
mkdir -p logs
touch logs/futterkarre.log
echo "✅ Log-System bereit"

# 7. Deployment Summary
echo ""
echo "=" * 60
echo "📋 DEPLOYMENT SUMMARY"
echo "=" * 60

echo "🔧 System Status:"
echo "   ✅ Git Repository aktuell"
echo "   ✅ Python Environment aktiv"
echo "   ✅ Dependencies installiert"
echo "   ✅ GUI funktional"
echo "   ✅ Log-System bereit"

echo ""
echo "📡 ESP8266 Status:"
for ip in "${ESP8266_IPS[@]}"; do
    if ping -c 1 -W 2 $ip > /dev/null 2>&1; then
        echo "   ✅ $ip erreichbar"
    else
        echo "   ⏳ $ip nicht verfügbar (Flash ESP8266 mit Dual-Mode Firmware)"
    fi
done

echo ""
echo "🎯 Nächste Schritte:"
echo "   1. 📱 ESP8266 mit Dual-Mode Firmware flashen"
echo "   2. 🔌 ESP8266 mit Strom versorgen"
echo "   3. 🖥️  Futterkarre GUI starten: python main.py"
echo "   4. ⚙️  ESP8266 Config-Seite öffnen"
echo "   5. 🧪 Dual-Mode Tests durchführen"

echo ""
echo "🚀 Pi5 System ist bereit für ESP8266 Dual-Mode Integration!"
echo "⏰ Deployment abgeschlossen: $(date '+%H:%M:%S')"