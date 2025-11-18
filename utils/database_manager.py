#!/usr/bin/env python3
"""
Database Manager - Persistente Daten-Verwaltung
SQLite-basierte Langzeit-Statistiken für das Futterkarre-System

Funktionen:
- Feeding History (Wer, Was, Wann, Wieviel)
- Horse Statistics (Durchschnitt, Trends, Gewichte)
- Daily/Weekly/Monthly Reports
- Data Export (CSV, JSON)
- Backup/Restore Funktionen
"""

import sqlite3
import logging
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict, field
from contextlib import contextmanager
import threading

# MySQL Import (optional - nur wenn verfügbar)
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class FeedingRecord:
    """Einzelner Fütterungs-Eintrag"""
    id: Optional[int] = None
    timestamp: str = ""
    horse_name: str = ""
    feed_type: str = ""
    planned_amount: float = 0.0
    actual_amount: float = 0.0
    duration_seconds: int = 0
    notes: str = ""
    load_weight_before: float = 0.0
    load_weight_after: float = 0.0

@dataclass
class HorseStatistics:
    """Pferde-Statistiken"""
    horse_name: str = ""
    total_feedings: int = 0
    avg_amount_per_feeding: float = 0.0
    total_amount: float = 0.0
    last_feeding: str = ""
    most_common_feed: str = ""
    feeding_frequency_days: float = 0.0

@dataclass
class DailyReport:
    """Täglicher Report"""
    date: str = ""
    total_horses_fed: int = 0
    total_amount_fed: float = 0.0
    most_active_hour: int = 0
    feed_types_used: List[str] = field(default_factory=list)
    unique_horses: List[str] = field(default_factory=list)

