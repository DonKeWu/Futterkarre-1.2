#!/usr/bin/env python3
"""
Direkter HX711 Test - prüft ob HX711 an GPIO-Pins erkannt wird
Für Pi5 mit HX711 an GPIO 5 (DT) und GPIO 6 (SCK)
"""

import sys
import time
import RPi.GPIO as GPIO

def test_hx711_direct():
    """Direkter Test der HX711 Hardware"""
    print("🔌 DIREKTER HX711 HARDWARE TEST")
    print("=" * 40)
    
    # GPIO Setup
    DT_PIN = 5   # GPIO 5 (Pi5 Pin 29) - Data
    SCK_PIN = 6  # GPIO 6 (Pi5 Pin 31) - Clock
    
    print(f"📋 Konfiguration:")
    print(f"   DT (Data):  GPIO {DT_PIN} (Pin 29)")
    print(f"   SCK (Clock): GPIO {SCK_PIN} (Pin 31)")
    print()
    
    try:
        # GPIO initialisieren
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DT_PIN, GPIO.IN)
        GPIO.setup(SCK_PIN, GPIO.OUT)
        GPIO.output(SCK_PIN, False)
        
        print("✅ GPIO Setup erfolgreich")
        
        # HX711 Bereitschaftstest
        print("🔍 Teste HX711 Bereitschaft...")
        
        ready_count = 0
        not_ready_count = 0
        
        for i in range(10):
            dt_state = GPIO.input(DT_PIN)
            print(f"Messung {i+1}: DT Pin State = {dt_state} ({'READY' if dt_state == 0 else 'NOT READY'})")
            
            if dt_state == 0:
                ready_count += 1
            else:
                not_ready_count += 1
                
            time.sleep(0.1)
        
        print()
        print(f"📊 Ergebnis:")
        print(f"   READY Messungen: {ready_count}/10")
        print(f"   NOT READY Messungen: {not_ready_count}/10")
        
        if ready_count > 0:
            print("✅ HX711 scheint angeschlossen und bereit zu sein!")
            return test_hx711_read_raw(DT_PIN, SCK_PIN)
        else:
            print("❌ HX711 nicht bereit - prüfe Verkabelung:")
            print("   - VCC an 3.3V oder 5V?")
            print("   - GND an Ground?") 
            print("   - DT an GPIO 5?")
            print("   - SCK an GPIO 6?")
            return False
            
    except Exception as e:
        print(f"❌ GPIO Test fehlgeschlagen: {e}")
        return False
    finally:
        GPIO.cleanup()

def test_hx711_read_raw(dt_pin, sck_pin):
    """Versuche Rohdaten vom HX711 zu lesen"""
    print("\n🔬 ROHDATEN-TEST")
    print("=" * 30)
    
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(dt_pin, GPIO.IN)
        GPIO.setup(sck_pin, GPIO.OUT)
        GPIO.output(sck_pin, False)
        
        # Warte auf HX711 bereit
        timeout = 50
        while GPIO.input(dt_pin) == 1 and timeout > 0:
            time.sleep(0.01)
            timeout -= 1
        
        if timeout == 0:
            print("❌ HX711 Timeout - nicht bereit für Datenübertragung")
            return False
        
        print("✅ HX711 bereit für Datenübertragung")
        
        # Lese 24-Bit Wert
        raw_value = 0
        
        for i in range(24):
            GPIO.output(sck_pin, True)
            time.sleep(0.000001)  # 1µs
            
            bit_value = GPIO.input(dt_pin)
            raw_value = (raw_value << 1) | bit_value
            
            GPIO.output(sck_pin, False)
            time.sleep(0.000001)  # 1µs
        
        # Zusätzlicher Clock-Impuls für Gain 128
        GPIO.output(sck_pin, True)
        time.sleep(0.000001)
        GPIO.output(sck_pin, False)
        
        # Konvertiere zu signed integer
        if raw_value & 0x800000:
            raw_value -= 0x1000000
        
        print(f"📊 Rohdaten gelesen: {raw_value}")
        
        if raw_value != 0:
            print("✅ HX711 liefert Daten!")
            return True
        else:
            print("⚠️ HX711 liefert Nullwerte - möglicherweise keine Wägezelle angeschlossen")
            return True
            
    except Exception as e:
        print(f"❌ Rohdaten-Test fehlgeschlagen: {e}")
        return False
    finally:
        GPIO.cleanup()

def test_hx711_library():
    """Teste mit HX711 Python Library (falls installiert)"""
    print("\n📚 HX711 LIBRARY TEST")
    print("=" * 30)
    
    try:
        from hx711 import HX711
        print("✅ HX711 Library importiert")
        
        # HX711 initialisieren
        hx = HX711(dout=5, pd_sck=6)
        hx.set_reading_format("MSB", "MSB")
        hx.reset()
        
        print("✅ HX711 Object erstellt")
        
        # Teste ob bereit
        if hx.is_ready():
            print("✅ HX711 ist bereit")
            
            # Lese mehrere Werte
            for i in range(5):
                try:
                    value = hx.read()
                    print(f"Messung {i+1}: {value}")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Messung {i+1} Fehler: {e}")
            
            return True
        else:
            print("❌ HX711 nicht bereit")
            return False
            
    except ImportError:
        print("⚠️ HX711 Library nicht installiert")
        print("💡 Installiere mit: pip3 install HX711")
        return False
    except Exception as e:
        print(f"❌ Library Test fehlgeschlagen: {e}")
        return False

def main():
    print("🚀 HX711 HARDWARE DETECTION TEST")
    print("=" * 50)
    print("🔌 Erwartete Verkabelung:")
    print("   HX711 VCC  → Pi5 3.3V (Pin 1)")
    print("   HX711 GND  → Pi5 GND  (Pin 6)")  
    print("   HX711 DT   → Pi5 GPIO 5 (Pin 29)")
    print("   HX711 SCK  → Pi5 GPIO 6 (Pin 31)")
    print("=" * 50)
    print()
    
    # Test 1: Direkter GPIO Test
    gpio_ok = test_hx711_direct()
    
    # Test 2: Library Test (falls verfügbar)
    library_ok = test_hx711_library()
    
    # Ergebnis
    print("\n📊 TESTERGEBNIS")
    print("=" * 20)
    print(f"GPIO Test: {'✅ OK' if gpio_ok else '❌ FEHLER'}")
    print(f"Library Test: {'✅ OK' if library_ok else '⚠️ Library fehlt'}")
    
    if gpio_ok:
        print("\n🎉 HX711 Hardware erkannt!")
        if not library_ok:
            print("💡 Installiere Library: sudo bash install_hx711.sh")
    else:
        print("\n❌ HX711 nicht erkannt - prüfe Verkabelung!")

if __name__ == "__main__":
    main()