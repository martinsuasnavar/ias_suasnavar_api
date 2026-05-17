import os
from flask import Flask, jsonify, request, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# =====================================================================
# 1. PASO CRÍTICO: Configuración de la Base de Datos antes de SQLAlchemy
# =====================================================================
uri = os.environ.get("DATABASE_URL")

if uri:
    # Quitamos las comillas dobles que arrastra el comando "set" de CMD
    uri = uri.strip('"')
    
    # Por las dudas, si en Render viniera como postgres://, lo adaptamos
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
else:
    uri = "sqlite:///data.db"

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializamos SQLAlchemy ahora que las configuraciones están listas
db = SQLAlchemy(app)

# =====================================================================
# 2. MODELO DE LA BASE DE DATOS
# =====================================================================
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    rol = db.Column(db.String(50), nullable=False)

# =====================================================================
# 3. RUTAS / ENDPOINTS
# =====================================================================

# Dashboard Frontend Principal
@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>User Dashboard - IAS</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; }
        header { background-color: #3f51b5; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
        .container { display: flex; flex: 1; }
        .table-section { flex: 2; padding: 20px; border-right: 2px solid #3f51b5; }
        .form-section { flex: 1; padding: 20px; background-color: #f9f9f9; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { color: #3f51b5; text-align: left; padding: 10px; border-bottom: 1px solid #ddd; }
        td { padding: 10px; border-bottom: 1px solid #eee; }
        input { width: 100%; padding: 8px; margin: 10px 0; border: 1px solid #3f51b5; box-sizing: border-box; }
        label { color: #999; font-weight: bold; display: block; }
        .btn-new { background: white; color: #3f51b5; border: none; padding: 8px 15px; font-weight: bold; cursor: pointer; border-radius: 4px; }
        .btn-save { background: #3f51b5; color: white; border: none; padding: 10px 30px; cursor: pointer; border-radius: 4px; }
        .btn-cancel { background: white; color: #3f51b5; border: 1px solid #3f51b5; padding: 10px 30px; cursor: pointer; border-radius: 4px; }
        .actions { display: flex; gap: 10px; margin-top: 20px; }
    </style>
</head>
<body>

<header>
    <h2>User Dashboard</h2>
    <button class="btn-new" onclick="document.getElementById('nombre').focus()">+ New user</button>
</header>

<div class="container">
    <section class="table-section">
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>NOMBRE</th>
                    <th>APELLIDO</th>
                    <th>ROL</th>
                    <th>ACTIONS</th>
                </tr>
            </thead>
            <tbody id="user-table-body">
            </tbody>
        </table>
    </section>

    <section class="form-section">
        <h3>New user</h3>
        <label>Nombre</label>
        <input type="text" id="nombre">
        
        <label>Apellido</label>
        <input type="text" id="apellido">
        
        <label>Rol</label>
        <input type="text" id="rol">

        <div class="actions">
            <button class="btn-save" onclick="saveUser()">Save</button>
            <button class="btn-cancel" onclick="clearForm()">Cancel</button>
        </div>
    </section>
</div>

<script>
    async function loadUsers() {
        const response = await fetch('/usuarios');
        const users = await response.json();
        const tbody = document.getElementById('user-table-body');
        tbody.innerHTML = '';
        users.forEach(u => {
            tbody.innerHTML += `
                <tr>
                    <td>${u.id}</td>
                    <td>${u.nombre}</td>
                    <td>${u.apellido}</td>
                    <td>${u.rol}</td>
                    <td><button onclick="alert('Función de eliminación pendiente de vincular')">Eliminar</button></td>
                </tr>`;
        });
    }

    async function saveUser() {
        const data = {
            nombre: document.getElementById('nombre').value,
            apellido: document.getElementById('apellido').value,
            rol: document.getElementById('rol').value
        };

        const response = await fetch('/usuarios', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            clearForm();
            loadUsers();
        }
    }

    function clearForm() {
        document.getElementById('nombre').value = '';
        document.getElementById('apellido').value = '';
        document.getElementById('rol').value = '';
    }

    loadUsers();
</script>

</body>
</html>
    ''')

# Healthcheck de la API
@app.route('/healthcheck')
def healthcheck():
    return jsonify({"status": "up", "db": "connected"}), 200

# GET: Obtener usuarios reales de Postgres
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([
        {"id": u.id, "nombre": u.nombre, "apellido": u.apellido, "rol": u.rol} 
        for u in usuarios
    ]), 200

# POST: Crear usuario real en Postgres
@app.route('/usuarios', methods=['POST'])
def create_usuario():
    data = request.get_json()
    nuevo_usuario = Usuario(
        nombre=data.get('nombre'),
        apellido=data.get('apellido'),
        rol=data.get('rol')
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({"message": "Usuario creado", "id": nuevo_usuario.id}), 201

# SEED: Carga automática de datos ficticios (Solo si DEBUG=True)
@app.route('/seed', methods=['GET'])
def seed_usuarios():
    if os.environ.get("DEBUG", "False").lower() != "true":
        return jsonify({"error": "Acción no permitida en este entorno"}), 403
        
    usuarios_prueba = [
        {"nombre": "Juan", "apellido": "Pérez", "rol": "Admin"},
        {"nombre": "María", "apellido": "Gómez", "rol": "Developer"},
        {"nombre": "Carlos", "apellido": "López", "rol": "Tester"},
        {"nombre": "Ana", "apellido": "Rodríguez", "rol": "Release Manager"}
    ]
    
    creados = 0
    for u in usuarios_prueba:
        existe = Usuario.query.filter_by(nombre=u["nombre"], apellido=u["apellido"]).first()
        if not existe:
            nuevo = Usuario(nombre=u["nombre"], apellido=u["apellido"], rol=u["rol"])
            db.session.add(nuevo)
            creados += 1
            
    if creados > 0:
        db.session.commit()
        return jsonify({"message": f"Se crearon {creados} usuarios de prueba correctamente."}), 201
    else:
        return jsonify({"message": "Los usuarios de prueba ya estaban cargados."}), 200

# =====================================================================
# 4. ARRANQUE DE LA APLICACIÓN
# =====================================================================
if __name__ == '__main__':
    # Configuración de variables con fallback para Render y CMD local
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    
    # Crea automáticamente las tablas de la base de datos si no existen
    with app.app_context():
        db.create_all()
    
    app.run(host=host, port=port, debug=debug)