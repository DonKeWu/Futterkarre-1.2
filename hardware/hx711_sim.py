# hardware/hx711_sim.py - VEREINFACHTE WORKFLOW-SIMULATION
import random
import sys

# Simulation-Steuerung
USE_SIMULATION = False

# Workflow-Simulation - FESTE WERTE für Testing
class WorkflowSimulation:
    def __init__(self):
        self.karre_gewicht = 0.0           # Startgewicht (leer)
        self.entnahme_pro_pferd = 4.5      # Entnahme pro Pferd (fest)
        self.ist_beladen = False           # Karre-Status (leer starten)
        
    def get_weight(self):
        """Gibt aktuelles Simulationsgewicht zurück mit kleinen Schwankungen"""
        if not self.ist_beladen:
            return 0.0
        # Kleine realistische Schwankungen
        schwankung = random.uniform(-0.1, 0.1)
        return max(0.0, self.karre_gewicht + schwankung)
    
    def pferd_gefuettert(self):
        """Automatische 4.5kg Entnahme bei 'Weiter'-Button"""
        self.karre_gewicht -= self.entnahme_pro_pferd
        if self.karre_gewicht <= 0:
            self.karre_gewicht = 0.0
            self.ist_beladen = False
        print(f"Simulation: 4.5kg entnommen, Rest: {self.karre_gewicht:.1f}kg")
    
    def karre_beladen(self, zusatz_gewicht=35.0):
        """Realistisches Beladen - addiert zum vorhandenen Gewicht"""
        self.karre_gewicht += zusatz_gewicht
        self.ist_beladen = True
        print(f"Simulation: +{zusatz_gewicht}kg geladen, Gesamt: {self.karre_gewicht:.1f}kg")
    
    def reset_karre(self):
        """Karre komplett entleeren (für Tests)"""
        self.karre_gewicht = 0.0
        self.ist_beladen = False
        print("Simulation: Karre komplett entleert")

# Globale Workflow-Simulation
_workflow_sim = WorkflowSimulation()

def setze_simulation(enabled: bool):
    """Schaltet Simulation ein/aus"""
    global USE_SIMULATION
    USE_SIMULATION = enabled
    print(f"HX711 Simulation: {'Ein' if enabled else 'Aus'}")

def ist_simulation_aktiv():
    """Prüft ob HX711-Simulation aktiv ist"""
    return USE_SIMULATION

def simuliere_gewicht():
    """Workflow-realistische Gewichtssimulation"""
    return _workflow_sim.get_weight()

def pferd_gefuettert():
    """Wird vom 'Weiter'-Button aufgerufen"""
    _workflow_sim.pferd_gefuettert()

def karre_beladen(zusatz_gewicht=35.0):
    """Wird vom 'Beladen bestätigen'-Button aufgerufen"""
    _workflow_sim.karre_beladen(zusatz_gewicht)

def reset_karre():
    """Karre komplett entleeren (für Tests)"""
    _workflow_sim.reset_karre()

def lese_einzelzellen():
    """Simuliert 4 einzelne Wägezellen für Debugging"""
    if USE_SIMULATION:
        gewicht = _workflow_sim.get_weight()
        # Gewicht auf 4 Zellen aufteilen
        basis = gewicht / 4.0
        return [round(basis + random.uniform(-0.5, 0.5), 2) for _ in range(4)]
    else:
        return [0.0, 0.0, 0.0, 0.0]

def lese_gewicht():
    """Kompatibilitätsfunktion für alten Code"""
    if USE_SIMULATION:
        return simuliere_gewicht()
    return 0.0


