# HX711 Pin-Konfiguration für 4 Wägezellen (Raspberry Pi 5)
# Optimierte Konfiguration mit separaten SCK-Pins für bessere Performance

# Pin-Zuordnung (siehe raspberry_pi5_hardware.md):
hx711_configs = [
    {'dt_pin': 5, 'sck_pin': 6, 'name': 'Vorne_Links'},     # GPIO 5/6
    {'dt_pin': 13, 'sck_pin': 19, 'name': 'Vorne_Rechts'},  # GPIO 13/19  
    {'dt_pin': 26, 'sck_pin': 21, 'name': 'Hinten_Links'},  # GPIO 26/21
    {'dt_pin': 20, 'sck_pin': 16, 'name': 'Hinten_Rechts'}  # GPIO 20/16
]

# Kalibrierungswerte (müssen für jede Zelle separat bestimmt werden)
scales = [1.0, 1.0, 1.0, 1.0]       # Skalenfaktoren
offsets = [0, 0, 0, 0]               # Nullpunkt-Offsets

# Hardware-Konfiguration: Standard HX711 Library für 4-Sensor Setup
# Zukünftige Erweiterung: Multi-HX711 Library für bessere Performance
# from hx711_multi import HX711  # Option für Multi-Sensor Hardware
from hx711 import HX711  # Standard HX711 Library (aktuell verwendet)

# HX711 Konfiguration für 4 Wägezellen (Option 1: 4x separate Module)
# Jede Wägezelle hat ihr eigenes HX711-Modul für maximale Zuverlässigkeit

try:
    from hx711 import HX711
    HX711_AVAILABLE = True
except ImportError:
    HX711 = None
    HX711_AVAILABLE = False

# 4x separate HX711-Module (je 1 pro Wägezelle):
hx711_configs = [
    {
        'dt_pin': 5, 'sck_pin': 6, 
        'name': 'Vorne_Links',
        'position': 'VL',
        'scale': 1.0,
        'offset': 0
    },
    {
        'dt_pin': 13, 'sck_pin': 19,
        'name': 'Vorne_Rechts', 
        'position': 'VR',
        'scale': 1.0,
        'offset': 0
    },
    {
        'dt_pin': 26, 'sck_pin': 21,
        'name': 'Hinten_Links',
        'position': 'HL', 
        'scale': 1.0,
        'offset': 0
    },
    {
        'dt_pin': 20, 'sck_pin': 16,
        'name': 'Hinten_Rechts',
        'position': 'HR',
        'scale': 1.0,
        'offset': 0
    }
]

class SingleHX711:
    """Ein einzelnes HX711-Modul für eine Wägezelle"""
    
    def __init__(self, dt_pin, sck_pin, config):
        if not HX711_AVAILABLE:
            raise RuntimeError("HX711 Library nicht verfügbar!")
            
        self.hx = HX711(dt_pin, sck_pin)
        self.config = config
        self.scale = config['scale']
        self.offset = config['offset']
        
        # HX711 initialisieren
        self.hx.set_reading_format("MSB", "MSB")
        self.hx.reset()
        
    def read_weight(self, samples=3):
        """Liest das Gewicht der Wägezelle"""
        try:
            raw_value = self.hx.read_average(samples)
            return (raw_value - self.offset) * self.scale
        except Exception as e:
            print(f"Fehler bei {self.config['name']}: {e}")
            return 0.0
            
    def tare(self):
        """Setzt Nullpunkt (Tara)"""
        try:
            self.hx.tare()
            print(f"✅ {self.config['name']}: Nullpunkt gesetzt")
        except Exception as e:
            print(f"❌ {self.config['name']}: Tara-Fehler: {e}")
            
    def calibrate(self, known_weight):
        """Kalibriert die Wägezelle mit bekanntem Gewicht"""
        try:
            print(f"Lege {known_weight}kg auf {self.config['name']} und drücke Enter...")
            input()
            
            raw_value = self.hx.read_average(10)
            if raw_value != 0:
                self.scale = known_weight / raw_value
                self.config['scale'] = self.scale
                print(f"✅ {self.config['name']} kalibriert: {self.scale:.6f}")
                return True
            else:
                print(f"❌ Kalibrierung fehlgeschlagen (raw_value = 0)")
                return False
        except Exception as e:
            print(f"❌ Kalibrierungs-Fehler: {e}")
            return False

