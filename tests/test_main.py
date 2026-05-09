import pytest
from app.main import app

@pytest.fixture
def client():
    # Preparamos un cliente de prueba de Flask
    with app.test_client() as client:
        yield client

def test_healthcheck(client):
    """Verifica que el endpoint /healthcheck responda correctamente"""
    response = client.get('/healthcheck')
    
    # Verificamos que el código de estado sea 200 (OK)
    assert response.status_code == 200
    
    # Verificamos que el JSON devuelto sea el correcto
    assert response.json['status'] == 'up'