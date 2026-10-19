import streamlit as st
from src.data_access import get_deforestation, get_news

st.title("🌳 Amazônia Legal | ODS 13")
st.subheader("Monitoramento do desmatamento e contexto climático")
st.write(
    "Aplicação exploratória que reúne a série histórica PRODES/TerraBrasilis "
    "e conteúdo jornalístico sobre Amazônia para apoiar uma leitura orientada por dados."
)

st.header("1. Problema de negócio")
st.write(
    "O desmatamento na Amazônia Legal representa um desafio para a conservação "
    "dos ecossistemas e para o enfrentamento das mudanças climáticas. Este projeto "
    "utiliza dados de desmatamento para apoiar a identificação dos territórios que "
    "apresentam maior necessidade de atenção e monitoramento, contribuindo para "
    "uma tomada de decisão orientada por dados."
)

st.header("2. Objetivos do projeto")
st.markdown(
    "- Organizar dados históricos de desmatamento da Amazônia Legal.\n"
    "- Permitir a visualização dos dados por território e ano.\n"
    "- Identificar diferenças na área desmatada entre os territórios.\n"
    "- Apoiar o monitoramento de áreas que merecem maior atenção.\n"
    "- Incorporar informações externas relacionadas ao tema.\n"
    "- Contribuir para discussões relacionadas às mudanças climáticas e ao ODS 13."
)

st.header("3. Tipo da pergunta")
st.info(
    "A aplicação possui caráter predominantemente descritivo: apresenta o comportamento "
    "do desmatamento ao longo do período disponível e complementa a análise com "
    "informações jornalísticas relacionadas ao meio ambiente e à Amazônia."
)

st.header("4. Visão geral dos dados")
rows = get_deforestation()
news = get_news()
if rows:
    years = [int(r["year"]) for r in rows if str(r.get("year", "")).strip()]
    c1, c2, c3 = st.columns(3)
    c1.metric("Registros válidos", len(rows))
    c2.metric("Estados/territórios", len({r.get("uf") for r in rows if r.get("uf")}))
    c3.metric("Série disponível", f"{min(years)}–{max(years)}" if years else "Indisponível")
else:
    st.warning("Base de desmatamento não encontrada. Verifique data/raw/.")
st.metric("Notícias processadas", len(news))
st.markdown("Use o menu para explorar indicadores, notícias, arquivos e a API.")

st.divider()
st.header("Fontes e método")
st.markdown(
    "**Dados de desmatamento:** TerraBrasilis / INPE  \n"
    "**Notícias:** Agência Brasil / EBC  \n"
    "**Método de coleta:** Requests + Beautiful Soup, com armazenamento prévio em CSV."
)
st.caption(
    "Desenvolvimento: Python + Streamlit. Ferramenta de IA utilizada na Etapa 4: "
    "ChatGPT (OpenAI), como apoio à geração, explicação e revisão do código."
)
