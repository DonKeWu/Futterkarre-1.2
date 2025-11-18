# Futterkarre Container 109 - Dell Wyse Proxmox

## 🖥️ INFRASTRUKTUR:
- **Proxmox Host:** Dell Wyse (192.168.2.10)  
- **Container:** LXC 109 (192.168.2.230)
- **Pi5 Futterkarre:** 192.168.2.17

## 📋 SETUP-REIHENFOLGE:

### QUICK-SETUP (empfohlen):
```bash
# Auf Dell Wyse Proxmox (192.168.2.10)
chmod +x setup_quick.sh
./setup_quick.sh

# Dann API deployen:
pct push 109 app.py /opt/futterkarre/api/app.py
pct exec 109 -- systemctl start futterkarre-api
```

### MANUELL (Schritt-für-Schritt):
```bash
# 1. Container
./create_container.sh

# 2. Setup
pct push 109 setup_futterkarre.sh /root/setup_futterkarre.sh
pct exec 109 -- /root/setup_futterkarre.sh

# 3. Deploy
./deploy_api.sh
```

## 🌐 ZUGRIFF:

- **Dashboard:** http://192.168.2.230:5000/
- **API Status:** http://192.168.2.230:5000/api/status
- **Pi5 Endpoint:** http://192.168.2.230:5000/api/fuetterung

## 📊 API ENDPOINTS:

### POST /api/fuetterung
```json
{
  "gesamtmenge": 135.0,
  "heu_kg": 67.5,
  "heulage_kg": 67.5,
  "heu_pferde": 15,
  "heulage_pferde": 15,
  "dauer_minuten": 32,
  "notizen": "Normale Fütterung",
  "pi5_id": "rpi5-stall-01"
}
```

### GET /api/fuetterungen/filter
```
?datum_von=2025-11-01&datum_bis=2025-11-30&limit=50
```

## 🗄️ DATENBANK:

- **SQLite:** `/opt/futterkarre/data/futterkarre.db`
- **Tabellen:** fuetterungen, pferde
- **Backup:** Automatisch täglich

## 🔧 WARTUNG:

```bash
# Service Status
pct exec 109 -- systemctl status futterkarre-api

# Logs anzeigen
pct exec 109 -- tail -f /opt/futterkarre/logs/api.log

# Service neustarten
pct exec 109 -- systemctl restart futterkarre-api

# Container Shell
pct enter 109
```

## 📈 FEATURES:

✅ SQLite Langzeit-Datenspeicherung
✅ REST API für Pi5 Integration  
✅ Web-Dashboard für Statistiken
✅ Pferdename/Zeitraum Filter
✅ Automatische Backups (geplant)
✅ Multi-Standort fähig (pi5_id)

## 🔮 ZUKUNFT:

- Grafana Integration (Container 106)
- Automatische Backups zu NAS
- Excel/CSV Export
- Email-Benachrichtigungen
- Mobile Web-App