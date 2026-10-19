# API FastAPI — guia de utilização

## Executar
Na raiz: `pip install -r requirements-api.txt` e `uvicorn api.main:app --reload`.
Documentação interativa: `http://127.0.0.1:8000/docs`; alternativa: `/redoc`.

## `GET /desmatamento`
Consulta dados PRODES/TerraBrasilis em JSON. Parâmetros opcionais: `uf`, `ano_inicio`, `ano_fim`, `limite` (1–20.000).
Exemplos:
- `http://127.0.0.1:8000/desmatamento?uf=Pará&ano_inicio=2015&ano_fim=2020`
- `http://127.0.0.1:8000/desmatamento?limite=10`
Resposta contém `total`, filtros e `dados` (`year`, `area_km2`, `uf`).

## `GET /resumo`
Retorna número de registros, estados, intervalo temporal e ranking agregado descritivo por estado.

## `POST /observacoes`
Recebe JSON com `titulo` (3–120 caracteres), `texto` (5–2.000) e `fonte` opcional (até 500). Devolve HTTP 201 e grava uma linha em `data/processed/observacoes.jsonl`.
Exemplo:
```json
{"titulo":"Observação de teste","texto":"Informação ambiental para testar a API.","fonte":"https://example.org/"}
```
Campos inválidos resultam em HTTP 422. A API acadêmica não possui autenticação; não publicar com escrita aberta em produção.

## Integração Streamlit
Inicie API num terminal e `streamlit run app.py` em outro. A página **API e contribuições** consome GET e POST. Para uma API hospedada separadamente, configure `API_BASE_URL`. `localhost` só funciona quando ambos os processos compartilham ambiente de rede.
