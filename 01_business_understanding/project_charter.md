# Project Charter

**Projeto:** Amazonia Legal | ODS 13 — análise descritiva do desmatamento e contexto ambiental

**Repositorio:** https://github.com/tassiana-bastos/amazon-carbon-ods13


## Problema de negocio

O desmatamento na Amazonia Legal representa um desafio para a conservacao dos ecossistemas e para o enfrentamento das mudancas climaticas.

Este projeto busca utilizar dados de desmatamento para apoiar a identificacao dos estados da Amazonia Legal que apresentam maior necessidade de atencao e monitoramento, contribuindo para uma tomada de decisao orintada por dados.

## Pergunta de negocio

Quais estados da Amazônia Legal devem ser priorizados para ações de conservação considerando a evolução e a intensidade do desmatamento?

## Objetivo geral

Desenvolver uma aplicacao exploratoria data-driven que permita explorar a evolucao do desmatamento na Amazonia Legal por estado e ano e complementar essa analise com noticias recentes relacionadas ao meio ambiente atraves da comparacao, exportacao e reutilizacao dos dados por pessoas e programas. 

## Objetivos específicos

- Analisar a evolução temporal do desmatamento por estado.  

- Comparar a intensidade do desmatamento entre os estados da Amazônia Legal.  

- Disponibilizar indicadores e filtros para exploração dos dados.  

- Coletar, processar e apresentar notícias relacionadas à Amazônia, desmatamento e mudanças climáticas.  

- Apresentar estatísticas básicas e uma nuvem de palavras a partir das notícias.  

- Permitir upload de CSV para complementar as informações.  

- Permitir download do recorte atualmente exibido.  

- Utilizar cache e estado de sessão no Streamlit 

## Escopo

### Incluido no projeto

- Dados históricos de taxas de desmatamento da Amazônia Legal por estado e ano.
  
- Streamlit multipáginas com st.navigation/st.Page.
  
- API FastAPI com GET e POST, validação e documentação OpenAPI.

- Período disponível no conjunto principal: 1988–2025.
  
- Integração do cliente Streamlit com a API. 

- Indicadores de desmatamento total, média anual, último valor disponível, variação entre primeiro e último ano e ordenação dos estados.

- Filtros interativos por estado e período.

- Coleta separada de conteúdo de páginas da Agência Brasil utilizando BeautifulSoup.

- Armazenamento dos dados coletados em CSV nos diretórios de dados do projeto.

- Exibição de notícias, estatísticas básicas e nuvem de palavras.

- Upload de CSV pelo usuário e identificação da procedência dos registros como “coletada” ou “enviada”.

- Download do recorte atualmente filtrado.

- Cache de dados e estado de sessão.

- Documentação do projeto e versionamento no GitHub.
  
- Decisão de Selenium fundamentada.
  
- Planejamento de Q&A com LLMs.

### Fora do escopo

- Previsão futura de desmatamento.

- Modelos preditivos de risco ambiental.

- Estimativa direta de emissões de GEE.

- Definição automática de políticas públicas ou decisões de conservação.


## Meta/KPIs

### KPI 1 — Desmatamento total

Área total desmatada no período selecionado.

### KPI 2 — Desmatamento médio anual

Desmatamento total dividido pelo número de anos considerados.

### KPI 3 — Último valor disponível

Área desmatada no ano mais recente disponível no período selecionado.

### KPI 4 — Variação

Comparação entre o primeiro e o último ano do período selecionado.

### KPI 5 — Ordenação dos estados

Ordenação dos nove estados da Amazônia Legal segundo os indicadores apresentados, permitindo a comparação entre os territórios.


## Stakeholders

| Stakeholder | Interesse / utilizacao|
|----------|----------|
| Analistas ambientais e de sustentabilidade   | Explorar e comparar os dados de desmatamento e as informações contextuais das notícias   |
| Gestores públicos   | Utilizar os indicadores como apoio à análise e definição de prioridades de monitoramento   |
| Responsáveis por programas de conservação    | Consultar a evolução territorial e temporal do desmatamento   |
| Usuários da aplicação    | Aplicar filtros, consultar notícias e complementar os dados por upload de CSV   |

## ODS 13 

O projeto está alinhado ao ODS 13 — Ação Contra a Mudança Global do Clima, ao utilizar dados sobre desmatamento para apoiar a análise de um fenômeno relacionado às mudanças climáticas e à conservação dos ecossistemas.
