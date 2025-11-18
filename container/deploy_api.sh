#!/bin/bash
# Deployment Script - Futterkarre API in Container 109 kopieren und starten
# Ausführen auf Proxmox: bash deploy_api.sh

echo "📦 Futterkarre API wird in Container 109 deployed..."

# API-Dateien kopieren
pct push 109 app.py /opt/futterkarre/api/app.py
pct exec 109 -- chown futterkarre:futterkarre /opt/futterkarre/api/app.py
pct exec 109 -- chmod +x /opt/futterkarre/api/app.py

# Service starten
pct exec 109 -- systemctl start futterkarre-api
pct exec 109 -- systemctl status futterkarre-api

echo "✅ Deployment abgeschlossen!"
echo "🌐 API verfügbar unter: http://192.168.2.230:5000"
echo "📊 Dashboard: http://192.168.2.230:5000/"
echo "🔌 Pi5 Endpoint: http://192.168.2.230:5000/api/fuetterung"