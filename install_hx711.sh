#!/bin/bash
# HX711 Library Installation auf Pi5

echo "🔧 HX711 Python Library Installation"
echo "===================================="

# Option 1: Über pip installieren
echo "📦 Installiere HX711 Library via pip..."
pip3 install HX711

# Falls das nicht funktioniert, Alternative:
echo "📦 Alternative: GPIO-basierte HX711 Library..."
pip3 install hx711py

# RPi.GPIO Update (falls nötig)
echo "🔧 RPi.GPIO Update..."
pip3 install --upgrade RPi.GPIO

echo "✅ Installation abgeschlossen!"
echo ""
echo "🧪 Teste mit:"
echo "python3 test_hx711_direct.py"