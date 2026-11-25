# Data Summary Report — Amazônia Legal | ODS 13

**Repositório:** https://github.com/tassiana-bastos/amazon-carbon-ods13
**Finalidade:** documentar as fontes, estruturas, preparação, utilização, qualidade e limitações dos dados empregados no projeto como um todo, incluindo a funcionalidade de memória conversacional integrada no TP5.

## 1. Visão geral

A aplicação combina dados ambientais estruturados, conteúdo jornalístico coletado, arquivos CSV enviados pelo usuário, observações recebidas pela API e histórico conversacional. Essas categorias possuem finalidades e níveis de confiabilidade diferentes e não devem ser tratadas como se fossem uma única base homogênea.

| Fonte/conjunto | Formato | Granularidade / campos conhecidos | Utilização |
|---|---|---|---|
| INPE/PRODES via TerraBrasilis | CSV | Registro por UF e ano; `year`, `area km²`, `uf` | Indicadores, filtros, tabelas, gráficos, API e fatos quantitativos fornecidos ao LLM |
| Agência Brasil/EBC | HTML de origem; CSV processado | Uma linha por notícia; `titulo`, `data_publicacao`, `texto`, `url`, `origem` | Página de notícias, estatísticas textuais, nuvem de palavras e recuperação lexical para contexto conversacional |
| CSV enviado pelo usuário | CSV | Estrutura depende do arquivo submetido; utilizado na área de dados/notícias | Complementar a exploração de notícias, sujeito às validações implementadas |
| Observações recebidas pela FastAPI | JSONL | `titulo`, `texto`, `fonte` opcional e timestamp de criação | Registrar contribuições separadamente das fontes oficiais |
| Histórico de conversas | JSON, um arquivo por UUID | Mensagens com papéis `user`/`assistant`, timestamps e notas derivadas | Manter contexto, permitir perguntas de acompanhamento, restauração e exclusão da conversa |

## 2. Dados quantitativos — INPE/PRODES via TerraBrasilis

### 2.1 Fonte e arquivo

- **Instituição/fonte:** INPE, por meio da plataforma TerraBrasilis.
- **Painel de referência:** https://terrabrasilis.dpi.inpe.br/app/dashboard/deforestation/biomes/legal_amazon/rates
- **Arquivo utilizado:** `data/raw/terrabrasilis_legal_amazon_23_08_2026_1787514448882.csv`.
- **Formato:** CSV separado por ponto e vírgula (`;`).
- **Campos observados:** `year`, `area km²`, `uf`.
- **Granularidade:** Unidade Federativa × ano.
- **Unidade informada no campo de área:** km².
- **Cobertura observada no arquivo documentado:** 336 registros, nove UFs e anos de 1988 a 2025.

A quantidade de registros não equivale necessariamente a todas as combinações possíveis de UF e ano. A série contém registros esparsos; a ausência de uma linha não deve ser interpretada automaticamente como valor zero.

### 2.2 Preparação e normalização

Os valores de área no arquivo utilizam convenção numérica brasileira, por exemplo `7.845,00`. O processamento remove o separador de milhar e converte a vírgula decimal para ponto antes de transformar o valor em número. O campo `year` é convertido para inteiro e a UF é normalizada como texto.

Linhas com campos ausentes ou valores que não podem ser convertidos são ignoradas pelas rotinas de leitura descritas na implementação. Os dados preparados são utilizados pela camada de acesso a dados e pela API.

### 2.3 Uso na aplicação

A série PRODES é a fonte quantitativa principal para:

- filtros por UF e intervalo de anos;
- indicadores descritivos e comparações;
- tabelas e gráficos;
- consultas pela API, incluindo `/desmatamento` e `/resumo`;
- preparação de fatos numéricos enviados no contexto da conversa com o LLM.

Os cálculos quantitativos são realizados por Python. O LLM recebe os fatos preparados e os utiliza para explicar os resultados; não deve ser encarregado de inventar ou estimar valores ausentes.

### 2.4 Limitações de interpretação

- O arquivo representa os campos e o recorte exportado descritos acima; não se deve presumir que contenha todas as variáveis ambientais ou sociais da Amazônia Legal.
- A série não contém, por si só, medidas diretas de carbono irrecuperável, emissões de GEE, situação fundiária, saúde, conflitos ou indicadores específicos de povos indígenas.
- A soma de taxas/valores anuais não deve ser apresentada como área geográfica única acumulada.
- Comparações entre anos devem considerar a disponibilidade efetiva de registros e a definição do indicador.
- A ausência de registro não equivale a zero sem confirmação na fonte.

## 3. Dados textuais — Agência Brasil/EBC

### 3.1 Fonte e coleta

