# Decisão técnica — LLM via API (TP5, Opção 1)

**Projeto:** Amazônia Legal | ODS 13  
**Estratégia:** memória conversacional via OpenRouter, sem inferência local.

## Justificativa
O TP5 permite modelos locais ou APIs online. Para esta entrega, foi escolhida a API porque o ambiente local não oferece margem de memória adequada para carregar e executar os pesos de um LLM. A aplicação mantém o modelo fora do computador e faz a chamada pelo backend FastAPI.

## Integração
- Endpoint: `https://openrouter.ai/api/v1/chat/completions`.
- Chave: `OPENROUTER_API_KEY`, carregada pelo backend a partir de `.env`.
- Modelo: `nvidia/nemotron-3.5-lightning:free`. Disponibilidade e limites são determinados pelo provedor e não são garantidos pelo projeto.
- `temperature=0.2` e `max_tokens=1500` para favorecer respostas contidas e reduzir respostas truncadas.
- Timeout de conexão/leitura e tratamento de HTTP 429, erros de autenticação, falhas do provedor e resposta vazia.

## Estratégia de memória
A API do modelo não guarda estado da aplicação. A memória é gerenciada pelo projeto:
1. O histórico completo é persistido em JSON, separado por UUID4.
2. Python extrai as UFs mencionadas nas mensagens do usuário e preserva notas em ordem de aparição.
3. O prompt recebe as notas e uma janela de até cinco mensagens recentes.
4. O histórico completo continua visível/recuperável, mesmo quando mensagens antigas saem da janela enviada ao modelo.
5. O usuário pode apagar a conversa; os arquivos ficam fora do Git.

A escolha combina a memória de entidades/notas ensinada na aula com uma janela curta de mensagens. Não há chamada adicional de LLM para resumir, evitando custo e latência de sumarização.

## Papel de Python e do LLM
Python lê/normaliza os dados, calcula fatos PRODES, recupera notícias por correspondência lexical e extrai notas de UFs. O LLM interpreta a pergunta e redige a resposta com base nesse contexto. O modelo não é responsável por calcular rankings ou inventar valores.

## Segurança e limites
- Não armazenar a chave no código, Streamlit ou repositório.
- Não versionar `.env` nem `data/conversas/`.
- Não compartilhar URLs de conversa: o UUID é o identificador de acesso ao histórico.
- Evitar dados pessoais/sensíveis, pois o conteúdo enviado é processado pelo provedor externo.
- A memória de notas só reconhece estados/siglas; a recuperação de notícias é lexical.
- Modelos gratuitos podem ter rate limits, latência ou indisponibilidade. O model id deve ser ajustado se o provedor deixar de oferecê-lo.

## Fontes
- Enunciado TP5 — Opção 1: memória conversacional, local ou API.
- Aula 17–18 — Etapa 9: histórico e papéis, `session_state`, fatos calculados em Python, notas, janela, persistência por id, exclusão e segredo fora do código.
- OpenRouter API: https://openrouter.ai/docs/api-reference/overview
