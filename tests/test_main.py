from app.main import app

def test_healthcheck():
    client = app.test_client()
    response = client.get('/healthcheck')
    assert response.status_code == 200
    assert response.json == {"status": "up"}

def test_users():
    client = app.test_client()
    response = client.get('/users')
    assert response.status_code == 200
    assert len(response.json) == 2  # Verificamos que traiga los 2 usuarios