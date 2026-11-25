import streamlit as st
from src.data_access import get_deforestation,get_news
st.title("🌳 Amazônia Legal | ODS 13")
st.subheader("Monitoramento do desmatamento e contexto climático")
st.write("Aplicação exploratória que reúne a série histórica PRODES/TerraBrasilis e conteúdo jornalístico sobre Amazônia para apoiar uma leitura orientada por dados.")
rows=get_deforestation(); news=get_news()
if rows:
    years=[r["year"] for r in rows]
    c1,c2,c3=st.columns(3)
    c1.metric("Registros válidos",len(rows)); c2.metric("Estados/territórios",len({r["uf"] for r in rows})); c3.metric("Série disponível",f"{min(years)}–{max(years)}")
else: st.warning("Base de desmatamento não encontrada. Verifique data/raw/.")
st.metric("Notícias processadas",len(news))
st.markdown("Use o menu para explorar indicadores, notícias, arquivos e a API.")

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


# ---------------------------------------------------------
# FONTES, MÉTODO DE COLETA E USO DE IA
# ---------------------------------------------------------

st.divider()
st.header("4. Fontes e método de coleta")

st.markdown(
    """
    **Dados de desmatamento:** TerraBrasilis / INPE

    **Notícias:** Agência Brasil / EBC

    **Método de coleta das notícias:** Web scraping com
    Requests + Beautiful Soup.

    **Arquivo processado:** `data/processed/agencia_brasil_meio_ambiente.csv`
    """
)

st.caption(
    "Desenvolvimento da aplicação: Python + Streamlit. "
    "Ferramentas de IA utilizadas no desenvolvimento: ChatGPT (OpenAI), "
    "como apoio à geração, explicação e revisão do código, e LLM via API "
    "OpenRouter na funcionalidade de memória conversacional."
)
