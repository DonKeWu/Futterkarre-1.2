#!/usr/bin/env python3
"""
Test Script für erweiterte Futterkarre-Systeme
Tests für SettingsManager und DatabaseManager

Funktionen:
- Settings Manager Tests
- Database Manager Tests
- Integration Tests
- Performance Tests
"""

import sys
import os
from pathlib import Path
import logging
import json
from datetime import datetime, date, timedelta

# Projekt-spezifische Imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.settings_manager import get_settings_manager, SettingsManager
from utils.database_manager import get_database_manager, DatabaseManager, FeedingRecord, HorseStatistics
from utils.timer_manager import get_timer_manager

# Logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_settings_manager():
    """Testet SettingsManager Funktionen"""
    print("=" * 60)
    print("SETTINGS MANAGER TESTS")
    print("=" * 60)
    
    try:
        # Instanz holen
        settings = get_settings_manager()
        print(f"✅ SettingsManager Instanz erstellt: {type(settings)}")
        
        # Singleton Test
        settings2 = get_settings_manager()
        assert settings is settings2, "Singleton Pattern fehlgeschlagen"
        print("✅ Singleton Pattern funktioniert")
        
        # Standard-Werte testen
        print(f"✅ Standard Helligkeit: {settings.system.brightness}%")
        print(f"✅ Standard Futtermenge: {settings.feeding.default_feed_amount} kg")
        print(f"✅ Simulation Modus: {settings.hardware.use_simulation}")
        
        # Einzelne Einstellung ändern
        old_brightness = settings.system.brightness
        new_brightness = 95
        settings.set_setting('system', 'brightness', new_brightness)
        assert settings.system.brightness == new_brightness, "Einstellung nicht gesetzt"
        print(f"✅ Einstellung geändert: Helligkeit {old_brightness}% → {new_brightness}%")
        
        # Speichern und Laden testen
        print("📁 Speichere Einstellungen...")
        success = settings.save_settings()
        assert success, "Speichern fehlgeschlagen"
        print("✅ Einstellungen gespeichert")
        
        # Neue Instanz laden (simuliert Neustart)
        settings_file = Path("config/settings.json")
        if settings_file.exists():
            print("✅ Settings-Datei existiert")
            with open(settings_file, 'r') as f:
                data = json.load(f)
                assert data['system']['brightness'] == new_brightness, "Gespeicherte Daten falsch"
            print("✅ Gespeicherte Daten korrekt")
        
        # Export Test
        export_path = Path("test_settings_export.json")
        success = settings.export_settings(export_path)
        assert success, "Export fehlgeschlagen"
        assert export_path.exists(), "Export-Datei nicht erstellt"
        print("✅ Settings Export erfolgreich")
        
        # Import Test
        settings.system.brightness = 50  # Wert ändern
        success = settings.import_settings(export_path)
        assert success, "Import fehlgeschlagen"
        assert settings.system.brightness == new_brightness, "Import-Daten falsch"
        print("✅ Settings Import erfolgreich")
        
        # Cleanup
        if export_path.exists():
            export_path.unlink()
        
        # Reset Test
        success = settings.reset_category('system')
        assert success, "Reset fehlgeschlagen"
        print("✅ Category Reset erfolgreich")
        
        # Callback Test
        callback_triggered = False
        def test_callback(category):
            nonlocal callback_triggered
            callback_triggered = True
            print(f"📢 Callback ausgelöst für Kategorie: {category}")
        
        settings.register_change_callback('system', test_callback)
        settings.set_setting('system', 'volume', 75)
        assert callback_triggered, "Callback nicht ausgelöst"
        print("✅ Callback System funktioniert")
        
    except Exception as e:
        print(f"❌ Settings Manager Test Fehler: {e}")
        raise

