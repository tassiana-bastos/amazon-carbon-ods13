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
  
- Análise da necessidade de Selenium para páginas dinâmicas, com justificativa técnica da ferramenta de coleta selecionada.
  
- Planejamento de Q&A com LLMs.

### Fora do escopo

- Previsão futura de desmatamento.

- Modelos preditivos de risco ambiental.

- Estimativa direta de emissões de GEE.

- Definição automática de políticas públicas ou decisões de conservação.

## Decisão técnica: Web Scraping com Selenium

### Contexto e diagnóstico

Durante a análise das fontes de dados do projeto, foi investigada a utilização de Selenium para a extração de informações do painel PRODES, disponibilizado pelo TerraBrasilis/INPE.

A investigação identificou que a página do TerraBrasilis utiliza JavaScript para carregar e renderizar os dados. Em um primeiro teste, a biblioteca Requests retornou o HTML inicial da página, mas não encontrou a tabela com os registros esperados.

Esse comportamento caracteriza uma página dinâmica: parte do conteúdo é disponibilizada posteriormente, após a execução de JavaScript no navegador.

### Alternativas avaliadas

Foram consideradas três possibilidades de extração:

1. **Requests + BeautifulSoup:** adequada para páginas cujo conteúdo já está disponível no HTML recebido pelo servidor.
2. **Requests + consumo de arquivos JSON:** alternativa para situações em que a aba Network do navegador permite identificar requisições que disponibilizam os dados em formato estruturado.
3. **Selenium:** ferramenta para automatizar um navegador e acessar elementos que aparecem somente após a execução de JavaScript.

### Decisão técnica

Embora o Selenium tenha sido estudado e avaliado para a extração de páginas dinâmicas, sua utilização não foi considerada necessária para as fontes selecionadas na versão atual do projeto.

A série histórica do PRODES utilizada na aplicação é obtida por meio da exportação CSV do painel TerraBrasilis, evitando a necessidade de automatizar a navegação e a extração da tabela pelo navegador.

Para as notícias da Agência Brasil, o conteúdo é disponibilizado em HTML estático, permitindo a coleta com Requests e BeautifulSoup.

Portanto, a decisão foi priorizar ferramentas mais simples e adequadas à natureza de cada fonte, evitando a introdução de dependências e complexidade desnecessárias.

### Arquitetura de coleta

A coleta é executada separadamente da aplicação Streamlit. Os dados são processados e armazenados em arquivos CSV nos diretórios de dados do projeto. A aplicação consome os arquivos já preparados, evitando executar processos de scraping a cada acesso do usuário.

O Selenium permanece como alternativa técnica para futuras fontes que apresentem conteúdo carregado dinamicamente e que não disponibilizem uma API, arquivo estruturado ou requisição JSON acessível de forma mais simples.

### Critérios de utilização futura

A adoção do Selenium será considerada quando:

- O conteúdo necessário não estiver presente no HTML inicial.
- Não houver API ou requisição JSON acessível que permita obter os dados diretamente.
- Não existir uma opção de exportação estruturada adequada.
- A utilização da ferramenta respeitar as permissões, os termos de uso e as políticas de acesso da fonte.

Quando utilizado, o processo deverá empregar esperas explícitas por condições de carregamento dos elementos, tratamento de erros, fechamento do navegador e armazenamento dos resultados em CSV ou TXT fora da aplicação.

A decisão segue o princípio de utilizar a solução tecnicamente mais simples que atenda aos requisitos de coleta.


## Plano de Perguntas e Respostas (Q&A) com LLMs

### Objetivo

Planejar a implementação de uma funcionalidade de perguntas e respostas em linguagem natural, utilizando Large Language Models (LLMs), para facilitar a consulta e interpretação dos dados históricos de desmatamento da Amazônia Legal e das notícias relacionadas ao meio ambiente.

A proposta é permitir que analistas ambientais, pesquisadores e gestores consultem informações do projeto por meio de perguntas, recebendo respostas contextualizadas, acompanhadas de evidências e referências às fontes utilizadas.

### Fontes de conhecimento

A funcionalidade deverá utilizar duas fontes principais:

**1. Série histórica do PRODES — INPE/TerraBrasilis**

- Tipo: dados estruturados.
- Formato: CSV.
- Granularidade: unidade federativa e ano.
- Período disponível: 1988–2025.
- Campos principais:
  - `year`: ano de referência.
  - `area km²`: área desmatada em quilômetros quadrados.
  - `uf`: unidade federativa.

Finalidade: responder perguntas quantitativas e comparativas sobre a evolução do desmatamento, diferenças entre estados, períodos de maior intensidade e indicadores históricos.

**2. Notícias da Agência Brasil — EBC**

- Tipo: dados não estruturados, predominantemente textuais.
- Formato de origem: HTML.
- Formato processado: CSV.
- Campos principais:
  - `titulo`: título da notícia.
  - `data_publicacao`: data de publicação.
  - `texto`: conteúdo textual da matéria.
  - `url`: endereço original da publicação.

Finalidade: fornecer contexto jornalístico atualizado sobre acontecimentos relacionados à Amazônia, desmatamento, conservação ambiental e mudanças climáticas.

