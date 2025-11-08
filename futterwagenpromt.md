# Futterwagen-Prompt

**Regeln für die Zusammenarbeit mit dem Raspberry Pi und Ubuntu-Rechner:**

- Du arbeitest auf einem Ubuntu-Rechner.
- Auf dem Ubuntu-Rechner darfst du Dinge direkt ausführen (z.B. Python-Programme, Git-Befehle, Tests).
- Der Raspberry Pi ist nur per SSH erreichbar.
- Du kannst hier auf dem Ubuntu-Rechner direkt Befehle ausführen.
- Für alles, was auf dem Pi laufen soll, musst du mir die passenden Terminal-Befehle liefern, die ich dann per SSH auf dem Pi ausführe.
- Du hast keinen direkten Zugriff auf den Pi, sondern nur über das Terminal und SSH.
- Schreibe die Befehle klar und vollständig auf, damit ich sie einfach kopieren und ausführen kann.

**Repository-Workflow:**
- Das gesamte Projekt-Repository soll vollständig auf GitHub hochgeladen werden.
- Der Raspberry Pi holt sich das Repository per Befehl direkt aus GitHub (z.B. mit `git clone` oder `git pull`).
- Änderungen werden immer zuerst auf dem Ubuntu-Rechner gemacht und dann per Git synchronisiert.

**Test-Modi:**
- **Lokale Tests**: Für schnelle Tests kann die Anwendung auch auf Ubuntu im Fenstermodus laufen (1280x720)
- **Pi5 Tests**: Vollbild-Modus (1280x720) auf 7" Touch-Display für finale Tests
- **VNC nicht nötig**: Fenstermodus ist praktischer für Entwicklung und Debugging

**Versionierungs-System (WICHTIG!):**
- Vor JEDEM Git-Upload muss die Versionsnummer erhöht werden
- Aktuelle Version: 1.4.0
- Bei kleinen Fixes/Bugfixes: Patch-Version erhöhen (1.4.0 → 1.4.1)
- Bei neuen Features: Minor-Version erhöhen (1.4.0 → 1.5.0)  
- Bei größeren Änderungen: Major-Version erhöhen (1.4.0 → 2.0.0)

**Versionierungs-Workflow:**
1. VERSION-Datei bearbeiten (z.B. "1.4.1")
2. __init__.py aktualisieren (__version__ = "1.4.1")
3. Git Commit mit Versionsnummer: "🏷️ Version 1.4.1 - Bugfix XYZ"
4. Git Tag erstellen: git tag -a v1.4.1 -m "Beschreibung"
5. Push mit Tags: git push origin main --tags
6. Pi5 per SSH updaten: git pull origin main

**Debugging-Best-Practices (Lessons Learned):**
- **Objekt-Status direkt prüfen**: `if self.aktuelles_pferd:` - Null-Checks sind essentiell
- **Kontext-Inhalt analysieren**: Was wird wirklich übertragen? Logs zeigen nicht immer die ganze Wahrheit
- **Einfache Null-Checks**: Manchmal sind die simpelsten Bugs die tückischsten
- **Root Cause vs. Symptom**: UI zeigt "TextLabel" ≠ UI-Problem, sondern fehlende Daten
- **Datenfluss verfolgen**: BeladenSeite → MainWindow → FütternSeite - wo geht das Objekt verloren?

**Merke:** Immer diese Regeln beachten, wenn du Anweisungen für den Raspberry Pi gibst!
