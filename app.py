import csv
from pathlib import Path
import io
import re
from collections import Counter

import streamlit as st
from wordcloud import WordCloud

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------

st.set_page_config(
    page_title="Amazônia Legal | ODS 13",
    page_icon="🌳",
    layout="wide"
)


# ---------------------------------------------------------
# CAMINHO DOS ARQUIVOS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

CSV_DESMATAMENTO = (
    BASE_DIR
    / "data"
    / "raw"
    / "terrabrasilis_legal_amazon_23_08_2026_1787514448882.csv"
)

CSV_NOTICIAS = (
    BASE_DIR
    / "data"
    / "processed"
    / "agencia_brasil_meio_ambiente.csv"
)

# ============================================================
# CACHE — CARREGAMENTO DO CSV DE DESMATAMENTO
# ============================================================

@st.cache_data # com isso o Streamlit nao precisa refazer a leitura e o processamento desses arquivos a cada interacao.
def carregar_dados_desmatamento(caminho, ultima_modificacao):

    dados = []

    with open(
        caminho,
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:

        leitor = csv.DictReader(
            arquivo,
            delimiter=";"
        )

        for linha in leitor:
            dados.append(linha)

    return dados


# ============================================================
# CACHE — CARREGAMENTO DAS NOTÍCIAS
# ============================================================

@st.cache_data
def carregar_noticias(caminho, ultima_modificacao):

    noticias = []

    with open(
        caminho,
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:

        leitor = csv.DictReader(arquivo)

        for linha in leitor:

            # Compatibilidade com o CSV atual, que ainda nao possui a coluna "origem".
            linha["origem"]= (
                linha.get("origem")
                or "coletada"
            )

            noticias.append(linha)

    return noticias


# ============================================================
# CARREGAR DADOS DE DESMATAMENTO
# ============================================================

try:

    modificacao_desmatamento = (
        CSV_DESMATAMENTO.stat().st_mtime_ns
    )

    dados_desmatamento= carregar_dados_desmatamento(
        CSV_DESMATAMENTO,
        modificacao_desmatamento
    )

except FileNotFoundError:

    st.error(
        "Não foi possível encontrar o arquivo de "
        "desmatamento em data/raw/."
    )

    st.stop()

# ============================================================
# CARREGAR NOTÍCIAS
# ============================================================

try:

    modificacao_noticias=(
        CSV_NOTICIAS.stat().st_mtime_ns
    )

    noticias_base = carregar_noticias(
        CSV_NOTICIAS, 
        modificacao_noticias
    )

except FileNotFoundError:

    noticias_base = []


# ============================================================
# ESTADO DE SESSÃO
# ============================================================

if "noticias" not in st.session_state:

    st.session_state.noticias = list(
        noticias_base
    )


# ---------------------------------------------------------
# TÍTULO DO PROJETO
# ---------------------------------------------------------

st.title("🌳 Monitoramento do Desmatamento na Amazônia Legal")

st.subheader(
    "Aplicação Demo — Projeto de Bloco | ODS 13"
)


# ---------------------------------------------------------
# PROBLEMA DE NEGÓCIO
# ---------------------------------------------------------

st.header("1. Problema de Negócio")

st.write(
    """
    O desmatamento na Amazônia Legal representa um desafio para a
    conservação dos ecossistemas e para o enfrentamento das mudanças
    climáticas.

    Este projeto busca utilizar dados de desmatamento para apoiar a
    identificação dos territórios da Amazônia Legal que apresentam
    maior necessidade de atenção e monitoramento, contribuindo para
    uma tomada de decisão orientada por dados.
    """
)


# ---------------------------------------------------------
# OBJETIVOS
# ---------------------------------------------------------

st.header("2. Objetivos do Projeto")

st.markdown(
    """
    - Organizar dados históricos de desmatamento da Amazônia Legal.
    - Permitir a visualização inicial dos dados por território e ano.
    - Identificar diferenças na área desmatada entre os territórios.
    - Apoiar o monitoramento de áreas que merecem maior atenção.
    - Incorporar informações externas relacionadas ao tema.
    - Contribuir para discussões relacionadas às mudanças climáticas
      e ao ODS 13 — Ação Contra a Mudança Global do Clima.
    """
)


# ---------------------------------------------------------
# TIPO DA PERGUNTA
# ---------------------------------------------------------

st.header("3. Tipo da Pergunta")

st.info(
    """
    A aplicação possui caráter predominantemente descritivo:
    busca apresentar o comportamento do desmatamento ao longo
    do período disponível e complementar essa análise com
    informações jornalísticas relacionadas ao meio ambiente
    e à Amazônia.
    """
)

# ============================================================
# DADOS DE DESMATAMENTO
# ============================================================
st.header("4. Dados de Desmatamento")

# ------------------------------------------------------------
# Preparação dos valores para os filtros
# ------------------------------------------------------------

ufs = sorted(
    {
        linha.get("uf", "")
        for linha in dados_desmatamento
        if linha.get("uf")
    }
)

anos = sorted(
    {
        int(linha["year"])
        for linha in dados_desmatamento
        if linha.get("year")
    }
)

# ------------------------------------------------------------
# Filtros
# ------------------------------------------------------------

coluna1, coluna2= st.columns(2)

with coluna1:

    uf_selecionada = st.selectbox(
        "Selecione a UF",
        options=["Todas"] + ufs
    )

with coluna2:

    ano_selecionado = st.selectbox(
        "Selecione o ano",
        options=["Todos"] + anos
    )

# ------------------------------------------------------------
# Aplicar filtros
# ------------------------------------------------------------

dados_filtrados = dados_desmatamento.copy()

if uf_selecionada != "Todas":

    dados_filtrados = [
        linha
        for linha in dados_filtrados
        if linha.get("uf") == uf_selecionada
    ]

if ano_selecionado != "Todos":

    dados_filtrados = [
        linha
        for linha in dados_filtrados
        if linha.get("year")
        and int(linha["year"]) == ano_selecionado
    ]


# ------------------------------------------------------------
# Métricas
# ------------------------------------------------------------

coluna1, coluna2, coluna3 = st.columns(3)

with coluna1:

    st.metric(
        "Registros",
        len(dados_filtrados)
    )

with coluna2:

    if dados_filtrados:

        anos_filtrados = [
            int(linha["year"])
            for linha in dados_filtrados
            if linha.get("year")
        ]

        st.metric(
            "Ano inicial",
            min(anos_filtrados)
        )

with coluna3:

    if dados_filtrados:

        st.metric(
            "Ano final",
            max(anos_filtrados)
        )
# ------------------------------------------------------------
# Tabela
# ------------------------------------------------------------

st.subheader("Dados filtrados")

st.dataframe(
    dados_filtrados,
    width="stretch"
)

# ============================================================
# NOTÍCIAS
# ============================================================

st.header(
    "5. Notícias e Conteúdo Web"
)

st.write(
    """
    As notícias apresentadas nesta seção foram coletadas
    separadamente por meio de web scraping com Beautiful Soup
    e armazenadas em CSV antes de serem utilizadas pela aplicação.
    """
)

# ============================================================
# FILTROS DAS NOTÍCIAS
# ============================================================

noticias = st.session_state.noticias


coluna1, coluna2 = st.columns(2)


with coluna1:

    origens_disponiveis = sorted(
        {
            noticia.get("origem", "coletada")
            for noticia in noticias
        }
    )

    origem_selecionada = st.selectbox(
        "Filtrar por origem",
        options=["Todas"] + origens_disponiveis
    )


with coluna2:

    termo_busca = st.text_input(
        "Buscar nas notícias",
        placeholder="Digite uma palavra ou expressão..."
    )

# ------------------------------------------------------------
# Aplicar filtros nas notícias
# ------------------------------------------------------------

noticias_filtradas = []

for noticia in noticias:

    origem = noticia.get(
        "origem",
        "coletada"
    )

    titulo = noticia.get(
        "titulo",
        ""
    )

    texto = noticia.get(
        "texto",
        ""
    )

    if (
        origem_selecionada != "Todas"
        and origem != origem_selecionada
    ):
        continue

    if termo_busca:

        conteudo_busca = (
            titulo + " " + texto
        ).lower()

        if termo_busca.lower() not in conteudo_busca:
            continue

    noticias_filtradas.append(noticia)

# ============================================================
# ESTATÍSTICAS DAS NOTÍCIAS
# ============================================================

total_noticias = len(
    noticias_filtradas
)

total_palavras = sum(
    len(
        noticia.get("texto", "").split()
    )
    for noticia in noticias_filtradas
)

total_caracteres = sum(
    len(
        noticia.get("texto", "")
    )
    for noticia in noticias_filtradas
)


coluna1, coluna2, coluna3 = st.columns(3)

with coluna1:

    st.metric(
        "Notícias",
        total_noticias
    )

with coluna2:

    st.metric(
        "Palavras",
        total_palavras
    )

with coluna3:

    st.metric(
        "Caracteres",
        total_caracteres
    )

# ============================================================
# TABELA RESUMIDA DAS NOTÍCIAS
# ============================================================

st.subheader(
    "Tabela de notícias"
)

tabela_noticias = [
    {
        "Título": noticia.get(
            "titulo",
            ""
        ),
        "Data de publicação": noticia.get(
            "data_publicacao",
            ""
        ),
        "Origem": noticia.get(
            "origem",
            "coletada"
        ),
        "URL": noticia.get(
            "url",
            ""
        )
    }
    for noticia in noticias_filtradas
]


if tabela_noticias:

    st.dataframe(
        tabela_noticias,
        width="stretch"
    )

else:

    st.info(
        "Nenhuma notícia corresponde aos filtros selecionados."
    )


# ============================================================
# CONTEÚDO DAS NOTÍCIAS
# ============================================================

st.subheader(
    "Conteúdo das notícias"
)


for noticia in noticias_filtradas:

    st.markdown(
        f"### {noticia.get('titulo', '')}"
    )

    st.write(
        f"**Publicado em:** "
        f"{noticia.get('data_publicacao', '')}"
    )

    st.write(
        f"**Origem:** "
        f"{noticia.get('origem', 'coletada')}"
    )

    texto = noticia.get(
        "texto",
        ""
    )

    if len(texto) > 500:

        st.write(
            texto[:500] + "..."
        )

    else:

        st.write(texto)

    url = noticia.get(
        "url",
        ""
    )

    if url:

        st.markdown(
            f"[Ler notícia original]({url})"
        )

    st.divider()

# ============================================================
# NUVEM DE PALAVRAS
# ============================================================

st.subheader(
    "Nuvem de palavras das notícias filtradas"
)


STOPWORDS = {
    "a", "à", "ao", "aos", "as",
    "com", "como", "da", "das",
    "de", "do", "dos", "e",
    "em", "entre", "era",
    "esse", "esta", "este",
    "foi", "foram", "há",
    "isso", "já", "mais",
    "mas", "na", "nas",
    "no", "nos", "não",
    "o", "os", "ou",
    "para", "pela", "pelas",
    "pelo", "pelos",
    "por", "que", "se",
    "sem", "ser", "sua",
    "suas", "seu", "seus",
    "também", "tem",
    "uma", "um", "uns",
    "umas", "sobre",
    "até", "quando",
    "onde", "porque",
    "são"
}


@st.cache_data
def preparar_frequencias(textos):

    texto_completo = " ".join(textos)

    palavras = re.findall(
        r"\b[a-záàâãéêíóôõúç]+\b",
        texto_completo.lower()
    )

    palavras_filtradas = [
        palavra
        for palavra in palavras
        if palavra not in STOPWORDS
        and len(palavra) > 2
    ]

    return Counter(
        palavras_filtradas
    )


textos_filtrados = tuple(
    noticia.get("texto", "")
    for noticia in noticias_filtradas
)


frequencias = preparar_frequencias(
    textos_filtrados
)


if frequencias:

    nuvem = WordCloud(
        width=1200,
        height=500,
        background_color="white",
        max_words=100
    ).generate_from_frequencies(
        frequencias
    )

    st.image(
        nuvem.to_array(),
        width="stretch"
    )

else:

    st.info(
        "Não existem textos suficientes "
        "para gerar a nuvem de palavras."
    )

# ============================================================
# UPLOAD DE CSV
# ============================================================

st.header(
    "6. Adicionar novas notícias"
)

st.write(
    """
    Você pode adicionar novas notícias ao conjunto de dados
    utilizando um arquivo CSV.

    O arquivo deve possuir as seguintes colunas:
    titulo, data_publicacao, texto e url.
    """
)


arquivo_upload = st.file_uploader(
    "Selecione um arquivo CSV",
    type=["csv"],
    key="upload_noticias"
)


if arquivo_upload is not None:

    if st.button(
        "Adicionar notícias ao sistema"
    ):

        try:

            conteudo = arquivo_upload.getvalue().decode(
                "utf-8-sig"
            )

            # Detectar automaticamente o separador do CSV
            primeira_linha= conteudo.splitlines()[0]

            if ";" in primeira_linha:
                delimitador= ";"
            else:
                delimitador= ","    

            leitor = csv.DictReader(
                io.StringIO(conteudo),
                delimiter=delimitador
            )

            colunas_obrigatorias = {
                "titulo",
                "data_publicacao",
                "texto",
                "url"
            }

            colunas_arquivo = set(
                leitor.fieldnames or []
            )

            if not colunas_obrigatorias.issubset(
                colunas_arquivo
            ):

                st.error(
                    "O arquivo não possui todas as "
                    "colunas obrigatórias: "
                    "titulo, data_publicacao, texto e url."
                )

            else:

                novas_noticias = []

                for linha in leitor:

                    linha["origem"] = "enviada"

                    novas_noticias.append(
                        linha
                    )

                # ------------------------------------------------
                # Evitar duplicação por URL
                # ------------------------------------------------

                urls_existentes = {
                    noticia.get("url", "")
                    for noticia in st.session_state.noticias
                }

                novas_noticias = [
                    noticia
                    for noticia in novas_noticias
                    if noticia.get("url", "")
                    not in urls_existentes
                ]

                if novas_noticias:

                    st.session_state.noticias.extend(
                        novas_noticias
                    )

                    st.success(
                        f"{len(novas_noticias)} notícia(s) "
                        "adicionada(s) com sucesso."
                    )

                else:

                    st.warning(
                        "Nenhuma nova notícia foi adicionada. "
                        "Os registros enviados já existem "
                        "no conjunto de dados."
                    )

        except Exception as erro:

            st.error(
                f"Não foi possível processar o arquivo: {erro}"
            )


# ============================================================
# DOWNLOAD DO RECORTE ATUAL
# ============================================================

st.header(
    "7. Download dos dados"
)

st.write(
    """
    O arquivo para download corresponde às notícias
    atualmente apresentadas de acordo com os filtros selecionados.
    """
)


saida = io.StringIO()

campos = [
    "titulo",
    "data_publicacao",
    "texto",
    "url",
    "origem"
]

escritor = csv.DictWriter(
    saida,
    fieldnames=campos
)

escritor.writeheader()

escritor.writerows(
    noticias_filtradas
)

csv_download = saida.getvalue().encode(
    "utf-8-sig"
)


st.download_button(
    label="⬇️ Baixar notícias filtradas em CSV",
    data=csv_download,
    file_name="noticias_amazonia_filtradas.csv",
    mime="text/csv"
)


# ============================================================
# FONTES
# ============================================================

st.header(
    "8. Fontes e método de coleta"
)

st.markdown(
    """
    **Dados de desmatamento:** TerraBrasilis / INPE

    **Notícias:** Agência Brasil / EBC

    **Método de coleta das notícias:** Web scraping com
    Requests + Beautiful Soup.

    **Arquivo processado:** `data/processed/agencia_brasil_meio_ambiente.csv`
    """
)


# ============================================================
# DECLARAÇÃO DE USO DE IA
# ============================================================

st.divider()

st.caption(
    "Desenvolvimento da aplicação: Python + Streamlit. "
    "Ferramenta de IA utilizada na Etapa 4: ChatGPT (OpenAI), "
    "como apoio à geração, explicação e revisão do código."
)

st.caption(
    "Fonte das notícias: Agência Brasil / EBC. "
    "Método de coleta: Web scraping com Beautiful Soup."
)