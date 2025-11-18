#!/usr/bin/env python3
"""
Futterkarre API Server für Proxmox Container 109
Proxmox Host: Dell Wyse (192.168.2.10)
Container IP: 192.168.2.230
Pi5 IP: 192.168.2.17
"""

from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os
import logging
import sqlite3

# === KONFIGURATION ===
PI5_IP = "192.168.2.17"  # Pi5 Futterkarre 
CONTAINER_IP = "192.168.2.230"  # Container auf Dell Wyse
PROXMOX_HOST = "192.168.2.10"  # Dell Wyse Proxmox

# Flask App Setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///opt/futterkarre/data/futterkarre.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Extensions
db = SQLAlchemy(app)
CORS(app, origins=[f"http://{PI5_IP}:*", "http://192.168.2.*"])  # Pi5 + lokales Netz

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/futterkarre/logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === DATENBANK MODELLE ===

class Fuetterung(db.Model):
    __tablename__ = 'fuetterungen'
    
    id = db.Column(db.Integer, primary_key=True)
    datum = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    zeit = db.Column(db.Time, nullable=False, default=datetime.utcnow().time)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Mengen
    gesamtmenge_kg = db.Column(db.Float, nullable=False)
    heu_kg = db.Column(db.Float, default=0.0)
    heulage_kg = db.Column(db.Float, default=0.0)
    
    # Pferde
    heu_pferde = db.Column(db.Integer, default=0)
    heulage_pferde = db.Column(db.Integer, default=0)
    gesamt_pferde = db.Column(db.Integer, default=0)
    
    # Dauer und Notizen
    dauer_minuten = db.Column(db.Integer)
    notizen = db.Column(db.Text)
    wetter = db.Column(db.String(50))
    
    # Synchronisation
    synchronized = db.Column(db.Boolean, default=True)
    pi5_id = db.Column(db.String(100))  # Pi5 MAC/Serial für Multi-Standort
    
    def to_dict(self):
        return {
            'id': self.id,
            'datum': self.datum.isoformat(),
            'zeit': self.zeit.isoformat(),
            'timestamp': self.timestamp.isoformat(),
            'gesamtmenge_kg': self.gesamtmenge_kg,
            'heu_kg': self.heu_kg,
            'heulage_kg': self.heulage_kg,
            'heu_pferde': self.heu_pferde,
            'heulage_pferde': self.heulage_pferde,
            'gesamt_pferde': self.gesamt_pferde,
            'dauer_minuten': self.dauer_minuten,
            'notizen': self.notizen,
            'wetter': self.wetter,
            'pi5_id': self.pi5_id
        }

class Pferd(db.Model):
    __tablename__ = 'pferde'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    box_nummer = db.Column(db.Integer, unique=True)
    rasse = db.Column(db.String(100))
    gewicht_kg = db.Column(db.Float)
    futter_typ = db.Column(db.String(50))  # 'heu', 'heulage', 'beides'
    aktiv = db.Column(db.Boolean, default=True)
    notizen = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'box_nummer': self.box_nummer,
            'rasse': self.rasse,
            'gewicht_kg': self.gewicht_kg,
            'futter_typ': self.futter_typ,
            'aktiv': self.aktiv,
            'notizen': self.notizen
        }

# === REST API ENDPOINTS ===

