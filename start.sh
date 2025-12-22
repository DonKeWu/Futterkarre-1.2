#!/bin/bash
# 🚀 Futterkarre Pi5 Starter - ESP8266 Integration Ready!

echo "🐴 Starte Futterkarre mit ESP8266-Integration..."

# Working Directory sicherstellen
cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

echo "📁 Arbeitsverzeichnis: $SCRIPT_DIR"

# Git-Update holen
echo "📡 Git-Update holen..."
git pull origin main

# Dependencies prüfen
echo "📦 Prüfe Python-Dependencies..."
if ! python3 -c "import PyQt5" 2>/dev/null; then
    echo "⚠️  PyQt5 fehlt - installiere Dependencies..."
    pip3 install -r requirements.txt
fi

# ESP8266-Verbindung testen
echo "📡 Teste ESP8266-Verbindung..."
if ping -c 1 192.168.2.20 >/dev/null 2>&1; then
    echo "✅ ESP8266 unter 192.168.2.20 erreichbar"
else
    echo "⚠️  ESP8266 192.168.2.20 nicht erreichbar - prüfe WiFi!"
fi

# 🎯 WICHTIG: PYTHONPATH setzen für korrekte Imports!
export PYTHONPATH="$SCRIPT_DIR"

echo "🚀 Starte Futterkarre..."
echo "   PYTHONPATH=$PYTHONPATH"
echo "   ESP8266-Integration: AKTIV"

# Futterkarre starten
python3 main.py

echo "🐎 Futterkarre beendet"