import sys

if sys.platform.startswith("linux") and not "anaconda" in sys.executable.lower():
    from hx711_multi import HX711

    # Passe die Pins und Kalibrierwerte an dein Setup an!
    dout_pins = [5, 6, 13, 19]  # DOUT der vier HX711
    sck_pin = 26                # Gemeinsamer SCK
    scales = [1, 1, 1, 1]       # Ersetze durch deine Skalenfaktoren
    offsets = [0, 0, 0, 0]      # Ersetze durch deine Offsets

    hx = HX711(
        dout_pins=dout_pins,
        sck_pin=sck_pin,
        channel_A_gain=128,
        channel_select='A'
    )
    hx.set_scale(scales)
    hx.set_offset(offsets)

else:
    HX711 = None  # Dummy für Simulation
    hx = None

def lese_gewicht_hx711():
    """Liest das Gesamtgewicht (Summe aller Zellen)"""
    if hx is None:
        raise RuntimeError("HX711 nicht verfügbar!")
    werte = hx.read_all()
    return sum(werte)

def lese_einzelzellwerte_hx711():
    """Liest die Werte aller vier Zellen einzeln"""
    if hx is None:
        raise RuntimeError("HX711 nicht verfügbar!")
    return hx.read_all()
