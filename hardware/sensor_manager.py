# hardware/sensor_manager.py - VEREINFACHTE VERSION mit WeightManager
from hardware.weight_manager import get_weight_manager

class SmartSensorManager:
    """
    Legacy-Wrapper für WeightManager
    Wird schrittweise durch direkten WeightManager-Zugriff ersetzt
    """
    
    def __init__(self):
        self.weight_manager = get_weight_manager()
    
    def read_weight(self) -> float:
        """Liest Gewicht über WeightManager"""
        return self.weight_manager.read_weight()
