#!/bin/bash

# ==============================================================================
# Futterkarre Git-Update und Auto-Start Script
# Aktualisiert das Projekt von Git und startet die Anwendung
# ==============================================================================

echo "🚀 Futterkarre Git-Update & Start Script v1.5.4"
echo "=================================================="

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Projekt-Pfade (automatisch erkannt - funktioniert überall!)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$PROJECT_DIR"
MAIN_SCRIPT="$PROJECT_DIR/main.py"

echo -e "${BLUE}📁 Projekt-Verzeichnis: $PROJECT_DIR${NC}"

# Schritt 1: Ins Projekt-Verzeichnis wechseln
echo -e "\n${YELLOW}📂 Wechsle ins Projekt-Verzeichnis...${NC}"
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Fehler: Projekt-Verzeichnis '$PROJECT_DIR' existiert nicht!${NC}"
    echo -e "${YELLOW}💡 Möchtest du das Projekt klonen? (j/n)${NC}"
    read -r clone_choice
    if [ "$clone_choice" = "j" ] || [ "$clone_choice" = "J" ]; then
        echo -e "${BLUE}📥 Klone Futterkarre-Projekt...${NC}"
        cd /home/daniel
        git clone https://github.com/DonKeWu/Futterkarre.git
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Projekt erfolgreich geklont!${NC}"
        else
            echo -e "${RED}❌ Fehler beim Klonen!${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Abgebrochen - kein Projekt-Verzeichnis!${NC}"
        exit 1
    fi
fi

cd "$PROJECT_DIR" || {
    echo -e "${RED}❌ Fehler: Kann nicht ins Verzeichnis '$PROJECT_DIR' wechseln!${NC}"
    exit 1
}
echo -e "${GREEN}✅ Im Projekt-Verzeichnis: $(pwd)${NC}"

# Schritt 2: Git-Updates holen
echo -e "\n${YELLOW}📡 Hole Git-Updates...${NC}"
echo -e "${BLUE}🔄 git fetch origin main${NC}"
git fetch origin main

echo -e "${BLUE}🔄 git pull origin main${NC}"
git pull origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Git-Update erfolgreich!${NC}"
else
    echo -e "${YELLOW}⚠️  Git-Update mit Warnungen (wird trotzdem fortgesetzt)${NC}"
fi

# Schritt 3: System-Dependencies prüfen (KEIN Virtual Environment!)
echo -e "\n${YELLOW}🐍 Prüfe System-Python Dependencies...${NC}"

# PyQt5 über APT installieren (Pi5-optimiert)
if ! dpkg -l | grep -q python3-pyqt5; then
    echo -e "${YELLOW}📦 Installiere PyQt5 über APT (Pi5-optimiert)...${NC}"
    sudo apt update
    sudo apt install -y python3-pyqt5 python3-pyqt5-dev
    echo -e "${GREEN}✅ PyQt5 installiert!${NC}"
else
    echo -e "${GREEN}✅ PyQt5 bereits verfügbar${NC}"
fi

# Hardware-Pakete über pip3 --user
echo -e "${YELLOW}� Installiere Hardware-Dependencies...${NC}"
pip3 install --user RPi.GPIO spidev

echo -e "${GREEN}✅ Alle Dependencies bereit (System-Python)!${NC}"

# Schritt 5: Berechtigungen prüfen
echo -e "\n${YELLOW}🔐 Prüfe Berechtigungen...${NC}"
if [ -f "$MAIN_SCRIPT" ]; then
    echo -e "${GREEN}✅ main.py gefunden${NC}"
else
    echo -e "${RED}❌ Fehler: main.py nicht gefunden in $MAIN_SCRIPT${NC}"
    exit 1
fi

# Schritt 6: Anwendung starten
echo -e "\n${YELLOW}🚀 Starte Futterkarre-Anwendung...${NC}"
echo -e "${BLUE}💻 Befehl: python main.py${NC}"
echo -e "${GREEN}🔴 Roter EXIT-Button verfügbar für Notfälle!${NC}"
echo -e "${YELLOW}📋 Logs werden angezeigt...${NC}"
echo ""

# Anwendung mit System-Python starten (KEIN .venv!)
echo -e "${BLUE}🐍 Starte mit System-Python (einfach & direkt)${NC}"
python3 main.py

# Schritt 7: Nach dem Beenden
echo -e "\n${YELLOW}👋 Futterkarre-Anwendung beendet${NC}"
echo -e "${BLUE}📊 Exit Code: $?${NC}"

# Optional: Logs anzeigen
echo -e "\n${YELLOW}📋 Möchtest du die letzten Log-Einträge sehen? (j/n)${NC}"
read -r show_logs
if [ "$show_logs" = "j" ] || [ "$show_logs" = "J" ]; then
    if [ -d "logs" ]; then
        echo -e "${BLUE}📄 Letzte Log-Einträge:${NC}"
        find logs -name "*.log" -exec tail -10 {} \; 2>/dev/null || echo -e "${YELLOW}Keine Logs gefunden${NC}"
    else
        echo -e "${YELLOW}Kein logs/ Verzeichnis gefunden${NC}"
    fi
fi

echo -e "\n${GREEN}🎯 Script beendet. Bis zum nächsten Mal! 👋${NC}"