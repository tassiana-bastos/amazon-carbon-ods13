import streamlit as st

st.set_page_config(
    page_title="Amazônia Legal | ODS 13",
    page_icon="🌳",
    layout="wide",
)

home = st.Page("pages/inicio.py", title="Visão geral", icon="🌳", default=True)
indicadores = st.Page("pages/indicadores.py", title="Desmatamento", icon="📊")
noticias = st.Page("pages/noticias.py", title="Notícias e contexto", icon="📰")
dados = st.Page("pages/dados.py", title="Dados e arquivos", icon="📁")
api = st.Page("pages/api_interacao.py", title="API e contribuições", icon="🔌")

navegacao = st.navigation({
    "Projeto": [home],
    "Explorar": [indicadores, noticias, dados],
    "Integração": [api],
})

st.sidebar.caption("Projeto de Bloco · IA Aplicada · ODS 13")
st.sidebar.markdown(
    "[Repositório GitHub](https://github.com/tassiana-bastos/amazon-carbon-ods13)"
)

navegacao.run()
