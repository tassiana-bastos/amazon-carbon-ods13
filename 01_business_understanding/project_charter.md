# Project Charter — Amazônia Legal | ODS 13

**Repositório:** https://github.com/tassiana-bastos/amazon-carbon-ods13
**Natureza do projeto:** aplicação exploratória de Ciência de Dados, com dashboard, processamento de dados ambientais, coleta de notícias, API e interação conversacional com LLM.
**Documento:** visão integrada do projeto e de sua evolução, incluindo as funcionalidades desenvolvidas até o TP5.

## 1. Contexto e problema de negócio

O desmatamento na Amazônia Legal é um fenômeno ambiental relevante para a conservação dos ecossistemas e para a discussão sobre mudanças climáticas. A análise exige consultar dados quantitativos organizados por território e ano e, quando disponível, informações textuais que ajudem a contextualizar acontecimentos relacionados ao tema.

O projeto reúne essas fontes em uma aplicação exploratória para permitir que estudantes, pesquisadores, analistas e demais usuários consultem indicadores, comparem registros por Unidade Federativa (UF), explorem notícias ambientais e interajam com os dados por meio de uma interface conversacional.

A aplicação oferece apoio à exploração e interpretação das informações disponíveis. Não substitui estudos especializados, bases oficiais completas ou processos de decisão de políticas públicas.

## 2. Pergunta orientadora

Como os registros históricos de desmatamento disponíveis para a Amazônia Legal se distribuem entre as Unidades Federativas e ao longo dos anos, e como notícias ambientais coletadas podem complementar a exploração desses dados?

## 3. Objetivo geral

Desenvolver e manter uma aplicação multipágina que integre dados estruturados de desmatamento, notícias ambientais coletadas, visualizações, recursos de ingestão e exportação, uma API e uma interface de perguntas e respostas com memória conversacional, mantendo rastreabilidade das fontes e explicitando as limitações dos dados.

## 4. Objetivos específicos

- Organizar e explorar a série histórica do PRODES/TerraBrasilis por UF e ano.
- Apresentar indicadores descritivos, filtros, tabelas e gráficos para apoiar comparações territoriais e temporais.
- Coletar e processar notícias da Agência Brasil relacionadas ao meio ambiente e à Amazônia.
- Apresentar notícias, estatísticas textuais e nuvem de palavras a partir do conteúdo processado.
- Permitir o envio de arquivos CSV para complementar a exploração de notícias e o download dos dados exibidos, conforme os recursos implementados na aplicação.
- Utilizar cache e estado de sessão no Streamlit para apoiar a interação com os dados.
- Disponibilizar uma API FastAPI para consulta dos dados, apresentação de resumo, registro de observações e interação conversacional.
- Integrar um LLM remoto por meio do OpenRouter para responder a perguntas em linguagem natural com contexto dos dados disponíveis.
- Manter o histórico de cada conversa, permitindo perguntas de acompanhamento e retomada da conversa.
- Documentar fontes, decisões técnicas, limitações, segurança e procedimentos de execução.

## 5. Público-alvo e stakeholders

- Estudantes e pesquisadores interessados em dados ambientais e no uso de IA aplicada.
- Analistas ambientais e de sustentabilidade que desejem explorar os registros disponíveis.
- Gestores e equipes de conservação que possam utilizar os indicadores como apoio exploratório, sem tratar a aplicação como instrumento automático de decisão.
- Usuários da aplicação que consultem notícias, enviem arquivos ou utilizem a interface conversacional.
- Desenvolvedores e consumidores técnicos interessados na API.

## 6. Escopo do projeto

### 6.1 Funcionalidades implementadas e documentadas

**Dashboard Streamlit**
- Aplicação multipágina com áreas de visão geral, indicadores de desmatamento, notícias e contexto, dados/arquivos, integração com API e memória conversacional.
- Apresentação de indicadores descritivos, filtros, tabelas e visualizações relativos aos dados disponíveis.
- Página de notícias com exploração do conteúdo processado, estatísticas textuais e nuvem de palavras.
- Recursos de upload e download de CSV na área de dados, observadas as validações e limitações da implementação.
- Uso de cache e estado de sessão nas funcionalidades que deles necessitam.

