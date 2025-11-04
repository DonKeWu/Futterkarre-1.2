"""
Scale Interface
Abstract base class for weight scale implementations
"""
from abc import ABC, abstractmethod
from typing import Optional


class ScaleInterface(ABC):
    """
    Abstract interface for weight scale hardware
    Allows for different implementations (real HX711, simulated, etc.)
    """
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the scale hardware
        Returns True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def tare(self) -> bool:
        """
        Tare (zero) the scale
        Returns True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_weight(self) -> Optional[float]:
        """
        Get current weight reading in kg
        Returns weight as float or None if error
        """
        pass
    
    @abstractmethod
    def calibrate(self, known_weight: float) -> bool:
        """
        Calibrate the scale with a known weight
        Args:
            known_weight: The known weight in kg
        Returns True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """
        Clean up hardware resources
        """
        pass
    
    @abstractmethod
    def is_ready(self) -> bool:
        """
        Check if scale is ready for measurement
        Returns True if ready, False otherwise
        """
        pass
