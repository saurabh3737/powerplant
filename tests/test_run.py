from fastapi.testclient import TestClient
from run import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"working_checking": "ok"}