class DatabaseManager:
    """
    Zentrale Datenbank-Verwaltung für persistente Statistiken
    
    Verwaltet:
    - Feeding History mit SQLite
    - Pferde-Statistiken
    - Reports und Trends
    - Export/Import Funktionen
    """
    
    def __init__(self, db_path: Union[str, Path] = "data/feeding_history.db"):
        self.db_path = Path(db_path)
        self._lock = threading.Lock()
        
        # Daten-Ordner erstellen
        self.db_path.parent.mkdir(exist_ok=True)
        
        # MySQL Konfiguration (optional)
        self.mysql_config = {
            'host': '192.168.2.230',
            'port': 3306,
            'user': 'root',
            'password': 'FutterkarreDB2025!',
            'database': 'futterkarre',
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
        
        # MySQL Verfügbarkeit prüfen
        self.mysql_available = self._check_mysql_connection()
        
        # Datenbanken initialisieren
        self.init_database()
        
        logger.info(f"DatabaseManager initialisiert: SQLite={self.db_path}, MySQL={self.mysql_available}")
    
    @contextmanager
    def get_connection(self):
        """Context Manager für SQLite-Datenbankverbindungen"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row  # Dict-like row access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"SQLite Datenbankfehler: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _check_mysql_connection(self) -> bool:
        """Prüft ob MySQL-Verbindung verfügbar ist"""
        if not MYSQL_AVAILABLE:
            logger.info("MySQL-Connector nicht verfügbar")
            return False
            
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            conn.close()
            logger.info("MySQL-Verbindung erfolgreich getestet")
            return True
        except Exception as e:
            logger.info(f"MySQL nicht verfügbar: {e}")
            return False
    
    @contextmanager
    def get_mysql_connection(self):
        """Context Manager für MySQL-Datenbankverbindungen"""
        if not self.mysql_available:
            raise Exception("MySQL nicht verfügbar")
            
        conn = None
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"MySQL Datenbankfehler: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def init_database(self):
        """Initialisiert Datenbank-Schema"""
        try:
            with self.get_connection() as conn:
                # Feeding History Tabelle
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS feeding_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        horse_name TEXT NOT NULL,
                        feed_type TEXT NOT NULL,
                        planned_amount REAL NOT NULL,
                        actual_amount REAL NOT NULL,
                        duration_seconds INTEGER DEFAULT 0,
                        notes TEXT DEFAULT '',
                        load_weight_before REAL DEFAULT 0.0,
                        load_weight_after REAL DEFAULT 0.0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # System Logs Tabelle (für Wartung/Kalibrierung)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS system_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        log_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        data TEXT DEFAULT '',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Indices für Performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_feeding_horse ON feeding_history(horse_name)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_feeding_date ON feeding_history(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_feeding_type ON feeding_history(feed_type)")
                
                conn.commit()
                logger.info("SQLite Datenbank-Schema erfolgreich initialisiert")
                
                # MySQL Synchronisation (falls verfügbar)
                if self.mysql_available:
                    self._sync_master_data_from_mysql()
                
        except Exception as e:
            logger.error(f"Fehler bei Datenbank-Initialisierung: {e}")
            raise
    
    def add_feeding_record(self, record: FeedingRecord) -> int:
        """
        Fügt einen Fütterungs-Eintrag hinzu
        
        Args:
            record: FeedingRecord Objekt
            
        Returns:
            ID des eingefügten Eintrags
        """
        try:
            with self._lock:
                with self.get_connection() as conn:
                    cursor = conn.execute("""
                        INSERT INTO feeding_history (
                            timestamp, horse_name, feed_type, planned_amount,
                            actual_amount, duration_seconds, notes,
                            load_weight_before, load_weight_after
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record.timestamp or datetime.now().isoformat(),
                        record.horse_name,
                        record.feed_type,
                        record.planned_amount,
                        record.actual_amount,
                        record.duration_seconds,
                        record.notes,
                        record.load_weight_before,
                        record.load_weight_after
                    ))
                    
                    conn.commit()
                    record_id = cursor.lastrowid
                    
                    logger.debug(f"Feeding Record hinzugefügt: ID {record_id} für {record.horse_name}")
                    return record_id or -1
                    
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen des Feeding Records: {e}")
            return -1
    
    def get_feeding_history(self, 
                          horse_name: Optional[str] = None,
                          days_back: int = 30,
                          limit: int = 1000) -> List[FeedingRecord]:
        """
        Holt Fütterungs-Historie
        
        Args:
            horse_name: Spezifisches Pferd (None für alle)
            days_back: Tage rückwirkend
            limit: Maximale Anzahl Einträge
            
        Returns:
            Liste von FeedingRecord Objekten
        """
        try:
            with self.get_connection() as conn:
                # Datum-Filter
                since_date = (datetime.now() - timedelta(days=days_back)).isoformat()
                
                if horse_name:
                    cursor = conn.execute("""
                        SELECT * FROM feeding_history 
                        WHERE horse_name = ? AND timestamp >= ?
                        ORDER BY timestamp DESC LIMIT ?
                    """, (horse_name, since_date, limit))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM feeding_history 
                        WHERE timestamp >= ?
                        ORDER BY timestamp DESC LIMIT ?
                    """, (since_date, limit))
                
                records = []
                for row in cursor.fetchall():
                    record = FeedingRecord(
                        id=row['id'],
                        timestamp=row['timestamp'],
                        horse_name=row['horse_name'],
                        feed_type=row['feed_type'],
                        planned_amount=row['planned_amount'],
                        actual_amount=row['actual_amount'],
                        duration_seconds=row['duration_seconds'],
                        notes=row['notes'],
                        load_weight_before=row['load_weight_before'],
                        load_weight_after=row['load_weight_after']
                    )
                    records.append(record)
                
                logger.debug(f"Feeding History abgerufen: {len(records)} Einträge")
                return records
                
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Feeding History: {e}")
            return []
    
    def get_horse_statistics(self, horse_name: str) -> Optional[HorseStatistics]:
        """
        Berechnet Statistiken für ein spezifisches Pferd
        
        Args:
            horse_name: Name des Pferdes
            
        Returns:
            HorseStatistics Objekt oder None
        """
        try:
            with self.get_connection() as conn:
                # Basis-Statistiken
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_feedings,
                        AVG(actual_amount) as avg_amount,
                        SUM(actual_amount) as total_amount,
                        MAX(timestamp) as last_feeding
                    FROM feeding_history 
                    WHERE horse_name = ?
                """, (horse_name,))
                
                row = cursor.fetchone()
                if not row or row['total_feedings'] == 0:
                    return None
                
                # Häufigster Futter-Typ
                cursor = conn.execute("""
                    SELECT feed_type, COUNT(*) as count
                    FROM feeding_history 
                    WHERE horse_name = ?
                    GROUP BY feed_type
                    ORDER BY count DESC
                    LIMIT 1
                """, (horse_name,))
                
                most_common_feed_row = cursor.fetchone()
                most_common_feed = most_common_feed_row['feed_type'] if most_common_feed_row else ""
                
                # Fütterungs-Frequenz (Tage zwischen Fütterungen)
                cursor = conn.execute("""
                    SELECT timestamp FROM feeding_history 
                    WHERE horse_name = ?
                    ORDER BY timestamp DESC
                    LIMIT 2
                """, (horse_name,))
                
                recent_feedings = cursor.fetchall()
                frequency_days = 0.0
                
                if len(recent_feedings) >= 2:
                    try:
                        dt1 = datetime.fromisoformat(recent_feedings[0]['timestamp'])
                        dt2 = datetime.fromisoformat(recent_feedings[1]['timestamp'])
                        frequency_days = (dt1 - dt2).total_seconds() / 86400  # Tage
                    except Exception:
                        pass
                
                stats = HorseStatistics(
                    horse_name=horse_name,
                    total_feedings=row['total_feedings'],
                    avg_amount_per_feeding=round(row['avg_amount'], 2),
                    total_amount=round(row['total_amount'], 2),
                    last_feeding=row['last_feeding'],
                    most_common_feed=most_common_feed,
                    feeding_frequency_days=round(frequency_days, 1)
                )
                
                return stats
                
        except Exception as e:
            logger.error(f"Fehler bei Pferde-Statistiken für {horse_name}: {e}")
            return None
    
    def get_daily_report(self, target_date: Optional[date] = None) -> DailyReport:
        """
        Erstellt Tages-Report
        
        Args:
            target_date: Zieldatum (heute wenn None)
            
        Returns:
            DailyReport Objekt
        """
        if target_date is None:
            target_date = date.today()
        
        try:
            with self.get_connection() as conn:
                date_str = target_date.isoformat()
                start_time = f"{date_str} 00:00:00"
                end_time = f"{date_str} 23:59:59"
                
                # Basis-Statistiken
                cursor = conn.execute("""
                    SELECT 
                        COUNT(DISTINCT horse_name) as unique_horses,
                        COUNT(*) as total_feedings,
                        SUM(actual_amount) as total_amount
                    FROM feeding_history 
                    WHERE timestamp BETWEEN ? AND ?
                """, (start_time, end_time))
                
                row = cursor.fetchone()
                
                # Aktivste Stunde
                cursor = conn.execute("""
                    SELECT 
                        CAST(strftime('%H', timestamp) AS INTEGER) as hour,
                        COUNT(*) as count
                    FROM feeding_history 
                    WHERE timestamp BETWEEN ? AND ?
                    GROUP BY hour
                    ORDER BY count DESC
                    LIMIT 1
                """, (start_time, end_time))
                
                hour_row = cursor.fetchone()
                most_active_hour = hour_row['hour'] if hour_row else 0
                
                # Verwendete Futter-Typen
                cursor = conn.execute("""
                    SELECT DISTINCT feed_type
                    FROM feeding_history 
                    WHERE timestamp BETWEEN ? AND ?
                """, (start_time, end_time))
                
                feed_types = [row['feed_type'] for row in cursor.fetchall()]
                
                # Gefütterte Pferde
                cursor = conn.execute("""
                    SELECT DISTINCT horse_name
                    FROM feeding_history 
                    WHERE timestamp BETWEEN ? AND ?
                """, (start_time, end_time))
                
                unique_horses = [row['horse_name'] for row in cursor.fetchall()]
                
                report = DailyReport(
                    date=date_str,
                    total_horses_fed=row['unique_horses'] or 0,
                    total_amount_fed=round(row['total_amount'] or 0.0, 2),
                    most_active_hour=most_active_hour,
                    feed_types_used=feed_types,
                    unique_horses=unique_horses
                )
                
                return report
                
        except Exception as e:
            logger.error(f"Fehler bei Daily Report für {target_date}: {e}")
            return DailyReport(date=target_date.isoformat())
    
    def export_data(self, 
                   export_path: Union[str, Path],
                   format: str = "csv",
                   days_back: int = 30) -> bool:
        """
        Exportiert Daten in CSV oder JSON
        
        Args:
            export_path: Ziel-Pfad
            format: "csv" oder "json"
            days_back: Tage rückwirkend
            
        Returns:
            True wenn erfolgreich
        """
        try:
            export_path = Path(export_path)
            records = self.get_feeding_history(days_back=days_back, limit=10000)
            
            if format.lower() == "csv":
                import csv
                
                with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Header
                    writer.writerow([
                        'Timestamp', 'Horse_Name', 'Feed_Type', 
                        'Planned_Amount', 'Actual_Amount', 'Duration_Seconds',
                        'Notes', 'Load_Weight_Before', 'Load_Weight_After'
                    ])
                    
                    # Daten
                    for record in records:
                        writer.writerow([
                            record.timestamp, record.horse_name, record.feed_type,
                            record.planned_amount, record.actual_amount, record.duration_seconds,
                            record.notes, record.load_weight_before, record.load_weight_after
                        ])
            
            elif format.lower() == "json":
                data = {
                    'export_info': {
                        'timestamp': datetime.now().isoformat(),
                        'days_back': days_back,
                        'total_records': len(records)
                    },
                    'feeding_records': [asdict(record) for record in records]
                }
                
                with open(export_path, 'w', encoding='utf-8') as jsonfile:
                    json.dump(data, jsonfile, indent=2, ensure_ascii=False)
            
            else:
                logger.error(f"Unbekanntes Export-Format: {format}")
                return False
            
            logger.info(f"Daten exportiert: {len(records)} Einträge nach {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Export fehlgeschlagen: {e}")
            return False
    
    def log_system_event(self, event_type: str, description: str, data: Optional[Dict] = None):
        """
        Loggt System-Events (Kalibrierung, Wartung, etc.)
        
        Args:
            event_type: Art des Events (calibration, maintenance, error, etc.)
            description: Beschreibung
            data: Zusätzliche Daten als Dict
        """
        try:
            with self._lock:
                with self.get_connection() as conn:
                    data_json = json.dumps(data) if data else ""
                    
                    conn.execute("""
                        INSERT INTO system_logs (timestamp, log_type, description, data)
                        VALUES (?, ?, ?, ?)
                    """, (
                        datetime.now().isoformat(),
                        event_type,
                        description,
                        data_json
                    ))
                    
                    conn.commit()
                    logger.debug(f"System Event geloggt: {event_type} - {description}")
                    
        except Exception as e:
            logger.error(f"Fehler beim Loggen von System Event: {e}")
    
    def get_feeding_trends(self, horse_name: str, days: int = 14) -> Dict[str, Any]:
        """
        Analysiert Fütterungs-Trends für ein Pferd
        
        Args:
            horse_name: Name des Pferdes
            days: Anzahl Tage für Analyse
            
        Returns:
            Dict mit Trend-Daten
        """
        try:
            records = self.get_feeding_history(horse_name=horse_name, days_back=days)
            
            if not records:
                return {'trend': 'no_data', 'message': 'Keine Daten verfügbar'}
            
            # Tägliche Mengen berechnen
            daily_amounts = {}
            for record in records:
                record_date = record.timestamp[:10]  # YYYY-MM-DD
                if record_date not in daily_amounts:
                    daily_amounts[record_date] = 0.0
                daily_amounts[record_date] += record.actual_amount
            
            amounts = list(daily_amounts.values())
            
            if len(amounts) < 2:
                return {'trend': 'insufficient_data', 'average': amounts[0] if amounts else 0}
            
            # Trend berechnen (vereinfacht: erste vs. zweite Hälfte)
            mid = len(amounts) // 2
            first_half_avg = sum(amounts[:mid]) / len(amounts[:mid])
            second_half_avg = sum(amounts[mid:]) / len(amounts[mid:])
            
            trend_direction = 'stable'
            trend_percentage = 0.0
            
            if abs(second_half_avg - first_half_avg) > 0.5:  # Threshold 0.5kg
                trend_percentage = ((second_half_avg - first_half_avg) / first_half_avg) * 100
                if trend_percentage > 10:
                    trend_direction = 'increasing'
                elif trend_percentage < -10:
                    trend_direction = 'decreasing'
            
            return {
                'trend': trend_direction,
                'trend_percentage': round(trend_percentage, 1),
                'average_first_half': round(first_half_avg, 2),
                'average_second_half': round(second_half_avg, 2),
                'total_days': len(daily_amounts),
                'daily_amounts': daily_amounts
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Trend-Analyse für {horse_name}: {e}")
            return {'trend': 'error', 'message': str(e)}
    
    def backup_database(self, backup_path: Union[str, Path]) -> bool:
        """Erstellt Backup der Datenbank"""
        try:
            import shutil
            backup_path = Path(backup_path)
            
            if self.db_path.exists():
                shutil.copy2(self.db_path, backup_path)
                logger.info(f"Datenbank-Backup erstellt: {backup_path}")
                return True
            else:
                logger.warning("Datenbank-Datei nicht gefunden für Backup")
                return False
                
        except Exception as e:
            logger.error(f"Backup fehlgeschlagen: {e}")
            return False
    
    def _sync_master_data_from_mysql(self):
        """Lädt Stammdaten (Pferde, Futter) von MySQL zu SQLite"""
        if not self.mysql_available:
            return
            
        try:
            with self.get_mysql_connection() as mysql_conn:
                mysql_cursor = mysql_conn.cursor(dictionary=True)
                
                # Pferde-Daten holen und lokal speichern
                mysql_cursor.execute("SELECT * FROM pferde")
                horses = mysql_cursor.fetchall()
                
                # Futter-Daten holen
                mysql_cursor.execute("SELECT * FROM futter")
                feeds = mysql_cursor.fetchall()
                
                # In lokale SQLite-Tabellen einfügen/aktualisieren
                with self.get_connection() as sqlite_conn:
                    # Pferde-Stammdaten-Tabelle erstellen
                    sqlite_conn.execute("""
                        CREATE TABLE IF NOT EXISTS horses_master (
                            id INTEGER PRIMARY KEY,
                            name TEXT UNIQUE,
                            rasse TEXT,
                            geburtsdatum TEXT,
                            gewicht REAL,
                            besonderheiten TEXT,
                            sync_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Futter-Stammdaten-Tabelle erstellen
                    sqlite_conn.execute("""
                        CREATE TABLE IF NOT EXISTS feeds_master (
                            id INTEGER PRIMARY KEY,
                            name TEXT UNIQUE,
                            typ TEXT,
                            kalorien_pro_kg REAL,
                            preis_pro_kg REAL,
                            lagerbestand_kg REAL,
                            sync_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Pferde synchronisieren
                    for horse in horses:
                        sqlite_conn.execute("""
                            INSERT OR REPLACE INTO horses_master 
                            (id, name, rasse, geburtsdatum, gewicht, besonderheiten)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            horse['id'], horse['name'], horse['rasse'],
                            str(horse['geburtsdatum']), horse['gewicht'], horse['besonderheiten']
                        ))
                    
                    # Futter synchronisieren  
                    for feed in feeds:
                        sqlite_conn.execute("""
                            INSERT OR REPLACE INTO feeds_master
                            (id, name, typ, kalorien_pro_kg, preis_pro_kg, lagerbestand_kg)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            feed['id'], feed['name'], feed['typ'],
                            feed['kalorien_pro_kg'], feed['preis_pro_kg'], feed['lagerbestand_kg']
                        ))
                    
                    sqlite_conn.commit()
                    logger.info(f"Stammdaten synchronisiert: {len(horses)} Pferde, {len(feeds)} Futter")
                    
        except Exception as e:
            logger.error(f"MySQL-Sync fehlgeschlagen: {e}")
    
    def sync_feeding_data_to_mysql(self):
        """Überträgt neue Fütterungsdaten von SQLite zu MySQL"""
        if not self.mysql_available:
            return
            
        try:
            # Ungesyncte Fütterungsdaten aus SQLite holen
            with self.get_connection() as sqlite_conn:
                cursor = sqlite_conn.execute("""
                    SELECT * FROM feeding_history 
                    WHERE id NOT IN (
                        SELECT COALESCE(sqlite_id, 0) FROM sync_status WHERE table_name = 'feeding_history'
                    )
                    ORDER BY timestamp
                """)
                unsynced_records = cursor.fetchall()
            
            if not unsynced_records:
                return
                
            # Zu MySQL übertragen
            with self.get_mysql_connection() as mysql_conn:
                mysql_cursor = mysql_conn.cursor()
                
                for record in unsynced_records:
                    mysql_cursor.execute("""
                        INSERT INTO fuetterungen (pferd_id, futter_id, menge_kg, zeit, notizen)
                        SELECT p.id, f.id, %s, %s, %s
                        FROM pferde p, futter f
                        WHERE p.name = %s AND f.name = %s
                    """, (
                        record['actual_amount'], record['timestamp'],
                        record['notes'], record['horse_name'], record['feed_type']
                    ))
                
                mysql_conn.commit()
                logger.info(f"{len(unsynced_records)} Fütterungsdaten zu MySQL übertragen")
                
        except Exception as e:
            logger.error(f"Feeding-Sync zu MySQL fehlgeschlagen: {e}")
    
    def get_horses_from_master(self) -> List[Dict[str, Any]]:
        """Holt Pferde-Liste aus den Stammdaten (lokal oder MySQL)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM horses_master ORDER BY name")
                return [dict(row) for row in cursor.fetchall()]
        except:
            # Fallback: CSV-Daten oder leere Liste
            logger.warning("Keine Pferde-Stammdaten verfügbar")
            return []
    
    def get_feeds_from_master(self) -> List[Dict[str, Any]]:
        """Holt Futter-Liste aus den Stammdaten (lokal oder MySQL)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM feeds_master ORDER BY name")
                return [dict(row) for row in cursor.fetchall()]
        except:
            # Fallback: CSV-Daten oder leere Liste
            logger.warning("Keine Futter-Stammdaten verfügbar")
            return []

# Globale Instanz
_db_manager_instance: Optional[DatabaseManager] = None

def get_database_manager() -> DatabaseManager:
    """Gibt die globale DatabaseManager-Instanz zurück (Lazy Loading)"""
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager()
    return _db_manager_instance