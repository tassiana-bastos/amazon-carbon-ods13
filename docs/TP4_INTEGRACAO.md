# Histórico da integração TP4 e migração para TP5

No TP4, a aplicação recebeu uma rota de classificação textual executada com um modelo local. Para o TP5, essa arquitetura foi substituída: não há carregamento de pesos, tokenizer ou runtime local de LLM.

A rota legada `POST /processar_texto` foi mantida para compatibilidade com clientes existentes, mas agora chama o provedor remoto configurado em `OPENROUTER_API_KEY` e `OPENROUTER_MODEL`.

A funcionalidade principal do TP5 está em `POST /conversas`, `GET /conversas/{id}`, `POST /conversas/{id}/mensagens` e `DELETE /conversas/{id}`. A página correspondente é `pages/conversa.py`.

Consulte `docs/TP5_IMPLEMENTACAO.md` para instalação, configuração, execução e testes. As dependências de modelos locais foram removidas de `requirements.txt`.