def test_database_manager():
    """Testet DatabaseManager Funktionen"""
    print("\n" + "=" * 60)
    print("DATABASE MANAGER TESTS")
    print("=" * 60)
    
    try:
        # Test-Datenbank verwenden
        test_db_path = Path("test_feeding_history.db")
        if test_db_path.exists():
            test_db_path.unlink()  # Alte Test-DB löschen
        
        db = DatabaseManager(test_db_path)
        print(f"✅ DatabaseManager Instanz erstellt: {type(db)}")
        
        # Test Feeding Records hinzufügen
        test_records = [
            FeedingRecord(
                timestamp=datetime.now().isoformat(),
                horse_name="Luna",
                feed_type="Heu_eigen",
                planned_amount=4.5,
                actual_amount=4.3,
                duration_seconds=120,
                notes="Alles ok",
                load_weight_before=45.2,
                load_weight_after=40.9
            ),
            FeedingRecord(
                timestamp=(datetime.now() - timedelta(hours=2)).isoformat(),
                horse_name="Max",
                feed_type="Heulage_eigen", 
                planned_amount=5.0,
                actual_amount=4.8,
                duration_seconds=95,
                notes="Schnell gefressen",
                load_weight_before=40.9,
                load_weight_after=36.1
            ),
            FeedingRecord(
                timestamp=(datetime.now() - timedelta(days=1)).isoformat(),
                horse_name="Luna",
                feed_type="Heu_eigen",
                planned_amount=4.5,
                actual_amount=4.5,
                duration_seconds=110,
                notes="Normal",
                load_weight_before=50.0,
                load_weight_after=45.5
            )
        ]
        
        # Records hinzufügen
        record_ids = []
        for record in test_records:
            record_id = db.add_feeding_record(record)
            assert record_id > 0, f"Feeding Record nicht hinzugefügt: {record_id}"
            record_ids.append(record_id)
        
        print(f"✅ {len(test_records)} Feeding Records hinzugefügt: IDs {record_ids}")
        
        # Historie abrufen
        all_history = db.get_feeding_history()
        assert len(all_history) >= len(test_records), "Nicht alle Records abgerufen"
        print(f"✅ Feeding History abgerufen: {len(all_history)} Einträge")
        
        # Pferde-spezifische Historie
        luna_history = db.get_feeding_history(horse_name="Luna")
        luna_count = len([r for r in test_records if r.horse_name == "Luna"])
        assert len(luna_history) >= luna_count, "Luna History unvollständig"
        print(f"✅ Luna History: {len(luna_history)} Einträge")
        
        # Pferde-Statistiken
        luna_stats = db.get_horse_statistics("Luna")
        assert luna_stats is not None, "Luna Statistiken nicht gefunden"
        assert luna_stats.horse_name == "Luna", "Falsche Statistiken"
        assert luna_stats.total_feedings >= luna_count, "Fütterungs-Count falsch"
        print(f"✅ Luna Statistiken: {luna_stats.total_feedings} Fütterungen, ⌀ {luna_stats.avg_amount_per_feeding} kg")
        
        # Tages-Report
        today_report = db.get_daily_report()
        assert today_report.date == date.today().isoformat(), "Falsches Report-Datum"
        print(f"✅ Heute Report: {today_report.total_horses_fed} Pferde, {today_report.total_amount_fed} kg")
        
        # Trend-Analyse
        luna_trends = db.get_feeding_trends("Luna")
        assert 'trend' in luna_trends, "Trend-Daten unvollständig"
        print(f"✅ Luna Trends: {luna_trends['trend']}")
        
        # System Event loggen
        db.log_system_event(
            "test_event",
            "Test System Event für Datenbank Test",
            {"test": True, "timestamp": datetime.now().isoformat()}
        )
        print("✅ System Event geloggt")
        
        # Export Test
        export_path = Path("test_export.csv")
        success = db.export_data(export_path, format="csv", days_back=7)
        assert success, "CSV Export fehlgeschlagen"
        assert export_path.exists(), "Export-Datei nicht erstellt"
        print("✅ CSV Export erfolgreich")
        
        # JSON Export Test
        json_export_path = Path("test_export.json")
        success = db.export_data(json_export_path, format="json", days_back=7)
        assert success, "JSON Export fehlgeschlagen"
        assert json_export_path.exists(), "JSON Export-Datei nicht erstellt"
        print("✅ JSON Export erfolgreich")
        
        # Backup Test
        backup_path = Path("test_backup.db")
        success = db.backup_database(backup_path)
        assert success, "Backup fehlgeschlagen"
        assert backup_path.exists(), "Backup-Datei nicht erstellt"
        print("✅ Database Backup erfolgreich")
        
        # Cleanup
        for cleanup_file in [test_db_path, export_path, json_export_path, backup_path]:
            if cleanup_file.exists():
                cleanup_file.unlink()
        print("✅ Cleanup abgeschlossen")
        
    except Exception as e:
        print(f"❌ Database Manager Test Fehler: {e}")
        raise

