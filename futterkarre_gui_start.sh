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

# Virtual Environment aktivieren falls verfügbar
if [ -f "$VENV_PATH/bin/python" ]; then
    # Mit Virtual Environment
    .venv/bin/python main.py
else
    # Fallback auf System Python
    python3 main.py
fi