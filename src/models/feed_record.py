"""
Feed Record Model
Represents a feeding record with weight measurement
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FeedRecord:
    """
    Data class representing a feed measurement record
    
    Attributes:
        record_id: Unique identifier for the record
        horse_id: ID of the horse being fed
        feed_type: Type of feed (Heu, Heulage, Pellets)
        weight: Weight of feed in kg
        timestamp: When the measurement was taken
        notes: Additional notes (optional)
    """
    record_id: Optional[int]
    horse_id: int
    feed_type: str
    weight: float
    timestamp: datetime
    notes: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert feed record to dictionary for CSV storage"""
        return {
            'record_id': self.record_id,
            'horse_id': self.horse_id,
            'feed_type': self.feed_type,
            'weight': f"{self.weight:.2f}",
            'timestamp': self.timestamp.isoformat(),
            'notes': self.notes or ''
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FeedRecord':
        """Create feed record from dictionary (from CSV)"""
        return cls(
            record_id=int(data['record_id']) if data.get('record_id') else None,
            horse_id=int(data['horse_id']),
            feed_type=str(data['feed_type']),
            weight=float(data['weight']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            notes=str(data['notes']) if data.get('notes') else None
        )
    
    def __str__(self) -> str:
        """String representation of the feed record"""
        return f"{self.feed_type}: {self.weight:.2f}kg for Horse {self.horse_id} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