- **Fonte:** Agência Brasil — https://agenciabrasil.ebc.com.br/
- **Formato de origem:** páginas HTML.
- **Método documentado:** coleta separada da aplicação, utilizando Requests e BeautifulSoup.
- **Verificação prévia:** o `robots.txt` da fonte foi consultado durante o trabalho de coleta.
- **Arquivo processado:** `data/processed/agencia_brasil_meio_ambiente.csv`.
- **Quantidade documentada na versão TP5:** cinco notícias.

As páginas utilizadas como fontes na documentação incluem:

- https://agenciabrasil.ebc.com.br/meio-ambiente/noticia/2026-09/devastacao-na-amazonia-pode-quebrar-maior-maquina-de-chuva-do-mundo
- https://agenciabrasil.ebc.com.br/meio-ambiente/noticia/2026-08/imazon-aponta-desmatamento-zero-em-60-de-terras-indigenas-na-amazonia
- https://agenciabrasil.ebc.com.br/geral/noticia/2016-05/amazonia-ameacada-guardioes-lutam-para-manter-floresta-em-pe
- https://agenciabrasil.ebc.com.br/meio-ambiente/noticia/2026-09/competitividade-do-mercado-de-carbono-moderniza-conservacao-florestal
- https://agenciabrasil.ebc.com.br/meio-ambiente/noticia/2026-10/incendios-avancam-sobre-o-oeste-do-para-e-deixam-ar-insalubre

### 3.2 Estrutura do CSV

O arquivo processado contém os campos:

| Campo | Descrição |
|---|---|
| `titulo` | Título da notícia |
| `data_publicacao` | Data/hora de publicação extraída |
| `texto` | Conteúdo textual processado |
| `url` | Endereço original da matéria |
| `origem` | Procedência do registro, quando disponível; na aplicação pode ser preenchida como `coletada` para registros sem valor |

### 3.3 Uso na aplicação

As notícias alimentam a página de notícias, a apresentação tabular, estatísticas textuais e nuvem de palavras. Na funcionalidade conversacional TP5, a rotina de recuperação realiza correspondência lexical simples entre termos da pergunta/contexto recente e o título/texto das matérias. Até três notícias correspondentes podem ser incluídas no contexto enviado ao LLM, preservando título, data, trecho e URL para inspeção.

### 3.4 Limitações

- A base documentada contém cinco matérias e não representa cobertura jornalística abrangente.
- A recuperação é lexical; não utiliza embeddings nem busca vetorial semântica.
- Uma notícia não comprova causalidade com uma variação observada no PRODES.
- Datas, títulos, trechos e URLs devem ser mantidos para rastreabilidade.
- O conteúdo jornalístico é fonte contextual, não substitui os dados oficiais quantitativos.

## 4. Arquivos CSV enviados pelo usuário

A aplicação possui funcionalidade de upload de CSV na área de dados/notícias para complementar a exploração do conteúdo disponível. A estrutura e a procedência do arquivo submetido devem ser verificadas conforme as validações da página. Os registros coletados e os registros enviados são identificados separadamente, por exemplo, como `coletada` e `enviada`.

O upload não transforma automaticamente o conteúdo em fonte oficial ou verificada. Arquivos externos devem ser tratados como entradas não confiáveis e analisados considerando seus campos, procedência e qualidade.

## 5. Observações recebidas pela API

A API possui uma operação `POST /observacoes` para receber observações estruturadas com título, texto e fonte opcional. Os registros são armazenados em `data/processed/observacoes.jsonl` com timestamp UTC.

Essas observações são contribuições de usuários. Não são incorporadas automaticamente à base oficial PRODES nem tratadas como fatos verificados. O arquivo de observações gerado localmente deve permanecer fora do versionamento quando contiver dados submetidos durante a execução.

## 6. Histórico e memória conversacional — TP5

### 6.1 Persistência

Cada conversa recebe um identificador UUID e tem seu histórico armazenado separadamente em JSON no diretório `data/conversas/`. O histórico contém mensagens do usuário e do assistente, além de timestamps e notas derivadas utilizadas para apoiar a continuidade da interação.

O Streamlit mantém o identificador da conversa na sessão e utiliza o parâmetro de URL `?conversa=` para permitir a retomada. A API disponibiliza operações para criar, recuperar, atualizar por novas mensagens e excluir conversas.

### 6.2 Notas e janela de contexto

A estratégia documentada combina:
- notas simples de entidades/UFs extraídas por Python do histórico de mensagens do usuário;
- uma janela recente de até cinco mensagens enviada ao modelo;
- fatos quantitativos calculados em Python a partir do PRODES;
- notícias recuperadas por correspondência lexical, quando disponíveis.

