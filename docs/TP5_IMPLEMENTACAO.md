# TP5 — Implementação e execução

## Arquitetura
`Streamlit (pages/conversa.py) → FastAPI (api/main.py) → OpenRouter API`

O Streamlit não recebe a chave do provedor. A API mantém os dados PRODES, recupera notícias, extrai notas e persiste a conversa em `data/conversas/`.

## Preparar ambiente
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Copie `.env.example` para `.env` e substitua `coloque_sua_chave_aqui` por sua chave OpenRouter. Não envie `.env` ao Git.

## Executar
Terminal 1:
```bash
uvicorn api.main:app
```
Terminal 2:
```bash
streamlit run app.py
```
Acesse a URL local exibida pelo Streamlit. A documentação da API fica em `http://127.0.0.1:8000/docs`.

## Teste manual sugerido
1. Abra **Conversa com os dados**.
2. Pergunte: “Qual UF teve o maior valor em 2025?”
3. Pergunte: “E no ano anterior?” — verifique se o estado é recuperado do histórico.
4. Pergunte: “Quanto variou?” — confira se a resposta usa os valores presentes nos fatos.
5. Pergunte sobre notícias/terras indígenas — confira se a resposta apresenta o título/URL recuperados quando houver correspondência.
6. Atualize a página (F5) e confirme que o histórico continua.
7. Reinicie a API sem `--reload` e confirme que o histórico permanece.
8. Clique em **Apagar conversa** e confirme que uma nova conversa é iniciada.
9. Em outro navegador/sessão, crie outra conversa e confirme que os históricos não se misturam.

## Testes automatizados
```bash
pytest -q
```
Os testes substituem a chamada externa por uma resposta controlada; não precisam consumir créditos OpenRouter. Eles verificam isolamento, persistência, notas, exclusão, validação do id e rotas preexistentes.

## Problemas comuns
- `OPENROUTER_API_KEY não configurada`: conferir `.env` na raiz e reiniciar Uvicorn.
- HTTP 429: aguardar e tentar novamente; limites de modelos gratuitos variam.
- HTTP 502/504: verificar disponibilidade do provedor e tentar novamente.
- `404 Conversa não encontrada`: o arquivo pode ter sido apagado ou o id da URL não existe.
- Se o model id padrão não estiver disponível na conta/provedor, definir outro id válido em `OPENROUTER_MODEL`.

## Segurança antes do commit
```bash
git status
```
Confirme que `.env`, `data/conversas/*.json`, `.venv/`, `__pycache__/` e arquivos de chave não aparecem na lista de arquivos a enviar.
