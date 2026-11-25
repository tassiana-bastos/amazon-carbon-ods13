# API FastAPI — guia de utilização (TP5)

## Executar
Na raiz: `pip install -r requirements.txt`, configurar `.env` a partir de `.env.example` e iniciar com `uvicorn api.main:app`.
Documentação interativa: `http://127.0.0.1:8000/docs`; alternativa: `/redoc`.

## Saúde
`GET /saude` informa se a chave OpenRouter está configurada, o provedor e o model id selecionado. A chave nunca é retornada.

## Dados PRODES
- `GET /desmatamento`: parâmetros opcionais `uf`, `ano_inicio`, `ano_fim`, `limite` (1–20.000). Retorna `year`, `area_km2`, `uf`.
- `GET /resumo`: número de registros, UFs, intervalo temporal e ranking agregado descritivo.

## Observações
`POST /observacoes` recebe `titulo` (3–120 caracteres), `texto` (5–2.000) e `fonte` opcional (até 500). Retorna HTTP 201 e grava em `data/processed/observacoes.jsonl`. Entradas não são consideradas dados oficiais.

## Memória conversacional
- `POST /conversas` — cria conversa e retorna UUID4.
- `GET /conversas/{id}` — recupera histórico e notas de estados.
- `POST /conversas/{id}/mensagens` — recebe `{"mensagem":"..."}`, calcula fatos, recupera notícias e chama OpenRouter.
- `DELETE /conversas/{id}` — apaga o arquivo da conversa (HTTP 204).

IDs inválidos retornam 422; conversas inexistentes retornam 404. As mensagens são persistidas em `data/conversas/`, diretório excluído do Git.

## Compatibilidade TP4
`POST /processar_texto` foi mantida, mas agora utiliza o provedor remoto configurado. Não carrega modelo local.

## Erros do provedor
- 503: chave ausente/inválida ou rate limit.
- 502: erro de comunicação, erro HTTP do provedor ou resposta vazia/inválida.
- 504: timeout.
