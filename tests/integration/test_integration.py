import pytest
import json
from app.main import app, db, Usuario
from sqlalchemy import create_engine

@pytest.fixture
def integration_client():
    # 1. Establecer el modo testing
    app.config['TESTING'] = True
    
    # 2. Definir la URI de Render directamente
    render_uri = 'postgresql://usuario:password@host-de-render.com/nombre_bd'
    app.config['SQLALCHEMY_DATABASE_URI'] = render_uri
    
    # 3. Re-vinculación segura mediante la inyección del engine en la sesión
    with app.app_context():
        nuevo_engine = create_engine(render_uri)
        
        # Removemos la sesión vinculada a SQLite
        db.session.remove()
        
        # Forzamos a la sesión activa a utilizar el nuevo motor de Postgres
        db.session.configure(bind=nuevo_engine)
        
    with app.test_client() as client:
        yield client
        
    # Limpieza final de la sesión al concluir el test
    with app.app_context():
        db.session.remove()

# =====================================================================
# TEST DE INTEGRACIÓN REAL (Render Postgres)
# =====================================================================

def test_flujo_creacion_y_limpieza_postgres(integration_client):
    """Prueba la inserción real en Postgres y limpia el registro al terminar"""
    
    # PASO 1: Crear el usuario de prueba a través de la API
    payload = {
        "nombre": "Test",
        "apellido": "Integracion",
        "rol": "QA_Automatico"
    }
    response_post = integration_client.post(
        '/usuarios', 
        data=json.dumps(payload), 
        content_type='application/json'
    )
    
    assert response_post.status_code == 201
    nuevo_usuario = json.loads(response_post.data)
    usuario_id = nuevo_usuario['id']  # Guardamos el ID que nos dio Postgres

    # PASO 2: Verificar que el usuario realmente impactó en la base de datos de Render
    response_get = integration_client.get('/usuarios')
    assert response_get.status_code == 200
    lista_usuarios = json.loads(response_get.data)
    
    # Buscamos nuestro usuario en la lista real para confirmar que existe
    usuario_encontrado = any(u['id'] == usuario_id for u in lista_usuarios)
    assert usuario_encontrado is True

    # PASO 3: LIMPIEZA QUIRÚRGICA (Borramos SOLO nuestro registro de prueba)
    with app.app_context():
        usuario_a_borrar = db.session.get(Usuario, usuario_id)
        if usuario_a_borrar:
            db.session.delete(usuario_a_borrar)
            db.session.commit()