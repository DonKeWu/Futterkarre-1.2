# hardware/fu_sim.py
import random

USE_SIMULATION = False
current_weight = 100.0  # Realistischeres Startgewicht

def setze_simulation(enabled: bool):
    """Schaltet Fütterungssimulation ein/aus"""
    global USE_SIMULATION
    USE_SIMULATION = enabled
    print(f"Fütterungs-Simulation: {'Ein' if enabled else 'Aus'}")

def simuliere_fuetterung(menge_kg: float = 1.0):
    """Simuliert Fütterung durch Gewichtsreduktion"""
    global current_weight
    if USE_SIMULATION:
        current_weight = max(0, current_weight - menge_kg)
        print(f"Simuliert: {menge_kg}kg gefüttert. Neues Gewicht: {current_weight}kg")
        return current_weight
    return current_weight

def simuliere_nachladen(menge_kg: float = 10.0):
    """Simuliert Nachladen von Futter"""
    global current_weight
    if USE_SIMULATION:
        current_weight += menge_kg
        # Maximalgewicht begrenzen
        current_weight = min(current_weight, 100.0)
        print(f"Simuliert: {menge_kg}kg nachgeladen. Neues Gewicht: {current_weight}kg")
        return current_weight
    return current_weight

def get_sim_weight() -> float:
    """Gibt aktuelles Simulationsgewicht zurück"""
    if USE_SIMULATION:
        # Kleine Schwankungen für Realismus
        schwankung = random.uniform(-0.1, 0.1)
        return max(0, current_weight + schwankung)
    return current_weight

def reset_sim_weight(gewicht: float = 100.0):
    """Setzt Simulationsgewicht zurück"""
    global current_weight
    current_weight = gewicht
    print(f"Simulationsgewicht zurückgesetzt auf: {gewicht}kg")

