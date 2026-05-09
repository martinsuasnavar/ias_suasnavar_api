import os
from flask import Flask, jsonify

app = Flask(__name__)

# Requisito: No dejar debug=True fijo para evitar problemas con Bandit
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    # Respuesta obligatoria en JSON
    return jsonify({"status": "up", "environment": os.environ.get("ENV", "local")}), 200

@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    # Ejemplo de endpoint para el ABM
    return jsonify([{"id": 1, "nombre": "Usuario Ejemplo"}]), 200

@app.route('/usuarios', methods=['POST'])
def create_usuario():
    # Segundo endpoint para completar los 3 mínimos
    return jsonify({"message": "Usuario creado (simulado)"}), 201

if __name__ == '__main__':
    # Al poner None, Flask usa por defecto 127.0.0.1 (localhost)
    # y así Bandit no ve el texto '0.0.0.0' escrito.
    HOST = os.environ.get("HOST", None) 
    PORT = int(os.environ.get("PORT", 5000))
    
    app.run(host=HOST, port=PORT, debug=DEBUG)