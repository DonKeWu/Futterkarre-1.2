#!/usr/bin/env python3
"""
Pi5 GPIO Pinout Helper für HX711
Zeigt die verfügbaren GPIO-Pins und empfohlene HX711-Verkabelung
"""

def show_pi5_gpio_pinout():
    """Zeigt Pi5 GPIO Pinout für HX711"""
    print("🔌 RASPBERRY PI 5 GPIO PINOUT FÜR HX711")
    print("=" * 60)
    print()
    
    print("📋 EMPFOHLENE HX711-VERKABELUNG:")
    print("┌─────────────────┬──────────────────┬─────────────────┐")
    print("│ HX711 Pin       │ Pi5 GPIO         │ Pi5 Physical    │")
    print("├─────────────────┼──────────────────┼─────────────────┤")
    print("│ VCC             │ 3.3V             │ Pin 1 oder 17   │")
    print("│ GND             │ Ground           │ Pin 6, 9, 14... │")
    print("│ DT (Data)       │ GPIO 5           │ Pin 29          │")
    print("│ SCK (Clock)     │ GPIO 6           │ Pin 31          │")
    print("└─────────────────┴──────────────────┴─────────────────┘")
    print()
    
    print("🔧 ALTERNATIVE GPIO-PINS (falls GPIO 5/6 belegt):")
    alternatives = [
        ("GPIO 13", "Pin 33", "GPIO 19", "Pin 35"),
        ("GPIO 26", "Pin 37", "GPIO 21", "Pin 40"),
        ("GPIO 20", "Pin 38", "GPIO 16", "Pin 36"),
        ("GPIO 12", "Pin 32", "GPIO 25", "Pin 22")
    ]
    
    print("┌─────────────────┬──────────────────┬─────────────────┬──────────────────┐")
    print("│ DT Option       │ DT Physical      │ SCK Option      │ SCK Physical     │")
    print("├─────────────────┼──────────────────┼─────────────────┼──────────────────┤")
    for dt_gpio, dt_pin, sck_gpio, sck_pin in alternatives:
        print(f"│ {dt_gpio:<15} │ {dt_pin:<16} │ {sck_gpio:<15} │ {sck_pin:<16} │")
    print("└─────────────────┴──────────────────┴─────────────────┴──────────────────┘")
    print()
    
    print("⚠️  WICHTIGE HINWEISE:")
    print("   • Verwende 3.3V (NICHT 5V) für VCC um Pi5 zu schützen")
    print("   • Mehrfach-Grounding für stabile Verbindung")
    print("   • Kurze Kabel (< 30cm) für bessere Signalqualität")
    print("   • HX711 und Wägezelle vor Tests korrekt verkabeln")
    print()
    
    print("🧪 TESTS:")
    print("   1. python3 test_hx711_direct.py     # Hardware-Detection")
    print("   2. sudo bash install_hx711.sh       # Library installieren")
    print("   3. python3 quick_pi5_test.py        # System-Test")

def show_wiring_check():
    """Verkabelungs-Checkliste"""
    print("\n✅ VERKABELUNGS-CHECKLISTE:")
    print("═" * 40)
    
    checklist = [
        "[ ] HX711 VCC → Pi5 3.3V (Pin 1)",
        "[ ] HX711 GND → Pi5 GND (Pin 6)", 
        "[ ] HX711 DT → Pi5 GPIO 5 (Pin 29)",
        "[ ] HX711 SCK → Pi5 GPIO 6 (Pin 31)",
        "[ ] Wägezelle E+ → HX711 E+",
        "[ ] Wägezelle E- → HX711 E-",
        "[ ] Wägezelle A+ → HX711 A+", 
        "[ ] Wägezelle A- → HX711 A-",
        "[ ] Alle Verbindungen fest",
        "[ ] Keine Kurzschlüsse"
    ]
    
    for item in checklist:
        print(f"   {item}")

def main():
    show_pi5_gpio_pinout()
    show_wiring_check()
    
    print("\n🚀 NÄCHSTE SCHRITTE:")
    print("1. Verkabelung nach obiger Tabelle prüfen")
    print("2. python3 test_hx711_direct.py ausführen")
    print("3. Bei Erfolg: sudo bash install_hx711.sh")

if __name__ == "__main__":
    main()