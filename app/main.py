from flask import Flask, jsonify
import os

app = Flask(__name__)

# Simulación de datos para el ABM (Alcance Técnico)
users = [
    {"id": 1, "nombre": "Admin Sistema", "rol": "Administrador"},
    {"id": 2, "nombre": "Usuario Prueba", "rol": "Consultor"}
]

@app.route('/')
def index():
    # Primer endpoint: Bienvenida
    return jsonify({
        "mensaje": "API de Informática Jurídica - UM",
        "estado": "Operativa"
    })

@app.route('/healthcheck')
def healthcheck():
    # Segundo endpoint: Salud del sistema
    return jsonify({"status": "up"})

@app.route('/users')
def get_users():
    # Tercer endpoint: Lista de usuarios (JSON)
    return jsonify(users)

if __name__ == '__main__':
    # Configuración segura para Bandit y Render
    port = int(os.environ.get("PORT", 10000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    
    app.run(host=host, port=port, debug=debug)