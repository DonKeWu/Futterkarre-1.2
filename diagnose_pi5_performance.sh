#!/bin/bash
# 🔍 Pi5 Performance-Diagnose bei ESP8266-Integration

echo "🔍 Pi5 Performance-Diagnose..."
echo "================================"

# System-Auslastung prüfen
echo "📊 CPU & Speicher:"
top -bn1 | grep -E "(Cpu|KiB Mem|KiB Swap)" | head -3

echo ""
echo "📊 Aktive Python-Prozesse:"
ps aux | grep python | grep -v grep

echo ""
echo "📊 Speicher-intensive Prozesse:"
ps aux --sort=-%mem | head -10

echo ""
echo "📊 Disk I/O:"
iostat -x 1 1 | tail -n +4

echo ""
echo "📊 Netzwerk-Aktivität:"
netstat -i

echo ""
echo "🔥 Temperatur:"
if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
    temp=$(cat /sys/class/thermal/thermal_zone0/temp)
    echo "CPU: $((temp/1000))°C"
    if [ $((temp/1000)) -gt 70 ]; then
        echo "⚠️  CPU-Temperatur hoch! Kühlkörper/Lüfter prüfen!"
    fi
fi

echo ""
echo "💾 Speicherplatz:"
df -h | grep -E "(Filesystem|/dev/)"

echo ""
echo "🚀 Systemdienste:"
systemctl --failed

echo ""
echo "📝 Letzte Kernel-Meldungen:"
dmesg | tail -10

echo ""
echo "🔧 Pi5-Optimierung Empfehlungen:"
echo "1. Unnötige Dienste stoppen: sudo systemctl disable bluetooth"
echo "2. GPU-Memory reduzieren: gpu_mem=64 in /boot/config.txt"  
echo "3. Swap vergrößern falls < 2GB RAM: sudo dphys-swapfile"
echo "4. Journal-Logs begrenzen: sudo journalctl --vacuum-size=50M"