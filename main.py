# main.py
from config.logging_config import setup_logging
setup_logging()
import logging
logger = logging.getLogger(__name__)

import sys
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from models import Pferd, Heulage
from controllers.fuetterung_controller import FütterungController
from hardware.hx711_sensor import HX711Sensor
from views.main_window import MainWindow
from utils.futter_loader import lade_heu_als_dataclasses

heuliste = lade_heu_als_dataclasses("heu_eigen_2025.csv")
if heuliste:
    heu = heuliste[0]  # Erstes Heu-Objekt
    print(heu.name, heu.trockenmasse)


def main():
    # 1. Hardware initialisieren
    sensor = HX711Sensor(data_pin=5, clock_pin=6)  # GPIO-Pins anpassen

    # 2. Heu-Dateien aus dem data-Ordner laden
    heu_namen = finde_heu_dateien()


    # 3. PyQt-Anwendung starten
    app = QApplication(sys.argv)
    window = MainWindow(sensor, heu_namen=heu_namen)
    window.show()

    # 4. Testdaten laden (optional/nur für Entwicklung)
    if True:  # Auf False setzen für Produktivbetrieb
        pferd = Pferd(name="Blitz", gewicht=500, alter=8)
        heulage = Heulage(
            name="Heulage 2024", trockenmasse=60.0, rohprotein=14.0, rohfaser=24.0,
            gesamtzucker=8.0, fruktan=4.0, me_pferd=8.0, pcv_xp=7.0,
            herkunft="Hof B", jahrgang=2024, ph_wert=4.5, siliergrad="gut"
        )
        controller = FütterungController()
        controller.neue_fütterung(pferd, heulage, 2.5, datetime.now())

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