Os dados coletados serão armazenados em `data/processed/agencia_brasil_meio_ambiente.csv`, separados da execução da aplicação.

### Estratégia de implementação

A arquitetura proposta combinará processamento convencional de dados com recuperação de informações e geração de respostas por LLM.

**1. Preparação dos dados**

- Limpeza e padronização da série histórica do PRODES.
- Tratamento de valores ausentes e inconsistências.
- Preparação dos textos das notícias.
- Preservação de títulos, datas, URLs e identificação das fontes.
- Organização dos dados para consulta e recuperação de informações.

**2. Recuperação de informações**

Será considerada uma abordagem baseada em RAG (Retrieval-Augmented Generation), na qual o modelo recebe informações recuperadas das fontes do projeto antes de elaborar uma resposta.

Para as notícias, poderão ser utilizados mecanismos de busca textual ou embeddings para localizar matérias relacionadas à pergunta.

Para a série histórica do PRODES, as consultas quantitativas deverão utilizar filtros, agregações e cálculos executados por código, garantindo maior precisão numérica.

**3. Geração das respostas**

O LLM receberá a pergunta do usuário e o contexto recuperado, produzindo uma resposta em linguagem natural.

As respostas deverão:

- Utilizar exclusivamente as informações disponíveis nas fontes consultadas.
- Apresentar os resultados de forma clara e contextualizada.
- Identificar as fontes utilizadas.
- Incluir links para as notícias quando aplicável.
- Informar explicitamente quando não houver evidências suficientes para responder.

### Exemplos de perguntas previstas

**Perguntas sobre a série histórica do PRODES:**

- Qual estado apresentou a maior área desmatada no período analisado?
- Como evoluiu o desmatamento no Pará entre 2015 e 2025?
- Quais estados apresentaram aumento ou redução do desmatamento?
- Qual foi o ano com maior área desmatada na série histórica?
- Como comparar a evolução do desmatamento entre dois estados?

**Perguntas sobre as notícias da Agência Brasil:**

- Quais são os principais acontecimentos recentes relacionados à Amazônia?
- Quais notícias abordam ações de combate ao desmatamento?
- Quais medidas de conservação ambiental foram mencionadas nas matérias?
- Quais assuntos aparecem com maior frequência nas notícias coletadas?

**Perguntas combinando as duas fontes:**

- As notícias recentes apresentam acontecimentos relacionados aos estados com maiores índices de desmatamento?
- Quais acontecimentos divulgados pela Agência Brasil ajudam a contextualizar os indicadores do PRODES?
- Existem notícias relacionadas aos períodos em que foram observadas maiores taxas de desmatamento?

### Controle de qualidade e confiabilidade

Para reduzir respostas incorretas ou informações não sustentadas pelas fontes, serão adotadas as seguintes medidas:

- Separação entre dados oficiais do PRODES e informações complementares provenientes de notícias.
- Cálculos estatísticos realizados por funções Python, e não estimados pelo LLM.
- Recuperação de trechos relevantes antes da geração das respostas.
- Inclusão de referências às fontes utilizadas.
- Tratamento de perguntas sem evidências suficientes.
- Distinção entre fatos apresentados nas notícias e interpretações produzidas pelo modelo.

O LLM será utilizado como ferramenta de interpretação e comunicação das informações, não como substituto das fontes oficiais ou dos cálculos estatísticos.

### Escopo e evolução

A funcionalidade de Q&A com LLMs representa uma evolução planejada para o projeto, permitindo ampliar a interação com os dados e transformar o painel em uma ferramenta de consulta contextualizada.

Nesta etapa, o foco está na preparação das fontes, definição da arquitetura e planejamento da integração. A implementação efetiva do mecanismo de recuperação e geração de respostas será realizada em uma etapa posterior.

A funcionalidade não terá como objetivo realizar previsões de desmatamento, estabelecer relações causais entre notícias e indicadores ou substituir análises técnicas e decisões de especialistas.


## KPIs descritivos

1. Série temporal por estado e intervalo de anos.  

2. Soma dos valores por estado no recorte, identificada como agregado comparativo.  

3. Valor do ano mais recente por estado.  

4. Variação entre primeiro e último ano, tratando ausências/zeros.  

5. Quantidade de registros, estados e anos disponíveis.  

6. Quantidade de notícias e frequência de palavras. 

 7. Disponibilidade/validade das rotas GET e POST 


## Stakeholders

| Stakeholder | Interesse / utilizacao|
|----------|----------|
| Analistas ambientais e de sustentabilidade   | Explorar e comparar os dados de desmatamento e as informações contextuais das notícias   |
| Gestores públicos   | Utilizar os indicadores como apoio à análise e definição de prioridades de monitoramento   |
| Responsáveis por programas de conservação    | Consultar a evolução territorial e temporal do desmatamento   |
| Usuários da aplicação    | Aplicar filtros, consultar notícias e complementar os dados por upload de CSV   |

## ODS 13 

O projeto está alinhado ao ODS 13 — Ação Contra a Mudança Global do Clima, ao utilizar dados sobre desmatamento para apoiar a análise de um fenômeno relacionado às mudanças climáticas e à conservação dos ecossistemas.