@app.route('/', methods=['GET'])
def dashboard():
    """Einfaches Web-Dashboard"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🐴 Futterkarre API Dashboard</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .card { background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
            .stat { text-align: center; padding: 15px; background: #e3f2fd; border-radius: 8px; }
            .stat h3 { margin: 0; color: #1976d2; }
            .stat p { margin: 5px 0; font-size: 24px; font-weight: bold; }
            h1 { color: #2e7d32; text-align: center; }
            .api-info { background: #f3e5f5; }
            .recent { max-height: 300px; overflow-y: auto; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #e8f5e8; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🐴 Futterkarre API Dashboard</h1>
            
            <div class="card stats">
                <div class="stat">
                    <h3>📊 Fütterungen</h3>
                    <p id="total-fuetterungen">-</p>
                </div>
                <div class="stat">
                    <h3>🌾 Gesamt Heu</h3>
                    <p id="total-heu">- kg</p>
                </div>
                <div class="stat">
                    <h3>🌿 Gesamt Heulage</h3>
                    <p id="total-heulage">- kg</p>
                </div>
                <div class="stat">
                    <h3>🐴 Aktive Pferde</h3>
                    <p id="active-pferde">-</p>
                </div>
            </div>
            
            <div class="card api-info">
                <h2>🔗 API Endpoints</h2>
                <ul>
                    <li><strong>POST /api/fuetterung</strong> - Neue Fütterung speichern</li>
                    <li><strong>GET /api/fuetterungen</strong> - Alle Fütterungen abrufen</li>
                    <li><strong>GET /api/fuetterungen/filter</strong> - Gefilterte Abfrage (?datum_von=2025-11-01&datum_bis=2025-11-30)</li>
                    <li><strong>GET /api/pferde</strong> - Pferde-Stammdaten</li>
                    <li><strong>POST /api/backup</strong> - Backup erstellen</li>
                    <li><strong>GET /api/status</strong> - System-Status</li>
                </ul>
            </div>
            
            <div class="card">
                <h2>📋 Letzte Fütterungen</h2>
                <div class="recent">
                    <table id="recent-table">
                        <thead>
                            <tr><th>Datum</th><th>Zeit</th><th>Gesamtmenge</th><th>Heu</th><th>Heulage</th><th>Pferde</th></tr>
                        </thead>
                        <tbody id="recent-tbody">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <script>
            // Dashboard Daten laden
            fetch('/api/status').then(r => r.json()).then(data => {
                document.getElementById('total-fuetterungen').textContent = data.total_fuetterungen;
                document.getElementById('total-heu').textContent = data.total_heu_kg.toFixed(1);
                document.getElementById('total-heulage').textContent = data.total_heulage_kg.toFixed(1);
                document.getElementById('active-pferde').textContent = data.active_pferde;
            });
            
            // Letzte Fütterungen laden
            fetch('/api/fuetterungen?limit=10').then(r => r.json()).then(data => {
                const tbody = document.getElementById('recent-tbody');
                data.fuetterungen.forEach(f => {
                    const row = tbody.insertRow();
                    row.innerHTML = `
                        <td>${f.datum}</td>
                        <td>${f.zeit}</td>
                        <td>${f.gesamtmenge_kg} kg</td>
                        <td>${f.heu_kg} kg</td>
                        <td>${f.heulage_kg} kg</td>
                        <td>${f.gesamt_pferde}</td>
                    `;
                });
            });
        </script>
    </body>
    </html>
    '''
    return html

@app.route('/api/fuetterung', methods=['POST'])
def neue_fuetterung():
    """Neue Fütterung vom Pi5 empfangen"""
    try:
        data = request.get_json()
        
        fuetterung = Fuetterung(
            gesamtmenge_kg=data.get('gesamtmenge', 0),
            heu_kg=data.get('heu_kg', 0),
            heulage_kg=data.get('heulage_kg', 0),
            heu_pferde=data.get('heu_pferde', 0),
            heulage_pferde=data.get('heulage_pferde', 0),
            gesamt_pferde=data.get('heu_pferde', 0) + data.get('heulage_pferde', 0),
            dauer_minuten=data.get('dauer_minuten'),
            notizen=data.get('notizen'),
            wetter=data.get('wetter'),
            pi5_id=data.get('pi5_id', 'unknown')
        )
        
        db.session.add(fuetterung)
        db.session.commit()
        
        logger.info(f"✅ Neue Fütterung gespeichert: ID={fuetterung.id}, Gesamt={fuetterung.gesamtmenge_kg}kg")
        
        return jsonify({
            'success': True,
            'message': 'Fütterung erfolgreich gespeichert',
            'id': fuetterung.id
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Speichern: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/fuetterungen', methods=['GET'])
def get_fuetterungen():
    """Fütterungen abrufen mit optionalen Filtern"""
    try:
        # Parameter
        limit = request.args.get('limit', 100, type=int)
        datum_von = request.args.get('datum_von')
        datum_bis = request.args.get('datum_bis')
        
        query = Fuetterung.query
        
        # Datum-Filter
        if datum_von:
            query = query.filter(Fuetterung.datum >= datetime.strptime(datum_von, '%Y-%m-%d').date())
        if datum_bis:
            query = query.filter(Fuetterung.datum <= datetime.strptime(datum_bis, '%Y-%m-%d').date())
        
        fuetterungen = query.order_by(Fuetterung.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(fuetterungen),
            'fuetterungen': [f.to_dict() for f in fuetterungen]
        })
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """System-Status und Statistiken"""
    try:
        # Statistiken berechnen
        total_fuetterungen = Fuetterung.query.count()
        total_heu = db.session.query(db.func.sum(Fuetterung.heu_kg)).scalar() or 0
        total_heulage = db.session.query(db.func.sum(Fuetterung.heulage_kg)).scalar() or 0
        active_pferde = Pferd.query.filter_by(aktiv=True).count()
        
        # Letzte Fütterung
        letzte_fuetterung = Fuetterung.query.order_by(Fuetterung.timestamp.desc()).first()
        
        return jsonify({
            'success': True,
            'server': 'Futterkarre API v1.0',
            'status': 'online',
            'timestamp': datetime.now().isoformat(),
            'total_fuetterungen': total_fuetterungen,
            'total_heu_kg': float(total_heu),
            'total_heulage_kg': float(total_heulage),
            'active_pferde': active_pferde,
            'letzte_fuetterung': letzte_fuetterung.to_dict() if letzte_fuetterung else None
        })
        
    except Exception as e:
        logger.error(f"❌ Status-Fehler: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# === DATENBANK INITIALISIERUNG ===

def init_database():
    """Datenbank und Beispiel-Daten erstellen"""
    with app.app_context():
        db.create_all()
        
        # Beispiel-Pferde hinzufügen (falls leer)
        if Pferd.query.count() == 0:
            beispiel_pferde = [
                Pferd(name="Thunder", box_nummer=1, rasse="Warmblut", gewicht_kg=600, futter_typ="heu"),
                Pferd(name="Bella", box_nummer=2, rasse="Pony", gewicht_kg=400, futter_typ="heulage"),
                Pferd(name="Max", box_nummer=3, rasse="Kaltblut", gewicht_kg=800, futter_typ="beides")
            ]
            
            for pferd in beispiel_pferde:
                db.session.add(pferd)
            
            db.session.commit()
            logger.info("✅ Beispiel-Pferde erstellt")

if __name__ == '__main__':
    # Datenbank initialisieren
    init_database()
    
    # Server starten
    logger.info("🚀 Futterkarre API startet auf http://192.168.2.109:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)