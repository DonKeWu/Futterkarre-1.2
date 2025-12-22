#!/bin/bash
# 🚀 ESP8266 Flash & Git Update für IP 192.168.2.20

echo "🔥 ESP8266 Flash & Git Update..."
echo "================================"

# 1. Git Status prüfen
echo "📊 Git Status:"
git status

echo ""
echo "🔄 Alle Änderungen committen..."

# 2. Alle Änderungen hinzufügen
git add .

# 3. Commit mit IP-Update
git commit -m "🔧 ESP8266 IP-Adresse: 192.168.2.17 → 192.168.2.20

- Alle Python-Dateien aktualisiert (views/, tests/, debug_*)
- PI5_UPDATE_ANLEITUNG.md aktualisiert
- start.sh aktualisiert
- Fix-Scripts erstellt: fix_esp8266_ip.sh, diagnose_pi5_performance.sh

ESP8266 läuft jetzt unter: 192.168.2.20
Pi5 Integration bereit für Test!"

# 4. Push zum GitHub
echo ""
echo "📤 Push zu GitHub..."
git push origin main

echo ""
echo "✅ Git Update abgeschlossen!"
echo ""
echo "🔥 NÄCHSTER SCHRITT: ESP8266 FLASHEN"
echo "================================"
echo ""
echo "🔧 ESP8266 Firmware anpassen:"
echo "1. Arduino IDE öffnen"
echo "2. esp8266_dual_hx711_simple.ino laden"  
echo "3. Zeile 61 ändern:"
echo '   IPAddress staticIP(192, 168, 2, 20);  // NEUE IP!'
echo ""
echo "4. Flashen: Ctrl+U"
echo "5. Serial Monitor prüfen (115200 baud)"
echo "6. ESP8266 sollte zeigen: 'Static IP: 192.168.2.20'"
echo ""
echo "🌐 Nach dem Flash testen:"
echo "  curl http://192.168.2.20/"
echo "  curl http://192.168.2.20/live-values-data"
echo ""
echo "🎯 Dann Pi5 Integration testen: ./start.sh"