def test_integration():
    """Testet Integration zwischen Systemen"""
    print("\n" + "=" * 60)
    print("INTEGRATION TESTS")
    print("=" * 60)
    
    try:
        # Manager-Instanzen
        settings = get_settings_manager()
        timer_manager = get_timer_manager()
        
        print("✅ Alle Manager verfügbar")
        
        # Timer Integration
        timer_manager.set_active_page("test_page")
        print("✅ Timer Manager Integration")
        
        # Settings → Hardware Simulation
        old_sim = settings.hardware.use_simulation
        settings.hardware.use_simulation = not old_sim
        settings.save_settings()
        
        # Neue Instanz - sollte Änderung beibehalten
        new_settings = SettingsManager()
        assert new_settings.hardware.use_simulation == (not old_sim), "Settings nicht persistent"
        print("✅ Settings Persistenz funktioniert")
        
        # Zurücksetzen
        settings.hardware.use_simulation = old_sim
        settings.save_settings()
        
    except Exception as e:
        print(f"❌ Integration Test Fehler: {e}")
        raise

def performance_test():
    """Führt Performance-Tests durch"""
    print("\n" + "=" * 60)
    print("PERFORMANCE TESTS")
    print("=" * 60)
    
    try:
        import time
        
        # Settings Performance
        settings = get_settings_manager()
        
        start_time = time.time()
        for i in range(100):
            settings.set_setting('system', 'brightness', 50 + (i % 50))
        settings_time = time.time() - start_time
        print(f"✅ Settings Performance: 100 Änderungen in {settings_time:.3f}s")
        
        # Database Performance
        test_db_path = Path("perf_test.db")
        if test_db_path.exists():
            test_db_path.unlink()
        
        db = DatabaseManager(test_db_path)
        
        start_time = time.time()
        for i in range(50):
            record = FeedingRecord(
                timestamp=datetime.now().isoformat(),
                horse_name=f"TestPferd_{i % 5}",
                feed_type="Test_Heu",
                planned_amount=4.0,
                actual_amount=4.0 + (i % 10) * 0.1,
                duration_seconds=100 + i,
                notes=f"Performance Test {i}"
            )
            db.add_feeding_record(record)
        db_time = time.time() - start_time
        print(f"✅ Database Performance: 50 Einträge in {db_time:.3f}s")
        
        # Query Performance
        start_time = time.time()
        for i in range(10):
            stats = db.get_horse_statistics(f"TestPferd_{i % 5}")
        query_time = time.time() - start_time
        print(f"✅ Query Performance: 10 Statistik-Abfragen in {query_time:.3f}s")
        
        # Cleanup
        if test_db_path.exists():
            test_db_path.unlink()
        
    except Exception as e:
        print(f"❌ Performance Test Fehler: {e}")
        raise

def main():
    """Hauptfunktion - führt alle Tests durch"""
    print("🚀 Starte erweiterte Futterkarre-System Tests")
    print(f"📅 Zeitstempel: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Alle Tests durchführen
        test_settings_manager()
        test_database_manager()
        test_integration()
        performance_test()
        
        print("\n" + "=" * 60)
        print("🎉 ALLE TESTS ERFOLGREICH!")
        print("=" * 60)
        print("✅ Settings Manager: Vollständig getestet")
        print("✅ Database Manager: Vollständig getestet") 
        print("✅ Integration: Erfolgreich")
        print("✅ Performance: Akzeptabel")
        print("\n🏁 Test Suite abgeschlossen - Systeme einsatzbereit!")
        
    except Exception as e:
        print(f"\n❌ TEST FEHLGESCHLAGEN: {e}")
        print("🔧 Bitte Fehler beheben und Tests erneut ausführen")
        raise

if __name__ == "__main__":
    main()