A extração de notas não exige uma chamada adicional ao LLM. Essa estratégia reduz o volume de histórico enviado, mas não equivale a uma memória semântica completa: as notas descritas concentram-se em nomes e siglas de UFs.

### 6.3 Envio ao provedor

A aplicação utiliza um LLM remoto por meio do OpenRouter. A chave é lida no servidor por variável de ambiente ou arquivo `.env`; não deve ser exposta no código, na interface ou no repositório. O modelo configurado é selecionado por `OPENROUTER_MODEL`, podendo variar conforme a configuração do ambiente.

O contexto enviado ao provedor pode incluir a pergunta, mensagens recentes, notas, fatos PRODES e trechos de notícias recuperados. Como esse processamento ocorre por meio de um serviço externo, não devem ser inseridos dados pessoais ou sensíveis.

### 6.4 Limitações e tratamento de falhas

A memória depende da persistência local dos arquivos e da disponibilidade da API/provedor. A integração deve tratar erros de autenticação, limite de requisições, timeout, indisponibilidade e resposta vazia. A disponibilidade e os limites de modelos gratuitos podem mudar conforme as condições do provedor.

Os arquivos em `data/conversas/` não devem ser versionados, pois podem conter conteúdo fornecido por usuários.

## 7. API — recursos relacionados aos dados

A API FastAPI disponibiliza, na implementação documentada, os seguintes recursos:

| Método | Endpoint | Finalidade |
|---|---|---|
| GET | `/` | Informações básicas e estado da API |
| GET | `/saude` | Verificação de saúde/configuração do serviço e do LLM |
| GET | `/desmatamento` | Consulta registros PRODES com filtros opcionais por UF e período |
| GET | `/resumo` | Metadados e agregação/ranking descritivo por UF |
| POST | `/observacoes` | Registro de observação em JSONL |
| POST | `/conversas` | Criação de conversa |
| GET | `/conversas/{conversation_id}` | Recuperação do histórico de uma conversa |
| POST | `/conversas/{conversation_id}/mensagens` | Envio de mensagem e geração de resposta contextual |
| DELETE | `/conversas/{conversation_id}` | Exclusão da conversa |
| POST | `/processar_texto` | Rota legada de processamento textual mantida para compatibilidade na implementação TP5, utilizando o provedor remoto |

A documentação OpenAPI pode ser consultada em `/docs` quando a API estiver em execução. Os contratos efetivos devem ser conferidos no código atual de `api/main.py`.

## 8. Qualidade, governança e segurança dos dados

- Preservar a fonte e a URL dos registros jornalísticos.
- Validar e normalizar campos antes de calcular indicadores.
- Não converter ausência de registro em zero sem respaldo na fonte.
- Manter dados quantitativos oficiais separados de notícias, uploads, observações e mensagens.
- Calcular indicadores numéricos com código determinístico em Python.
- Tratar arquivos enviados e observações como dados não verificados.
- Não versionar `.env`, `data/conversas/`, arquivos locais de observações, ambientes virtuais, bytecode, caches ou pesos de modelos.
- Evitar inserir dados pessoais/sensíveis em conversas enviadas a provedores externos.
- Apresentar as limitações da recuperação lexical e da cobertura reduzida de notícias.

## 9. Organização dos arquivos de dados

| Caminho | Conteúdo |
|---|---|
| `data/raw/` | CSV original do PRODES e arquivos brutos de coleta, conforme mantidos no projeto |
| `data/processed/` | CSV processado da Agência Brasil e arquivos derivados |
| `data/processed/observacoes.jsonl` | Observações geradas por chamadas à API; manter fora do Git quando contiver contribuições locais |
| `data/conversas/` | Histórico JSON por conversa; manter fora do Git |

## 10. Reprodutibilidade

Na versão documentada, a execução requer instalar as dependências de `requirements.txt`, configurar `OPENROUTER_API_KEY` e, opcionalmente, `OPENROUTER_MODEL` no ambiente local, iniciar a API FastAPI e iniciar o dashboard Streamlit em terminais separados.

Comandos de referência:

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
streamlit run app.py
pytest -q
```

A chave real deve ser definida localmente no `.env` ou no ambiente de hospedagem. O arquivo `.env` não deve ser enviado ao GitHub.

## 11. Limitações gerais do conjunto de dados

O conjunto atual permite análise descritiva da série PRODES e exploração contextual de um conjunto pequeno de notícias. Não contém variáveis suficientes para medir diretamente carbono irrecuperável, emissões, impactos sociais, situação territorial de povos indígenas ou relações causais entre eventos jornalísticos e taxas de desmatamento. Essas análises exigiriam fontes adicionais, documentadas e validadas antes de serem incorporadas ao projeto.
