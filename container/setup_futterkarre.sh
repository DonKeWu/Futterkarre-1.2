#!/bin/bash
# Futterkarre API Setup im LXC Container 109
# Ausführen im Container: pct exec 109 -- bash /root/setup_futterkarre.sh

echo "🛠️ Futterkarre API wird im Container installiert..."

# System updaten
apt update && apt upgrade -y

# Python und Dependencies installieren
apt install -y python3 python3-pip python3-venv sqlite3 curl wget

# Futterkarre Benutzer erstellen
useradd -m -s /bin/bash futterkarre
usermod -aG sudo futterkarre

# Verzeichnisse erstellen
mkdir -p /opt/futterkarre/{api,data,backup,logs}
chown -R futterkarre:futterkarre /opt/futterkarre

# Python Virtual Environment
cd /opt/futterkarre
sudo -u futterkarre python3 -m venv venv
sudo -u futterkarre /opt/futterkarre/venv/bin/pip install --upgrade pip

# Flask und Dependencies installieren
sudo -u futterkarre /opt/futterkarre/venv/bin/pip install \
    flask \
    flask-sqlalchemy \
    flask-cors \
    requests \
    schedule \
    python-dateutil

# SQLite Datenbank initialisieren
sudo -u futterkarre sqlite3 /opt/futterkarre/data/futterkarre.db ".databases"

# Systemd Service erstellen
cat > /etc/systemd/system/futterkarre-api.service << 'EOF'
[Unit]
Description=Futterkarre API Service
After=network.target

[Service]
Type=simple
User=futterkarre
Group=futterkarre
WorkingDirectory=/opt/futterkarre/api
ExecStart=/opt/futterkarre/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Service aktivieren (wird erst gestartet wenn app.py vorhanden)
systemctl daemon-reload
systemctl enable futterkarre-api

echo "✅ Container-Setup abgeschlossen!"
echo "📁 Futterkarre-Root: /opt/futterkarre"
echo "🗄️ Datenbank: /opt/futterkarre/data/futterkarre.db"
echo "🌐 Service: futterkarre-api (bereit für app.py)"