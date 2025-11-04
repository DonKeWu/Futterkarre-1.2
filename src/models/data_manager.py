"""
Data Manager
Handles CSV-based data persistence for horses and feed records
"""
import csv
import os
from datetime import datetime
from typing import List, Optional
from .horse import Horse
from .feed_record import FeedRecord
import config.settings as settings


class DataManager:
    """
    Manages data persistence using CSV files
    Handles CRUD operations for horses and feed records
    """
    
    def __init__(self):
        """Initialize data manager and ensure data directory exists"""
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        self._ensure_csv_files()
    
    def _ensure_csv_files(self):
        """Create CSV files with headers if they don't exist"""
        # Horses CSV
        if not os.path.exists(settings.HORSES_CSV):
            with open(settings.HORSES_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['horse_id', 'name', 'breed', 'age', 'weight', 'notes'])
                writer.writeheader()
        
        # Feed records CSV
        if not os.path.exists(settings.FEED_RECORDS_CSV):
            with open(settings.FEED_RECORDS_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['record_id', 'horse_id', 'feed_type', 'weight', 'timestamp', 'notes'])
                writer.writeheader()
    
    # Horse management methods
    def get_all_horses(self) -> List[Horse]:
        """Retrieve all horses from CSV"""
        horses = []
        try:
            with open(settings.HORSES_CSV, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    horses.append(Horse.from_dict(row))
        except FileNotFoundError:
            pass
        return horses
    
    def get_horse_by_id(self, horse_id: int) -> Optional[Horse]:
        """Get a specific horse by ID"""
        horses = self.get_all_horses()
        for horse in horses:
            if horse.horse_id == horse_id:
                return horse
        return None
    
    def add_horse(self, horse: Horse) -> bool:
        """Add a new horse to the database"""
        try:
            # Check if ID already exists
            if self.get_horse_by_id(horse.horse_id):
                return False
            
            with open(settings.HORSES_CSV, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['horse_id', 'name', 'breed', 'age', 'weight', 'notes'])
                writer.writerow(horse.to_dict())
            return True
        except Exception as e:
            print(f"Error adding horse: {e}")
            return False
    
    def update_horse(self, horse: Horse) -> bool:
        """Update an existing horse"""
        try:
            horses = self.get_all_horses()
            updated = False
            
            for i, h in enumerate(horses):
                if h.horse_id == horse.horse_id:
                    horses[i] = horse
                    updated = True
                    break
            
            if not updated:
                return False
            
            # Write back all horses
            with open(settings.HORSES_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['horse_id', 'name', 'breed', 'age', 'weight', 'notes'])
                writer.writeheader()
                for h in horses:
                    writer.writerow(h.to_dict())
            return True
        except Exception as e:
            print(f"Error updating horse: {e}")
            return False
    
    def delete_horse(self, horse_id: int) -> bool:
        """Delete a horse from the database"""
        try:
            horses = self.get_all_horses()
            horses = [h for h in horses if h.horse_id != horse_id]
            
            with open(settings.HORSES_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['horse_id', 'name', 'breed', 'age', 'weight', 'notes'])
                writer.writeheader()
                for h in horses:
                    writer.writerow(h.to_dict())
            return True
        except Exception as e:
            print(f"Error deleting horse: {e}")
            return False
    
    def get_next_horse_id(self) -> int:
        """Get the next available horse ID"""
        horses = self.get_all_horses()
        if not horses:
            return 1
        return max(h.horse_id for h in horses) + 1
    
    # Feed record management methods
    def get_all_feed_records(self, horse_id: Optional[int] = None) -> List[FeedRecord]:
        """
        Retrieve all feed records, optionally filtered by horse_id
        """
        records = []
        try:
            with open(settings.FEED_RECORDS_CSV, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    record = FeedRecord.from_dict(row)
                    if horse_id is None or record.horse_id == horse_id:
                        records.append(record)
        except FileNotFoundError:
            pass
        return records
    
    def add_feed_record(self, record: FeedRecord) -> bool:
        """Add a new feed record"""
        try:
            # Auto-assign record ID if not set
            if record.record_id is None:
                record.record_id = self._get_next_record_id()
            
            with open(settings.FEED_RECORDS_CSV, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['record_id', 'horse_id', 'feed_type', 'weight', 'timestamp', 'notes'])
                writer.writerow(record.to_dict())
            return True
        except Exception as e:
            print(f"Error adding feed record: {e}")
            return False
    
    def _get_next_record_id(self) -> int:
        """Get the next available record ID"""
        records = self.get_all_feed_records()
        if not records:
            return 1
        return max(r.record_id for r in records if r.record_id is not None) + 1
    
    def get_feed_records_by_date_range(self, start_date: datetime, end_date: datetime, 
                                        horse_id: Optional[int] = None) -> List[FeedRecord]:
        """Get feed records within a date range"""
        all_records = self.get_all_feed_records(horse_id)
        return [r for r in all_records if start_date <= r.timestamp <= end_date]