**Dados e coleta**
- Utilização de uma série histórica PRODES/TerraBrasilis fornecida em CSV, com campos `year`, `area km²` e `uf`.
- Coleta separada de páginas HTML da Agência Brasil com Requests e BeautifulSoup, seguida de armazenamento dos conteúdos processados em CSV.
- Separação entre arquivos de origem, dados processados e execução da aplicação.

**API**
- API construída com FastAPI, com documentação OpenAPI.
- Rotas de saúde, consulta de desmatamento, resumo agregado, registro de observações e recursos de conversa.
- Validação dos dados de entrada e respostas HTTP para erros de validação, recursos inexistentes ou indisponibilidade do provedor, conforme os contratos implementados.
- A rota legada `/processar_texto` é mantida na implementação TP5 para compatibilidade, utilizando o provedor remoto, e não um modelo carregado localmente.

**Memória conversacional com LLM — TP5, Opção 1**
- Integração com LLM remoto por meio da API OpenRouter; o projeto não precisa carregar os pesos de um modelo local para essa funcionalidade.
- Identificação independente de conversas por UUID.
- Persistência do histórico de cada conversa em arquivo JSON separado.
- Extração por Python de notas simples sobre entidades/UFs mencionadas no histórico.
- Envio de uma janela recente de mensagens, das notas e dos fatos calculados a partir do PRODES ao modelo.
- Recuperação lexical de notícias da Agência Brasil para fornecer contexto e referências quando houver correspondência.
- Possibilidade de restaurar e apagar uma conversa.
- Configuração da chave por variável de ambiente/arquivo `.env`, sem versionar o segredo.

### 6.2 Evolução histórica

O projeto foi desenvolvido incrementalmente. As etapas anteriores estabeleceram a compreensão do problema, a organização das fontes, a aplicação Streamlit, a coleta e apresentação de notícias e a API. A etapa TP4 documentou e experimentou uma abordagem de classificação textual com modelo local Qwen. Na evolução para o TP5, a implementação conversacional foi direcionada à Opção 1, com LLM remoto via OpenRouter, para evitar a necessidade de carregar pesos de modelo no ambiente de execução.

A documentação e os arquivos históricos das etapas anteriores podem ser mantidos no repositório como registro do processo. A abordagem local do TP4 não deve ser descrita como mecanismo ativo da memória conversacional TP5.

### 6.3 Fora do escopo / não alegado como funcionalidade entregue

- Previsão de desmatamento ou modelos preditivos de risco ambiental.
- Estimativa direta de carbono irrecuperável ou emissões de gases de efeito estufa a partir do CSV atual.
- Inferência causal entre notícias, variações de desmatamento e impactos sociais.
- Avaliação quantitativa da situação de povos indígenas, conflitos territoriais ou serviços essenciais, pois esses indicadores não integram as fontes quantitativas descritas neste documento.
- Sistema RAG semântico baseado em embeddings ou busca vetorial: a recuperação de notícias descrita na versão TP5 é lexical.
- Tomada automática de decisão ou recomendação oficial de políticas públicas.
- Garantia de disponibilidade contínua do modelo gratuito ou de limites de uso do provedor externo.

## 7. Fontes de dados e método em alto nível

1. **INPE/PRODES via TerraBrasilis:** série estruturada em CSV, com registros por UF e ano, utilizada para indicadores e fatos numéricos.
2. **Agência Brasil/EBC:** páginas HTML coletadas e processadas em CSV, utilizadas na seção de notícias e na recuperação lexical de contexto.
3. **CSV enviado pelo usuário:** entrada complementar para a exploração de notícias, sujeita à validação implementada na aplicação.
4. **Observações enviadas à API:** contribuições armazenadas separadamente em JSONL; não são tratadas automaticamente como dados oficiais.
5. **Histórico conversacional:** mensagens armazenadas por conversa em JSON, utilizadas para manter contexto entre turnos.

