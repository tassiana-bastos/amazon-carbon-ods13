# Data Summary Report

Documento de levantamento e caracterizacao das fontes de dados utilizadas no projeto.

## Resumo das fontes

| Fonte | Tipo de dado | Objetivo de uso |
|----------|----------|----------|
| INPE – PRODES, disponibilizado pela plataforma TerraBrasilis   | Estruturado — CSV; granularidade Estado × ano; unidade km²; período 1988–2025   | Analisar a evolução temporal e a intensidade do desmatamento nos estados da Amazônia Legal e permitir comparações entre os territórios.   |
| Agência Brasil   | Não estruturado — HTML/texto, processado e armazenado em CSV   | Contextualizar acontecimentos recentes relacionados à Amazônia, desmatamento e mudanças climáticas; alimentar a seção de notícias, estatísticas básicas e nuvem de palavras.   |
| Arquivo CSV enviado pelo usuário   | Estruturado — CSV   | Complementar as informações de notícias já apresentadas na aplicação. Os registros enviados são identificados pela procedência “enviada”.   |


### 1. INPE – PRODES / TerraBrasilis

**Pagina de consulta:** TerraBrasilis — Dashboard PRODES — Taxas de Desmatamento — Amazônia Legal.
  
**Consulta utilizada:** Taxas de desmatamento — Amazônia Legal — Estados — série histórica completa — exportação/CSV.

**Campos extraidos:** year, area km², uf.

**Período:** 1988–2025.

**Unidade:** km².

**Granularidade:** Estado x ano.

**Formato:** CSV.

**Utilizacao:** o conjunto constitui a base principal da análise quantitativa da aplicação, sendo utilizado nos indicadores, filtros e comparações entre os estados.

**Fonte/URL de consulta:** https://terrabrasilis.dpi.inpe.br/app/dashboard/deforestation/biomes/legal_amazon/rates

### 2. Agência Brasil

A Agência Brasil foi utilizada como fonte de conteúdo web para a etapa de web scraping.

O conteúdo das páginas foi coletado separadamente do código da aplicação utilizando requests e BeautifulSoup. Antes da coleta, foi verificado o robots.txt da fonte. O conteúdo processado foi armazenado em data/processed/agencia_brasil_meio_ambiente.csv.

**Campos armazenados:** titulo, data_publicacao, texto, url.

**Tipo:** não estruturado — HTML/texto, posteriormente estruturado em CSV.

**Utilização:** complementar a análise quantitativa com informações contextuais recentes e alimentar a tabela de notícias, estatísticas básicas e nuvem de palavras da aplicação.

### 3. Arquivos CSV enviados pelo usuário

A aplicação permite o envio de arquivos CSV para complementar os dados de notícias existentes.

Os registros enviados são incorporados ao estado de sessão da aplicação e recebem a identificação de procedência enviada, enquanto os registros obtidos pela coleta web são identificados como coletada.

O download disponibilizado pela aplicação corresponde ao recorte atualmente exibido após a aplicação dos filtros.

### Procedencia e Organizacao

Os dados coletados da web e os dados utilizados pela aplicação são mantidos em etapas separadas. A coleta é executada por código próprio, enquanto a aplicação Streamlit utiliza os arquivos processados armazenados no diretório data/.

Essa separação permite reproduzir a coleta sem depender da execução do scraping a cada abertura da aplicação.


