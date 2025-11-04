"""
HX711 Scale Implementation
Real hardware implementation for HX711 weight sensor
"""
from typing import Optional
from .scale_interface import ScaleInterface
import config.settings as settings


class HX711Scale(ScaleInterface):
    """
    Implementation of ScaleInterface for HX711 weight sensor
    Requires RPi.GPIO and hx711 library
    """
    
    def __init__(self):
        """Initialize HX711 scale with configuration from settings"""
        self.hx = None
        self.reference_unit = settings.HX711_REFERENCE_UNIT
        self.initialized = False
        
    def initialize(self) -> bool:
        """Initialize the HX711 sensor"""
        try:
            # Import HX711 library (only available on Raspberry Pi)
            from hx711 import HX711
            
            # Initialize HX711 with data and clock pins
            self.hx = HX711(
                dout_pin=settings.HX711_DATA_PIN,
                pd_sck_pin=settings.HX711_CLOCK_PIN
            )
            
            # Set reference unit for calibration
            self.hx.set_reference_unit(self.reference_unit)
            
            # Reset and tare
            self.hx.reset()
            self.hx.tare()
            
            self.initialized = True
            return True
            
        except ImportError as e:
            print(f"HX711 library not available: {e}")
            print("Please install with: pip install hx711")
            return False
        except Exception as e:
            print(f"Error initializing HX711: {e}")
            return False
    
    def tare(self) -> bool:
        """Tare (zero) the scale"""
        if not self.initialized or self.hx is None:
            return False
        
        try:
            self.hx.tare(times=settings.TARE_SAMPLES)
            return True
        except Exception as e:
            print(f"Error taring scale: {e}")
            return False
    
    def get_weight(self) -> Optional[float]:
        """Get current weight reading in kg"""
        if not self.initialized or self.hx is None:
            return None
        
        try:
            # Get average of multiple readings for stability
            weight = self.hx.get_weight(times=settings.MEASUREMENT_SAMPLES)
            
            # Convert to kg and round to specified decimals
            weight_kg = weight / 1000.0  # Assuming raw reading is in grams
            weight_kg = round(weight_kg, settings.WEIGHT_DECIMALS)
            
            # Ensure non-negative weight
            return max(0.0, weight_kg)
            
        except Exception as e:
            print(f"Error reading weight: {e}")
            return None
    
    def calibrate(self, known_weight: float) -> bool:
        """
        Calibrate the scale with a known weight
        Args:
            known_weight: The known weight in kg
        """
        if not self.initialized or self.hx is None:
            return False
        
        try:
            # Get current raw reading
            raw_value = self.hx.get_value(times=settings.MEASUREMENT_SAMPLES)
            
            # Calculate new reference unit
            # reference_unit = raw_value / (known_weight * 1000)  # Convert kg to grams
            self.reference_unit = raw_value / (known_weight * 1000)
            self.hx.set_reference_unit(self.reference_unit)
            
            print(f"Calibrated with known weight {known_weight}kg")
            print(f"New reference unit: {self.reference_unit}")
            
            return True
            
        except Exception as e:
            print(f"Error calibrating scale: {e}")
            return False
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if self.hx is not None:
            try:
                self.hx.power_down()
                self.initialized = False
            except Exception as e:
                print(f"Error cleaning up HX711: {e}")
    
    def is_ready(self) -> bool:
        """Check if scale is ready for measurement"""
        if not self.initialized or self.hx is None:
            return False
        
        try:
            # Check if HX711 is responding
            return self.hx.is_ready()
        except Exception:
            return False
