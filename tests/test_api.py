from fastapi.testclient import TestClient
from api.main import app
client=TestClient(app)
def test_root():
    r=client.get("/"); assert r.status_code==200 and r.json()["status"]=="online"
def test_get():
    r=client.get("/desmatamento",params={"limite":5}); assert r.status_code==200 and len(r.json()["dados"])<=5
def test_post_validation():
    r=client.post("/observacoes",json={"titulo":"Teste válido","texto":"Texto ambiental de teste."})
    assert r.status_code==201
