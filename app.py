import csv
from pathlib import Path

import streamlit as st


# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------

st.set_page_config(
    page_title="Amazônia Legal | ODS 13",
    page_icon="🌳",
    layout="wide"
)


# ---------------------------------------------------------
# CAMINHO DO ARQUIVO
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "terrabrasilis_legal_amazon_23_08_2026_1787514448882.csv"
)


# ---------------------------------------------------------
# FUNÇÃO PARA LER O CSV
# ---------------------------------------------------------

def carregar_dados(caminho):
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


# ---------------------------------------------------------
# CARREGAMENTO DOS DADOS
# ---------------------------------------------------------

try:
    dados = carregar_dados(CSV_PATH)

except FileNotFoundError:
    st.error(
        "Não foi possível encontrar o arquivo CSV. "
        "Verifique se ele está dentro de data/raw/."
    )
    st.stop()


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
    Nesta primeira versão, a aplicação possui caráter descritivo:
    busca mostrar o que aconteceu com o desmatamento ao longo do
    período disponível nos dados.

    As análises preditivas e funcionalidades mais avançadas serão
    desenvolvidas nas próximas etapas do projeto.
    """
)


# ---------------------------------------------------------
# INDICADORES INICIAIS
# ---------------------------------------------------------

st.header("4. Dados disponíveis")

anos = sorted(
    {
        int(linha["year"])
        for linha in dados
        if linha["year"]
    }
)

ufs = sorted(
    {
        linha["uf"]
        for linha in dados
        if linha["uf"]
    }
)

coluna_area = "area km²"

areas = []

for linha in dados:
    valor = linha[coluna_area]

    if valor:
        valor = valor.replace(".", "").replace(",", ".")

        try:
            areas.append(float(valor))
        except ValueError:
            pass


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Registros",
        len(dados)
    )

with col2:
    st.metric(
        "Territórios",
        len(ufs)
    )

with col3:
    st.metric(
        "Período",
        f"{min(anos)}–{max(anos)}"
    )


# ---------------------------------------------------------
# LINKS ÚTEIS
# ---------------------------------------------------------

st.header("5. Links úteis e fontes de inspiração")

st.markdown(
    """
    - [IBGE — Instituto Brasileiro de Geografia e Estatística](https://www.ibge.gov.br/)
    - [TerraBrasilis - PRODES (Desmatamento)](https://terrabrasilis.dpi.inpe.br/app/map/deforestation)
    - [What is Irrecoverable Carbon? — World Economic Forum](https://www.weforum.org/stories/climate-action/what-is-irrecoverable-carbon/)
    - [Conecta Brasil - ODS](https://conectabrasil.org/ods)
    """
)


# ---------------------------------------------------------
# AMOSTRA DOS DADOS
# ---------------------------------------------------------

st.header("6. Amostra dos dados")

st.write(
    "Abaixo são apresentados os primeiros registros do arquivo "
    "utilizado nesta versão inicial da aplicação."
)

# Mostra somente uma amostra para não carregar todos os registros.
amostra = dados[:10]

st.dataframe(
    amostra,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# INFORMAÇÕES SOBRE A FONTE
# ---------------------------------------------------------

st.header("7. Sobre os dados")

st.markdown(
    """
    **Fonte utilizada nesta versão:** dados de desmatamento da
    Amazônia Legal disponibilizados no arquivo CSV utilizado pelo
    projeto.

    **Tipo de dado:** estruturado.

    **Formato:** CSV, organizado em linhas e colunas.

    **Principais campos utilizados:**

    - `year` — ano do registro.
    - `area km²` — área de desmatamento em km².
    - `uf` — unidade federativa.
    """
)


# ---------------------------------------------------------
# DECLARAÇÃO DE USO DE IA
# ---------------------------------------------------------

st.divider()

st.caption(
    "Desenvolvimento da aplicação: Python + Streamlit. "
    "Ferramenta de IA utilizada na Etapa 4: ChatGPT (OpenAI), "
    "como apoio à geração, explicação e revisão do código."
)
