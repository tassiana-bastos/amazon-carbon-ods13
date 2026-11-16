#Testes da API sem carregar o modelo Qwen.

from contextlib import asynccontextmanager

from fastapi.testclient import TestClient

from api.main import app, MOTORES


@asynccontextmanager
async def lifespan_de_teste(_app):
    """Substitui o lifespan real para não carregar pesos durante pytest."""
    yield


# Impede o TestClient de executar o carregamento do Qwen nestes testes.
app.router.lifespan_context = lifespan_de_teste

client = TestClient(app)


def test_texto_invalido_retorna_422():
    response = client.post(
        "/processar_texto",
        json={"texto": "curto"},
    )

    assert response.status_code == 422


def test_campo_extra_retorna_422():
    response = client.post(
        "/processar_texto",
        json={
            "texto": "Incêndios florestais atingiram áreas da Amazônia.",
            "campo_extra": "não permitido",
        },
    )

    assert response.status_code == 422


def test_modelo_indisponivel_retorna_503():
    motores_anteriores = MOTORES.copy()
    MOTORES.clear()

    try:
        response = client.post(
            "/processar_texto",
            json={
                "texto": "Incêndios florestais atingiram áreas de vegetação na Amazônia.",
            },
        )

        assert response.status_code == 503
        assert "Modelo LLM local indisponível" in response.json()["detail"]
    finally:
        MOTORES.clear()
        MOTORES.update(motores_anteriores)

