# Timer- und Navigationsanalyse Futterkarre

## Problem
- Nach Klick auf den Startbutton und Auswahlseite werden immer wieder nur die Auswahlseite und das Stoppen aller Timer geloggt.
- Die Navigation bleibt auf der Auswahlseite hängen, weitere Seiten werden nicht angezeigt.
- Die TimerManager-Logik stoppt alle Timer bei jedem Navigationsschritt, aber es werden keine neuen Timer oder Aktionen gestartet.

## Ursache
- Die Navigation (`show_status`) ruft bei jedem Seitenwechsel `self.timer_manager.stop_all_timers()` auf, aber es werden keine neuen Timer oder Aktionen für die Zielseite gestartet.
- Die Buttons auf der Auswahlseite sind korrekt verbunden, aber die Zielseiten (z.B. FuetternSeite) starten keine eigenen Timer oder Logik.
- Die Navigation springt immer wieder auf die Auswahlseite zurück, weil kein Kontext oder Statuswechsel erfolgt.

## Lösungsvorschläge
1. **TimerManager-Logik prüfen:**
   - Stelle sicher, dass beim Wechsel auf eine neue Seite die passenden Timer und Aktionen für diese Seite gestartet werden.
   - Ergänze in den Zielseiten (z.B. FuetternSeite) die Initialisierung und das Starten der relevanten Timer.

2. **Navigation erweitern:**
   - Prüfe, ob die Methode `show_status` im MainWindow nach dem Seitenwechsel die Initialisierung der Zielseite korrekt ausführt.
   - Ergänze ggf. Initialisierungs- oder Update-Methoden für jede Seite.

3. **Debugging:**
   - Füge zusätzliche Log-Ausgaben in die Zielseiten ein, um zu sehen, ob die Methoden nach der Navigation wirklich ausgeführt werden.

## Nächste Schritte
- Die Navigation und Timer-Logik gezielt in MainWindow und den Zielseiten analysieren und reparieren.
- Nach jedem Seitenwechsel die Initialisierung und Timer-Start der Zielseite sicherstellen.
- Die Analyse und Lösungsschritte in dieser Datei dokumentieren.

---
Letzte Analyse: 5. November 2025
