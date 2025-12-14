#!/usr/bin/env python3
"""
Quick Pi5 Test - Schneller Futterkarre Hardware Test
"""

import time
import sys
import subprocess
from datetime import datetime

def quick_test():
    print("⚡ QUICK PI5 FUTTERKARRE TEST")
    print("=" * 40)
    print(f"Zeit: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # 1. Python Test
    print("🐍 Python:", sys.version.split()[0], "✅")
    
    # 2. Wichtige Module
    modules = ['PyQt5', 'serial']
    for mod in modules:
        try:
            __import__(mod)
            print(f"📦 {mod}: ✅")
        except:
            print(f"📦 {mod}: ❌")
    
    # 3. Dateien Check
    files = ['main.py', 'config/settings.json']
    for file in files:
        try:
            with open(file, 'r'):
                print(f"📁 {file}: ✅")
        except:
            print(f"📁 {file}: ❌")
    
    # 4. Hardware Ports
    try:
        result = subprocess.run(['ls', '/dev/ttyUSB*'], capture_output=True)
        if result.returncode == 0:
            print("🔌 USB Ports: ✅")
        else:
            print("🔌 USB Ports: ❌")
    except:
        print("🔌 USB Ports: ❌")
    
    # 5. Memory Check
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if 'MemAvailable' in line:
                    mem_mb = int(line.split()[1]) // 1024
                    status = "✅" if mem_mb > 500 else "⚠️"
                    print(f"💾 RAM frei: {mem_mb}MB {status}")
                    break
    except:
        print("💾 RAM: ❌")
    
    # 6. Futterkarre Import Test
    try:
        from config.app_config import AppConfig
        print("🎯 Futterkarre Config: ✅")
    except Exception as e:
        print(f"🎯 Futterkarre Config: ❌ ({str(e)[:30]})")
    
    try:
        from hardware.sensor_manager import SmartSensorManager
        print("⚙️ Hardware Manager: ✅")
    except Exception as e:
        print(f"⚙️ Hardware Manager: ❌ ({str(e)[:30]})")
    
    print()
    print("🏁 Quick Test abgeschlossen!")

if __name__ == "__main__":
    quick_test()