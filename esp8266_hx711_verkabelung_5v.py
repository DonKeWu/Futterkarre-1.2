#!/usr/bin/env python3
"""
ESP8266-HX711 Stromversorgungs-Leitfaden
Korrekte 5V-Verkabelung für HX711-Module
"""

print("🔌 ESP8266-HX711 STROMVERSORGUNGS-LEITFADEN")
print("=" * 50)
print()

print("⚡ PROBLEM IDENTIFIZIERT:")
print("   • HX711 benötigt 5V (nicht 3.3V)")
print("   • Bei 3.3V: Keine LED, keine Kommunikation")
print()

print("🔧 KORREKTE VERKABELUNG:")
print()
print("ESP8266 → HX711:")
print("├── VIN (5V)  → VCC  (HX711 Stromversorgung)")
print("├── GND       → GND  (Gemeinsame Masse)")
print("├── D6        → DT   (Data)")
print("└── D7        → SCK  (Clock)")
print()

print("📋 VERKABELUNGS-CHECKLISTE:")
print("□ 1. ESP8266 VIN-Pin mit HX711 VCC verbinden")
print("□ 2. ESP8266 GND-Pin mit HX711 GND verbinden")  
print("□ 3. ESP8266 D6-Pin mit HX711 DT verbinden")
print("□ 4. ESP8266 D7-Pin mit HX711 SCK verbinden")
print("□ 5. Wägezelle 4 Drähte an HX711 E+/E-/A+/A-")
print()

print("⚠️  WICHTIGE HINWEISE:")
print("   • ESP8266 VIN gibt 5V weiter (vom USB/Netzteil)")
print("   • NICHT 3V3-Pin verwenden für HX711!")
print("   • HX711 LED sollte nach Verkabelung leuchten")
print("   • Logik-Pins (D6/D7) bleiben 3.3V-kompatibel")
print()

print("🧪 TEST NACH VERKABELUNG:")
print("   1. HX711 LED leuchtet → Stromversorgung OK")
print("   2. ESP8266 neu starten")
print("   3. Status prüfen: curl http://192.168.2.20/status")
print("   4. weight_available sollte 'true' werden")
print()

print("🎯 ESP8266 PIN-LAYOUT:")
print("   ┌─────────────────────┐")
print("   │ ESP8266 NodeMCU     │")
print("   │                     │")
print("   │ VIN ●          ● 3V3│ ← NICHT für HX711!")
print("   │ GND ●          ● GND│")
print("   │  D6 ●          ● D7 │")
print("   │     ●          ●    │")
print("   └─────────────────────┘")
print()
print("   VIN → HX711 VCC (5V)")
print("   GND → HX711 GND")
print("   D6  → HX711 DT")
print("   D7  → HX711 SCK")