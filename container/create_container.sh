#!/bin/bash
# Futterkarre LXC Container 109 Setup für Proxmox
# Ausführen auf Proxmox-Server: bash create_container.sh

echo "🚀 Futterkarre Container 109 wird erstellt..."

# Container erstellen
pct create 109 /var/lib/vz/template/cache/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname futterkarre-api \
  --cores 1 \
  --memory 512 \
  --swap 512 \
  --rootfs local-lvm:4 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.2.230/24,gw=192.168.2.1 \
  --nameserver 192.168.2.1 \
  --onboot 1 \
  --unprivileged 1

# Container starten
echo "📦 Container wird gestartet..."
pct start 109

# Warten bis Container bereit ist
sleep 10

echo "✅ Container 109 (futterkarre-api) erfolgreich erstellt!"
echo "🌐 IP-Adresse: 192.168.2.230"
echo "📋 Nächster Schritt: bash setup_futterkarre.sh"