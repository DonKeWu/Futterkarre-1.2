#!/bin/bash
# 🧹 Pi5 Futterkarre Bereinigung - Entfernt ESP8266-Zeug

echo "🧹 BEREINIGE PI5 FUTTERKARRE INSTALLATION"
echo "========================================"

cd "$(dirname "$0")"

echo "📁 Arbeitsverzeichnis: $(pwd)"

# ESP8266-Verzeichnisse entfernen
echo "🗑️  Entferne ESP8266-Verzeichnisse..."
rm -rf esp8266_dual_hx711_*
rm -rf wireless/esp8266/
rm -rf wireless/esp32/

# ESP8266-Dateien entfernen
echo "🗑️  Entferne ESP8266-Dateien..."
rm -f *esp8266*
rm -f test_dual_*
rm -f test_hx711_*
rm -f diagnose_*
rm -f pi5_*test*
rm -f test_pi5_esp8266_integration.py

# Arduino/Hardware-Dateien entfernen
echo "🗑️  Entferne Arduino-Dateien..."
rm -f *.ino
rm -f install_hx711.sh
rm -f pi5_hx711_pinout.py

# Dokumentations-PDFs entfernen
echo "🗑️  Entferne PDF-Dokumentation..."
rm -f *.pdf

# Development-Zeug entfernen
echo "🗑️  Entferne Development-Dateien..."
rm -f TODO.md
rm -f VERSION
rm -f *DEPLOYMENT*.md
rm -f *ESP8266*.md
rm -f *DUAL_MODE*.md
rm -f *FLASH*.md
rm -f SIMULATION_*.md

# Git-Reste bereinigen
echo "🗑️  Bereinige Git-Status..."
git status --porcelain

echo ""
echo "✅ BEREINIGUNGS-ERGEBNIS:"
echo "========================"

# Was übrig bleibt
echo "📦 VERBLEIBT AUF PI5:"
ls -la | grep -E "(main\.py|views|models|utils|hardware|config|data|logs|requirements\.txt|start\.sh)"

echo ""
echo "🚫 ENTFERNT (ESP8266-Zeug):"
echo "   ❌ esp8266_* Verzeichnisse"
echo "   ❌ wireless/esp8266/ & wireless/esp32/"
echo "   ❌ test_*esp8266* Dateien"
echo "   ❌ *.ino Arduino-Dateien"
echo "   ❌ *.pdf Dokumentation"
echo "   ❌ Development-Markdown-Dateien"

echo ""
echo "🎯 PI5-INSTALLATION BEREINIGT!"
echo "💡 Starte mit: ./start.sh"