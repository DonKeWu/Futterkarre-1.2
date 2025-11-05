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

**Merke:** Immer diese Regeln beachten, wenn du Anweisungen für den Raspberry Pi gibst!
