from fastapi.testclient import TestClient

from api import main


def test_conversation_memory_persistence_notes_and_delete(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "CONVERSATIONS_DIR", tmp_path)
    monkeypatch.setattr(main, "call_openrouter", lambda messages: "Resposta baseada nos fatos fornecidos.")

    with TestClient(main.app) as client:
        created = client.post("/conversas")
        assert created.status_code == 201
        conversation_id = created.json()["conversation_id"]
        assert len(conversation_id) == 32

        first = client.post(
            f"/conversas/{conversation_id}/mensagens",
            json={"mensagem": "Quero analisar o Acre."},
        )
        assert first.status_code == 200
        assert "Acre (AC)" in first.json()["notas"]

        second = client.post(
            f"/conversas/{conversation_id}/mensagens",
            json={"mensagem": "E no ano anterior, considerando o mesmo estado?"},
        )
        assert second.status_code == 200
        assert second.json()["total_mensagens"] == 4

        restored = client.get(f"/conversas/{conversation_id}")
        assert restored.status_code == 200
        assert len(restored.json()["messages"]) == 4
        assert "Acre (AC)" in restored.json()["notas"]

        deleted = client.delete(f"/conversas/{conversation_id}")
        assert deleted.status_code == 204
        assert client.get(f"/conversas/{conversation_id}").status_code == 404


def test_conversation_ids_are_validated(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "CONVERSATIONS_DIR", tmp_path)
    with TestClient(main.app) as client:
        assert client.get("/conversas/nao-e-uuid").status_code == 422
        assert client.get("/conversas/" + "a" * 32).status_code == 404


def test_existing_data_routes_remain_available():
    with TestClient(main.app) as client:
        data = client.get("/desmatamento")
        summary = client.get("/resumo")
        assert data.status_code == 200
        assert data.json()["total"] > 0
        assert summary.status_code == 200
        assert summary.json()["total_registros"] > 0


def test_python_extracts_state_notes_without_llm():
    notes = main.extrair_notas([
        {"role": "user", "content": "E o Acre?"},
        {"role": "assistant", "content": "Vou verificar."},
        {"role": "user", "content": "Compare também Mato Grosso."},
    ])
    assert notes == ["Acre (AC)", "Mato Grosso (MT)"]


def test_news_retrieval_returns_source_metadata():
    news = main.recuperar_noticias("terras indígenas amazônia")
    assert isinstance(news, list)
    if news:
        assert {"titulo", "data_publicacao", "url", "trecho"} <= set(news[0])
