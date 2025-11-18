#!/bin/bash
# FUTTERKARRE CONTAINER 109 - KOMPLETT-SETUP
# Proxmox Host: Dell Wyse (192.168.2.10)
# Container IP: 192.168.2.109  
# Pi5 IP: 192.168.2.230

echo "🐴 FUTTERKARRE CONTAINER 109 - SETUP"
echo "===================================="
echo "Proxmox Host: Dell Wyse (192.168.2.10)"
echo "Container IP: 192.168.2.230"
echo "Pi5 IP: 192.168.2.17"
echo ""

# === CONTAINER ERSTELLEN ===
echo "📦 Container 109 erstellen..."
pct create 109 /var/lib/vz/template/cache/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname futterkarre-api \
  --cores 1 \
  --memory 1024 \
  --swap 512 \
  --rootfs local-lvm:8 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.2.230/24,gw=192.168.2.1 \
  --nameserver 192.168.2.1 \
  --onboot 1 \
  --unprivileged 1

pct start 109
echo "⏳ Container startet (15 Sekunden warten)..."
sleep 15

# === SYSTEM KONFIGURIEREN ===
echo "🛠️ System Setup im Container..."
pct exec 109 -- bash -c "
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv sqlite3 curl nano htop
useradd -m -s /bin/bash futterkarre
usermod -aG sudo futterkarre
mkdir -p /opt/futterkarre/{api,data,backup,logs}
chown -R futterkarre:futterkarre /opt/futterkarre
cd /opt/futterkarre
sudo -u futterkarre python3 -m venv venv
sudo -u futterkarre /opt/futterkarre/venv/bin/pip install --upgrade pip
sudo -u futterkarre /opt/futterkarre/venv/bin/pip install flask flask-sqlalchemy flask-cors requests
sudo -u futterkarre touch /opt/futterkarre/data/futterkarre.db
"

# === SYSTEMD SERVICE ===
echo "⚙️ Systemd Service konfigurieren..."
pct exec 109 -- bash -c "
cat > /etc/systemd/system/futterkarre-api.service << 'EOF'
[Unit]
Description=Futterkarre API - Pi5 Datensammler
After=network.target

[Service]
Type=simple
User=futterkarre
Group=futterkarre
WorkingDirectory=/opt/futterkarre/api
Environment=PATH=/opt/futterkarre/venv/bin
ExecStart=/opt/futterkarre/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable futterkarre-api
"

echo ""
echo "✅ SETUP ABGESCHLOSSEN!"
echo ""
echo "📋 NÄCHSTE SCHRITTE:"
echo "1. pct push 109 app.py /opt/futterkarre/api/app.py"
echo "2. pct exec 109 -- systemctl start futterkarre-api"
echo ""
echo "🌐 ZUGRIFF:"
echo "   Dashboard: http://192.168.2.230:5000/"
echo "   Pi5 API:   http://192.168.2.230:5000/api/fuetterung"
echo ""
echo "🔧 WARTUNG:"
echo "   Status:    pct exec 109 -- systemctl status futterkarre-api"
echo "   Logs:      pct exec 109 -- tail -f /opt/futterkarre/logs/api.log"
echo "   Shell:     pct enter 109"