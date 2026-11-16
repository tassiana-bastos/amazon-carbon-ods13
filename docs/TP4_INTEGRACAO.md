# TP4 — Guia de integração no repositório existente

Repositório: https://github.com/tassiana-bastos/amazon-carbon-ods13

## Arquivos desta entrega

- `api/main.py`: versão integrada da API existente, preservando `/`, `/desmatamento`, `/resumo` e `/observacoes`, e acrescentando `/saude` e `/processar_texto`.
- `src/baixar_modelo.py`: download inicial dos arquivos do Hugging Face para o computador.
- `pages/ia_ambiental.py`: página Streamlit para enviar texto para análise.
- `docs/escolha_do_modelo.md`: justificativa técnica e critérios de seleção.
- `requirements-llm.txt`: dependências extras para o motor local.
- `tests/test_tp4.py`: testes de contrato e tratamento de indisponibilidade sem carregar o modelo pesado.

## 1. Copiar os arquivos

Copie os arquivos para os mesmos caminhos no seu repositório. Substitua `api/main.py` pelo arquivo fornecido, pois ele incorpora as rotas que já existiam. Os outros arquivos são novos. Não apague suas fontes CSV nem as páginas atuais.

## 2. Ambiente e dependências

Na raiz do projeto, ative seu ambiente virtual. Mantenha `requirements.txt` atual como está e instale as dependências extras:

```bash
pip install -r requirements.txt
pip install -r requirements-llm.txt
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

O PyTorch pode ter instalação diferente conforme CPU/GPU e sistema operacional. O comando acima instala a distribuição CPU, adequada para um teste inicial sem configurar CUDA. Para GPU NVIDIA, substitua-o pela versão compatível indicada pelo seletor oficial do PyTorch.

## 3. Baixar o modelo (requer internet nesta etapa)

Execute uma única vez, a partir da raiz:

```bash
python -m src.baixar_modelo
```

Os arquivos do modelo serão gravados em `models/qwen2.5-1.5b-instruct/`. O diretório `models/` deve permanecer fora do Git, pois contém vários GB de pesos. Não faça commit nem push dos pesos.

## 4. Iniciar os serviços localmente

Abra dois terminais na raiz do projeto.

Terminal 1 — API:

```bash
uvicorn api.main:app --reload
```

Terminal 2 — aplicação Streamlit:

```bash
streamlit run app.py
```

Abra `http://127.0.0.1:8000/docs`, confira `/saude` e teste `POST /processar_texto`. Depois, na aplicação Streamlit, abra a página **Análise de texto com IA local**.

## 5. Testar a API

Exemplo do corpo JSON:

```json
{
  "texto": "Incêndios florestais e fumaça atingiram áreas de vegetação no sul do Amazonas."
}
```

A resposta 200 contém `texto_processado`, `tipo_analise`, `categoria`, `confianca`, `modelo` e `aviso`. O Pydantic valida a estrutura de saída por `response_model=ResultadoAnalise`.

Testes de validação: texto menor que 15 caracteres ou envio de campos adicionais deve produzir HTTP 422. Se o modelo não estiver instalado/carregado, `GET /saude` permanece disponível e `POST /processar_texto` retorna HTTP 503.

## 6. Incluir a página no menu Streamlit

A estrutura atual já utiliza a pasta `pages/` para páginas independentes. Adicione `pages/ia_ambiental.py` nessa pasta. Se o seu roteador `app.py` usa `st.navigation`/`st.Page` com lista explícita, acrescente uma página apontando para esse arquivo; não duplique a página se o projeto já descobrir automaticamente os arquivos da pasta.

## 7. Ajustar o `.gitignore`

Acrescente estas linhas, caso ainda não existam:

```gitignore
# Pesos grandes do modelo local
models/

# Arquivos locais gerados/temporários
__pycache__/
*.py[cod]
```

O modelo não deve ser enviado ao Streamlit Community Cloud. Esta etapa do TP4 é explicitamente local; o serviço online atual do painel não terá acesso ao modelo que está no seu computador.

## 8. Git: revisar, commit e push

```bash
git status
git add api/main.py src/baixar_modelo.py pages/ia_ambiental.py docs/escolha_do_modelo.md docs/TP4_INTEGRACAO.md requirements-llm.txt tests/test_tp4.py .gitignore
git commit -m "TP4: integra classificador LLM local via FastAPI"
git push
```

Antes do commit, confira que `models/` não aparece no `git status`.

## 9. Limitação de escopo

Esta primeira integração faz classificação temática local, para cumprir a tarefa de NLP do TP4 e demonstrar o modelo atrás do FastAPI. Ela não implementa ainda o Q&A com recuperação RAG, citações dinâmicas de notícias ou respostas quantitativas do PRODES. Esses itens continuam como evolução planejada no Project Charter. Para responder perguntas numéricas sobre o PRODES, os cálculos devem continuar sendo feitos em Python e apresentados ao modelo como contexto, nunca estimados livremente pelo LLM.
