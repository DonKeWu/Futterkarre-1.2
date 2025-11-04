"""
Horse Model
Represents a horse in the stable management system
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Horse:
    """
    Data class representing a horse
    
    Attributes:
        horse_id: Unique identifier for the horse
        name: Name of the horse
        breed: Breed of the horse (optional)
        age: Age of the horse in years (optional)
        weight: Current weight of the horse in kg (optional)
        notes: Additional notes about the horse (optional)
    """
    horse_id: int
    name: str
    breed: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    notes: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert horse to dictionary for CSV storage"""
        return {
            'horse_id': self.horse_id,
            'name': self.name,
            'breed': self.breed or '',
            'age': self.age or '',
            'weight': self.weight or '',
            'notes': self.notes or ''
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Horse':
        """Create horse from dictionary (from CSV)"""
        return cls(
            horse_id=int(data['horse_id']),
            name=str(data['name']),
            breed=str(data['breed']) if data.get('breed') else None,
            age=int(data['age']) if data.get('age') and str(data['age']).strip() else None,
            weight=float(data['weight']) if data.get('weight') and str(data['weight']).strip() else None,
            notes=str(data['notes']) if data.get('notes') else None
        )
    
    def __str__(self) -> str:
        """String representation of the horse"""
        return f"{self.name} (ID: {self.horse_id})"
