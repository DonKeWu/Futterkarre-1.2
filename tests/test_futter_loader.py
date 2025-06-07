# tests/test_futter_loader.py
import unittest
from utils.futter_loader import lade_heu_als_dataclasses


class TestFutterLoader(unittest.TestCase):
    def test_lade_heu(self):
        heuliste = lade_heu_als_dataclasses(dateiname)
        if heuliste:
            heu = heuliste[0]  # Das erste Heu-Objekt aus der Liste
        self.assertIsNotNone(heu)
