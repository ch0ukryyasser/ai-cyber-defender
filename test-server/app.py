from flask import Flask, request, jsonify
import logging
from datetime import datetime

app = Flask(__name__)

# Configuration du logging pour écrire dans un fichier
logging.basicConfig(
    filename='logs/access.log',
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger('access')

@app.before_request
def log_request():
    log_line = f'{datetime.now().isoformat()} | IP={request.remote_addr} | {request.method} {request.path} | UA={request.headers.get("User-Agent")}'
    logger.info(log_line)

@app.route('/')
def home():
    return jsonify({"message": "Bienvenue sur le serveur de test"})

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    if username == 'admin' and password == 'admin123':
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "failed"}), 401

@app.route('/search')
def search():
    query = request.args.get('q', '')
    return jsonify({"results": f"Recherche pour: {query}"})

@app.route('/api/users/<user_id>')
def get_user(user_id):
    return jsonify({"user_id": user_id, "name": "Utilisateur test"})

if __name__ == '__main__':
    import os
    os.makedirs('logs', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=False)