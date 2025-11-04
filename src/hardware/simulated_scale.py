"""
Simulated Scale Implementation
Mock implementation for development and testing without hardware
"""
import random
import time
from typing import Optional
from .scale_interface import ScaleInterface
import config.settings as settings


class SimulatedScale(ScaleInterface):
    """
    Simulated scale for testing without hardware
    Provides realistic weight readings for development
    """
    
    def __init__(self):
        """Initialize simulated scale"""
        self.initialized = False
        self.tared = False
        self.current_weight = 0.0
        self.last_tare_time = 0
        
    def initialize(self) -> bool:
        """Initialize the simulated scale"""
        print("Initializing simulated scale...")
        self.initialized = True
        self.tared = False
        self.current_weight = random.uniform(0.0, 2.0)  # Initial random weight
        return True
    
    def tare(self) -> bool:
        """Tare (zero) the scale"""
        if not self.initialized:
            return False
        
        print("Taring scale...")
        time.sleep(0.5)  # Simulate taring delay
        self.current_weight = 0.0
        self.tared = True
        self.last_tare_time = time.time()
        return True
    
    def get_weight(self) -> Optional[float]:
        """
        Get current weight reading in kg
        Simulates realistic weight variations
        """
        if not self.initialized:
            return None
        
        # Add small random variation to simulate sensor noise
        noise = random.uniform(-0.01, 0.01)
        weight = max(0.0, self.current_weight + noise)
        
        # Round to specified decimals
        weight = round(weight, settings.WEIGHT_DECIMALS)
        
        return weight
    
    def calibrate(self, known_weight: float) -> bool:
        """
        Calibrate the scale with a known weight
        In simulation, just acknowledge the calibration
        """
        if not self.initialized:
            return False
        
        print(f"Simulated calibration with {known_weight}kg")
        return True
    
    def cleanup(self):
        """Clean up resources (nothing to do in simulation)"""
        self.initialized = False
        print("Simulated scale cleaned up")
    
    def is_ready(self) -> bool:
        """Check if scale is ready"""
        return self.initialized
    
    # Additional methods for simulation control
    def set_weight(self, weight: float):
        """
        Set the simulated weight (for testing)
        Args:
            weight: Weight to set in kg
        """
        self.current_weight = max(0.0, weight)
    
    def add_weight(self, additional: float):
        """
        Add weight to the scale (simulate placing item)
        Args:
            additional: Additional weight in kg
        """
        self.current_weight = max(0.0, self.current_weight + additional)
    
    def remove_weight(self, amount: float):
        """
        Remove weight from the scale (simulate removing item)
        Args:
            amount: Amount of weight to remove in kg
        """
        self.current_weight = max(0.0, self.current_weight - amount)
