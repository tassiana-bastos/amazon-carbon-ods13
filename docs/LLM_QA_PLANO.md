# Memória conversacional e Q&A — TP5

A implementação desta etapa está documentada em `TP5_IMPLEMENTACAO.md`, `decisao_llm_api.md`, `project_charter.md` e `data_summary_report.md`.

O sistema combina:
- fatos quantitativos calculados em Python a partir do CSV PRODES/TerraBrasilis;
- recuperação lexical de notícias no CSV da Agência Brasil, preservando título, data e URL;
- memória de entidades (estados) extraídas por Python de todo o histórico;
- janela de até cinco mensagens recentes (`user`/`assistant`) enviada ao modelo;
- persistência de uma conversa por UUID em arquivo JSON, com leitura, retomada e exclusão.

O LLM recebe os fatos e contexto em uma mensagem `system`; os turnos são enviados com seus papéis. O prompt proíbe criar números sem evidência e exige reconhecer limitações. A estratégia não é um RAG vetorial nem uma memória semântica geral.
