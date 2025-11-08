#!/bin/bash

# ==============================================================================
# Futterkarre GUI-Start (ohne Terminal-Ausgabe)
# Startet die Anwendung direkt im GUI-Modus
# ==============================================================================

# Dynamischer Projekt-Pfad (wo das Script liegt)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_SCRIPT="$PROJECT_DIR/main.py"

# Ins Projekt-Verzeichnis wechseln
cd "$PROJECT_DIR" || exit 1

# Git-Update im Hintergrund (ohne Ausgabe)
git pull origin main >/dev/null 2>&1

# Direkt mit System-Python starten (KEIN .venv!)
python3 main.py