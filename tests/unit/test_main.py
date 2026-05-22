import pytest
import json
from app.main import app, db, Usuario

@pytest.fixture
def client():
    # 1. ARRANGE: Configuramos la app para el entorno de pruebas
    app.config['TESTING'] = True
    # Forzamos una base de datos en memoria para no tocar Postgres ni archivos locales
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # Creamos un cliente de pruebas de Flask
    with app.test_client() as client:
        with app.app_context():
            # Creamos las tablas de forma limpia en la base de datos temporal
            db.create_all()
        yield client
        
        with app.app_context():
            # Destruimos todo al terminar para que el próximo test empiece de cero
            db.drop_all()

# =====================================================================
# TESTS UNITARIOS
# =====================================================================

def test_healthcheck(client):
    """Verifica que el endpoint de healthcheck responda correctamente"""
    # 2. ACT: Hacemos la petición simulada
    response = client.get('/healthcheck')
    
    # 3. ASSERT: Validamos las respuestas esperadas
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'up'
    assert data['db'] == 'connected'


def test_get_usuarios_vacio(client):
    """Verifica que /usuarios devuelva una lista vacía si no hay registros"""
    response = client.get('/usuarios')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0


def test_create_usuario(client):
    """Verifica la creación exitosa de un usuario mediante POST"""
    payload = {
        "nombre": "Estudiante",
        "apellido": "Informatica",
        "rol": "Developer"
    }
    
    # Mandamos el POST con el JSON de prueba
    response = client.post('/usuarios', 
                           data=json.dumps(payload), 
                           content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Usuario creado'
    assert 'id' in data


def test_seed_usuarios_prohibido_en_produccion(client, monkeypatch):
    """Verifica que /seed devuelva 403 si DEBUG no es True"""
    # Forzamos a que la variable de entorno DEBUG sea False para simular producción
    monkeypatch.setenv("DEBUG", "False")
    
    response = client.get('/seed')
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert "error" in data
    assert data['error'] == "Acción no permitida en este entorno"
    
    
# Forzando ejecucion del pipeline de pruebas unitarias