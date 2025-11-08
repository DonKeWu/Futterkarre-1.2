# test_csv_validator.py - Schnelltest für CSV-Validierung
import logging
from utils.csv_validator import csv_validator
from utils.futter_loader import lade_pferde_als_dataclasses, lade_heu_als_dataclasses, lade_heulage_als_dataclasses

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def test_csv_validation():
    """Testet die neue CSV-Validierung"""
    print("🧪 CSV-Validierung Test gestartet...\n")
    
    # 1. Pferde CSV testen
    print("📊 Teste Pferde CSV...")
    pferde = lade_pferde_als_dataclasses('pferde.csv')
    print(f"✅ {len(pferde)} Pferde geladen")
    if pferde:
        print(f"   Beispiel: {pferde[0].name} (Box {pferde[0].box}, {pferde[0].gewicht}kg)\n")
    
    # 2. Heu CSV testen
    print("🌾 Teste Heu CSV...")
    heu_liste = lade_heu_als_dataclasses('heu_eigen_2025.csv')
    print(f"✅ {len(heu_liste)} Heu-Einträge geladen")
    if heu_liste:
        heu = heu_liste[0]
        print(f"   Beispiel: {heu.name} - {heu.rohprotein}% Protein, {heu.fruktan}% Fruktan\n")
    
    # 3. Heulage CSV testen
    print("🥬 Teste Heulage CSV...")
    heulage_liste = lade_heulage_als_dataclasses('heulage_eigen_2025.csv')
    print(f"✅ {len(heulage_liste)} Heulage-Einträge geladen")
    if heulage_liste:
        heulage = heulage_liste[0]
        print(f"   Beispiel: {heulage.name} - {heulage.rohprotein}% Protein, pH {heulage.ph_wert}\n")
    
    # 4. Direkter Validator-Test
    print("🔍 Teste CSV-Validator direkt...")
    from utils.csv_validator import CSVValidator
    validator = CSVValidator()
    result = validator.validate_csv_file('data/pferde.csv', 'pferde')
    print(f"   Validierung: {'✅ Erfolgreich' if result['success'] else '❌ Fehlgeschlagen'}")
    print(f"   Gültige Zeilen: {result['valid_rows']}")
    print(f"   Warnungen: {result['warning_count']}")
    print(f"   Fehler: {result['error_count']}")
    
    print("\n🎉 CSV-Validierung Test abgeschlossen!")

if __name__ == '__main__':
    test_csv_validation()