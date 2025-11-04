"""
Application Controller
Main controller coordinating models, views, and hardware
"""
from datetime import datetime
from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal

from src.models import Horse, FeedRecord, DataManager
from src.hardware import ScaleInterface, HX711Scale, SimulatedScale
import config.settings as settings


class AppController(QObject):
    """
    Main application controller implementing MVC pattern
    Coordinates between data models, hardware, and views
    """
    
    # Qt signals for UI updates
    weight_updated = pyqtSignal(float)  # Emitted when weight changes
    scale_ready = pyqtSignal(bool)  # Emitted when scale status changes
    error_occurred = pyqtSignal(str)  # Emitted on errors
    
    def __init__(self):
        """Initialize controller with data manager and scale"""
        super().__init__()
        self.data_manager = DataManager()
        self.scale: Optional[ScaleInterface] = None
        self._initialize_scale()
    
    def _initialize_scale(self):
        """Initialize the appropriate scale implementation"""
        try:
            if settings.SIMULATION_MODE:
                print("Initializing in SIMULATION mode")
                self.scale = SimulatedScale()
            else:
                print("Initializing HX711 hardware scale")
                self.scale = HX711Scale()
            
            if self.scale.initialize():
                print("Scale initialized successfully")
                self.scale_ready.emit(True)
            else:
                print("Scale initialization failed")
                self.scale_ready.emit(False)
                self.error_occurred.emit("Failed to initialize scale")
                
        except Exception as e:
            print(f"Error initializing scale: {e}")
            self.error_occurred.emit(f"Scale initialization error: {e}")
            self.scale_ready.emit(False)
    
    # Horse management methods
    def get_all_horses(self) -> List[Horse]:
        """Get all horses from database"""
        return self.data_manager.get_all_horses()
    
    def get_horse(self, horse_id: int) -> Optional[Horse]:
        """Get a specific horse by ID"""
        return self.data_manager.get_horse_by_id(horse_id)
    
    def add_horse(self, name: str, breed: str = None, age: int = None, 
                  weight: float = None, notes: str = None) -> bool:
        """
        Add a new horse to the system
        Returns True if successful
        """
        horse_id = self.data_manager.get_next_horse_id()
        horse = Horse(
            horse_id=horse_id,
            name=name,
            breed=breed,
            age=age,
            weight=weight,
            notes=notes
        )
        return self.data_manager.add_horse(horse)
    
    def update_horse(self, horse_id: int, name: str = None, breed: str = None,
                     age: int = None, weight: float = None, notes: str = None) -> bool:
        """
        Update an existing horse
        Only updates provided fields
        """
        horse = self.get_horse(horse_id)
        if not horse:
            return False
        
        if name is not None:
            horse.name = name
        if breed is not None:
            horse.breed = breed
        if age is not None:
            horse.age = age
        if weight is not None:
            horse.weight = weight
        if notes is not None:
            horse.notes = notes
        
        return self.data_manager.update_horse(horse)
    
    def delete_horse(self, horse_id: int) -> bool:
        """Delete a horse from the system"""
        return self.data_manager.delete_horse(horse_id)
    
    # Scale operations
    def tare_scale(self) -> bool:
        """Tare (zero) the scale"""
        if self.scale is None:
            return False
        return self.scale.tare()
    
    def get_current_weight(self) -> Optional[float]:
        """Get current weight from scale"""
        if self.scale is None:
            return None
        
        weight = self.scale.get_weight()
        if weight is not None:
            self.weight_updated.emit(weight)
        return weight
    
    def calibrate_scale(self, known_weight: float) -> bool:
        """Calibrate scale with known weight"""
        if self.scale is None:
            return False
        return self.scale.calibrate(known_weight)
    
    def is_scale_ready(self) -> bool:
        """Check if scale is ready for measurements"""
        if self.scale is None:
            return False
        return self.scale.is_ready()
    
    # Feed record operations
    def record_feeding(self, horse_id: int, feed_type: str, 
                       weight: float, notes: str = None) -> bool:
        """
        Record a feeding event
        Args:
            horse_id: ID of the horse being fed
            feed_type: Type of feed (Heu, Heulage, Pellets)
            weight: Weight of feed in kg
            notes: Optional notes
        """
        # Validate feed type
        if feed_type not in settings.FEED_TYPES:
            self.error_occurred.emit(f"Invalid feed type: {feed_type}")
            return False
        
        # Validate weight
        if weight < settings.MIN_WEIGHT or weight > settings.MAX_WEIGHT:
            self.error_occurred.emit(f"Weight out of range: {weight}kg")
            return False
        
        # Verify horse exists
        if not self.get_horse(horse_id):
            self.error_occurred.emit(f"Horse ID {horse_id} not found")
            return False
        
        # Create and save record
        record = FeedRecord(
            record_id=None,  # Will be auto-assigned
            horse_id=horse_id,
            feed_type=feed_type,
            weight=weight,
            timestamp=datetime.now(),
            notes=notes
        )
        
        return self.data_manager.add_feed_record(record)
    
    def get_feed_history(self, horse_id: Optional[int] = None) -> List[FeedRecord]:
        """Get feeding history, optionally filtered by horse"""
        return self.data_manager.get_all_feed_records(horse_id)
    
    def get_feed_records_by_date(self, start_date: datetime, end_date: datetime,
                                  horse_id: Optional[int] = None) -> List[FeedRecord]:
        """Get feed records within a date range"""
        return self.data_manager.get_feed_records_by_date_range(
            start_date, end_date, horse_id
        )
    
    # Cleanup
    def cleanup(self):
        """Clean up resources on application exit"""
        if self.scale:
            self.scale.cleanup()
