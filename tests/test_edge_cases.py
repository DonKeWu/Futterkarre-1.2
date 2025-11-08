#!/usr/bin/env python3
"""
Test-Script für Edge Cases der CSV-Validierung
"""

import os
import tempfile
from utils.csv_validator import CSVValidator

def create_test_csv(filename, content):
    """Erstellt temporäre Test-CSV"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def test_edge_cases():
    print("🧪 CSV Edge Cases Test...")
    
    # Test 1: Komplett kaputte CSV
    print("\n1️⃣ Test: Völlig kaputte CSV")
    broken_csv = """Box,Name,Gewicht,Alter
1,"Eddi,500,10
2,Luna""50kg",8
3,Star,gewicht,alter
,,,
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(broken_csv)
        temp_file = f.name
    
    try:
        validator = CSVValidator()
        result = validator.validate_csv_file(temp_file, 'pferde')
        print(f"   Resultat: {result['status']}")
        print(f"   Gültige Zeilen: {result['valid_rows']}")
        print(f"   Fehler: {result['error_count']}")
        print(f"   Warnungen: {result['warning_count']}")
    finally:
        os.unlink(temp_file)
    
    # Test 2: Datei existiert nicht
    print("\n2️⃣ Test: Datei existiert nicht")
    result = validator.validate_csv_file('nonexistent.csv', 'pferde')
    print(f"   Resultat: {result['status']}")
    print(f"   Message: {result.get('message', 'Kein Message')}")
    
    # Test 3: Leere Datei
    print("\n3️⃣ Test: Leere CSV-Datei")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("")
        temp_file = f.name
    
    try:
        result = validator.validate_csv_file(temp_file, 'pferde')
        print(f"   Resultat: {result['status']}")
        print(f"   Message: {result.get('message', 'Kein Message')}")
    finally:
        os.unlink(temp_file)
    
    # Test 4: Nur Header
    print("\n4️⃣ Test: Nur CSV-Header")
    header_only = "Box,Name,Gewicht,Alter\n"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(header_only)
        temp_file = f.name
    
    try:
        result = validator.validate_csv_file(temp_file, 'pferde')
        print(f"   Resultat: {result['status']}")
        print(f"   Gültige Zeilen: {result['valid_rows']}")
    finally:
        os.unlink(temp_file)
    
    # Test 5: Ungültiger Typ
    print("\n5️⃣ Test: Ungültiger CSV-Typ")
    result = validator.validate_csv_file('pferde.csv', 'invalid_type')
    print(f"   Resultat: {result['status']}")
    print(f"   Message: {result.get('message', 'Kein Message')}")
    
    print("\n🎉 Edge Cases Test abgeschlossen!")

if __name__ == "__main__":
    test_edge_cases()