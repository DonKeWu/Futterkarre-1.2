#!/bin/bash
# Einfaches Futterkarre Start-Script - findet automatisch das richtige Verzeichnis

# Farben für Terminal-Output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚜 Futterkarre Auto-Finder & Starter${NC}"
echo "========================================"

# Finde das Projektverzeichnis automatisch
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR=""

# 1. Prüfe aktuelles Verzeichnis des Scripts
if [ -f "$SCRIPT_DIR/main.py" ]; then
    PROJECT_DIR="$SCRIPT_DIR"
    echo -e "${GREEN}✅ Projekt gefunden im Script-Verzeichnis${NC}"
# 2. Prüfe typische Pfade
elif [ -f "/home/daniel/Dokumente/HOF/Futterwagen/Python/Futterkarre/main.py" ]; then
    PROJECT_DIR="/home/daniel/Dokumente/HOF/Futterwagen/Python/Futterkarre"
    echo -e "${GREEN}✅ Projekt gefunden in HOF-Verzeichnis${NC}"
elif [ -f "/home/daniel/Projekte/Futterkarre/main.py" ]; then
    PROJECT_DIR="/home/daniel/Projekte/Futterkarre"
    echo -e "${GREEN}✅ Projekt gefunden in Projekte-Verzeichnis${NC}"
else
    echo -e "${RED}❌ Futterkarre-Projekt nicht gefunden!${NC}"
    echo "Suche nach main.py in Home-Verzeichnis..."
    FOUND_PATH=$(find /home/daniel -name "main.py" -path "*/Futterkarre*" 2>/dev/null | head -1)
    if [ -n "$FOUND_PATH" ]; then
        PROJECT_DIR="$(dirname "$FOUND_PATH")"
        echo -e "${GREEN}✅ Projekt automatisch gefunden: $PROJECT_DIR${NC}"
    else
        echo -e "${RED}❌ Kein Futterkarre-Projekt gefunden!${NC}"
        exit 1
    fi
fi

# Wechsel zum Projektverzeichnis
cd "$PROJECT_DIR"
echo -e "${BLUE}📂 Arbeitsverzeichnis: $PROJECT_DIR${NC}"

# Git Status prüfen
echo -e "${BLUE}📋 Git Status prüfen...${NC}"
if git status &>/dev/null; then
    git status --porcelain
    
    # Unkommittierte Änderungen sichern (falls vorhanden)
    if [[ -n $(git status --porcelain) ]]; then
        echo -e "${BLUE}💾 Lokale Änderungen gefunden - Sicherung erstellen...${NC}"
        git stash push -m "Auto-Stash vor Git-Pull $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    # Git Pull ausführen
    echo -e "${BLUE}⬇️  Git Pull von GitHub...${NC}"
    git pull origin main
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Git Pull erfolgreich${NC}"
    else
        echo -e "${RED}❌ Git Pull fehlgeschlagen${NC}"
        echo "Versuche trotzdem zu starten..."
    fi
else
    echo -e "${BLUE}ℹ️  Kein Git-Repository - starte direkt${NC}"
fi

# 2 Sekunden warten für Benutzer-Feedback
sleep 2

# Display-Variable setzen für GUI
export DISPLAY=:0

# Hauptanwendung starten
echo -e "${GREEN}🚀 Futterkarre wird gestartet...${NC}"
echo "========================================"

# Python-Anwendung starten
python3 main.py

# Exit-Code prüfen
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Anwendung normal beendet${NC}"
else
    echo -e "${RED}❌ Anwendung mit Fehler beendet (Exit-Code: $?)${NC}"
    echo "Drücke Enter zum Fortfahren..."
    read
fi