Os detalhes de campos, período, preparação, qualidade e limitações estão descritos no documento Data Summary Report.

## 8. Indicadores de acompanhamento do projeto

Os indicadores descritivos utilizados na aplicação incluem, conforme o recorte e a disponibilidade dos dados:

- Quantidade de registros, UFs e anos presentes na base.
- Valores de desmatamento por UF e ano.
- Comparações entre UFs e períodos.
- Valor mais recente disponível por UF.
- Variação entre anos selecionados quando há registros comparáveis.
- Quantidade de notícias processadas e estatísticas textuais.
- Disponibilidade das rotas da API e dos recursos conversacionais.
- Quantidade de mensagens/histórico por conversa, quando exibida pela interface.

As somas de valores anuais devem ser identificadas como agregações comparativas da série, não como uma área geográfica única acumulada. A interpretação depende da definição do indicador e da cobertura dos registros.

## 9. Arquitetura e decisões técnicas

- **Interface:** Streamlit multipágina.
- **Serviço de API:** FastAPI.
- **Dados estruturados:** CSV e processamento com Python.
- **Coleta web:** Requests e BeautifulSoup para as páginas HTML selecionadas da Agência Brasil.
- **LLM:** provedor remoto acessado pelo OpenRouter; o identificador do modelo é configurável por variável de ambiente.
- **Memória:** arquivos JSON por UUID, notas extraídas por Python e janela recente de mensagens.
- **Recuperação de notícias:** correspondência lexical simples; não equivale a recuperação semântica completa.
- **Persistência de observações:** arquivo JSONL separado.
- **Versionamento:** Git e GitHub.

A escolha por exportação CSV para a série PRODES evita automatizar a navegação do painel quando o arquivo estruturado já atende à necessidade. Para as páginas da Agência Brasil selecionadas, Requests e BeautifulSoup foram utilizados. Selenium foi avaliado, mas não é necessário para as fontes e o fluxo descritos nesta versão.

## 10. Segurança, privacidade e riscos

- A chave OpenRouter deve permanecer em `.env` ou em variável de ambiente do servidor e nunca ser adicionada ao Git.
- O diretório `data/conversas/` contém histórico fornecido por usuários e deve permanecer fora do versionamento.
- Observações e conversas não devem ser tratadas como fontes oficiais verificadas.
- Como o LLM é acessado por um provedor externo, o conteúdo enviado no contexto da requisição é processado por terceiro. Não inserir informações pessoais ou sensíveis.
- O modelo pode produzir respostas incorretas; números devem ser calculados em Python e respostas devem ser verificadas.
- A recuperação lexical pode não encontrar notícias relevantes quando a pergunta utiliza sinônimos ou termos diferentes.
- Antes de disponibilizar a API publicamente para uso amplo, devem ser avaliados autenticação, limitação de requisições, política de retenção e controles de acesso.

## 11. Critérios de sucesso

- O dashboard permite navegar pelas funcionalidades implementadas sem eliminar as páginas anteriores.
- Os indicadores quantitativos são derivados dos dados processados, e não inventados pelo LLM.
- As notícias preservam título, data e URL para rastreabilidade.
- A API expõe contratos documentados e valida as entradas.
- A conversa mantém contexto entre mensagens e permite recuperar/apagar uma conversa.
- A integração com o provedor utiliza segredo fora do código e do Git.
- A documentação descreve o estado real da aplicação, suas fontes e limitações.

## 12. Reprodutibilidade

Os procedimentos de instalação, configuração das variáveis de ambiente, inicialização do FastAPI e do Streamlit e execução dos testes devem ser mantidos atualizados no README e na documentação técnica do repositório.

**Repositório:** https://github.com/tassiana-bastos/amazon-carbon-ods13
