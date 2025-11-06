"""
Futterkarre 1.4.0 - Intelligente Futterwaage für Pferde

Ein PyQt5-basiertes Steuerungssystem für eine mobile Futterwaage zur präzisen 
Pferdefütterung mit Raspberry Pi 5 und HX711-Wägezellen.
"""

__version__ = "1.4.0"
__author__ = "DonKeWu"
__description__ = "Intelligente Futterwaage für Pferde"

# Version auch aus VERSION-Datei laden als Fallback
import os
try:
    version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
    if os.path.exists(version_file):
        with open(version_file, 'r', encoding='utf-8') as f:
            file_version = f.read().strip()
            if file_version != __version__:
                print(f"Warning: Version mismatch - __init__.py: {__version__}, VERSION file: {file_version}")
except Exception as e:
    print(f"Could not read VERSION file: {e}")