# HX711-Instanzen (werden bei Initialisierung erstellt)
hx_sensors = []

def init_hx711_sensors():
    """Initialisiert 4x separate HX711-Module für 4 Wägezellen"""
    global hx_sensors
    
    if not HX711_AVAILABLE:
        raise RuntimeError("HX711 Library nicht verfügbar!")
    
    hx_sensors = []
    
    for config in hx711_configs:
        try:
            sensor = SingleHX711(
                dt_pin=config['dt_pin'],
                sck_pin=config['sck_pin'], 
                config=config
            )
            hx_sensors.append(sensor)
            print(f"HX711 {config['name']} erfolgreich initialisiert")
        except Exception as e:
            print(f"Fehler bei HX711 {config['name']}: {e}")

def lese_gewicht_hx711():
    """Liest das Gesamtgewicht aller 4 Wägezellen"""
    if not hx_sensors:
        raise RuntimeError("HX711-Sensoren nicht initialisiert!")
    
    gesamtgewicht = 0.0
    
    for sensor in hx_sensors:
        try:
            gewicht = sensor.read_weight(samples=3)
            gesamtgewicht += gewicht
        except Exception as e:
            print(f"Fehler beim Lesen von {sensor.config['name']}: {e}")
    
    return gesamtgewicht

def lese_einzelzellwerte_hx711():
    """Liest alle 4 Wägezellen einzeln"""
    if not hx_sensors:
        raise RuntimeError("HX711-Sensoren nicht initialisiert!")
    
    gewichte = []
    
    for sensor in hx_sensors:
        try:
            gewicht = sensor.read_weight(samples=3)
            gewichte.append(gewicht)
        except Exception as e:
            print(f"Fehler beim Lesen von {sensor.config['name']}: {e}")
            gewichte.append(0.0)  # Fallback-Wert
    
    return gewichte  # [VL, VR, HL, HR]

def kalibriere_einzelzelle(sensor_index, bekanntes_gewicht):
    """Kalibriert eine spezifische Wägezelle"""
    if sensor_index >= len(hx_sensors):
        raise ValueError(f"Sensor-Index {sensor_index} nicht verfügbar!")
    
    sensor = hx_sensors[sensor_index]
    return sensor.calibrate(bekanntes_gewicht)

def nullpunkt_setzen_alle():
    """Setzt Nullpunkt für alle 4 Wägezellen"""
    print("🔄 Nullpunkt-Kalibrierung: Karren leeren und Enter drücken...")
    input()
    
    for sensor in hx_sensors:
        sensor.tare()

def teste_alle_sensoren():
    """Testet alle HX711-Sensoren auf Funktion"""
    print("🧪 Teste alle 4 HX711-Sensoren...")
    
    for i, sensor in enumerate(hx_sensors):
        try:
            raw_value = sensor.hx.read()
            print(f"✅ Sensor {i+1} ({sensor.config['name']}): {raw_value}")
        except Exception as e:
            print(f"❌ Sensor {i+1} ({sensor.config['name']}): Fehler - {e}")

# Initialisierung beim Import (falls HX711 verfügbar)
try:
    if HX711_AVAILABLE:
        init_hx711_sensors()
        print("🔌 HX711 4-Sensor System initialisiert")
    else:
        hx_sensors = []
        print("⚠️ HX711 Library nicht verfügbar - Simulation verwenden")
except Exception as e:
    print(f"⚠️ HX711-Initialisierung fehlgeschlagen: {e}")
    hx_sensors = []
