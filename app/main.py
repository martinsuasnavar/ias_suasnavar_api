from flask import Flask, jsonify, render_template_string
import os

app = Flask(__name__)

# Simulación de datos para el ABM (Alcance Técnico)
users = [
    {"id": 1, "nombre": "Admin Sistema", "rol": "Administrador"},
    {"id": 2, "nombre": "Usuario Prueba", "rol": "Consultor"}
]

@app.route('/')
def index():
    # Frontend básico integrado para probar los endpoints
    return render_template_string('''
        <h1>API Management - IAS</h1>
        <button onclick="fetchUsers()">Cargar Usuarios</button>
        <pre id="output"></pre>
        <script>
            function fetchUsers() {
                fetch('/users')
                    .then(res => res.json())
                    .then(data => {
                        document.getElementById('output').innerText = JSON.stringify(data, null, 2);
                    });
            }
        </script>
    ''')

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