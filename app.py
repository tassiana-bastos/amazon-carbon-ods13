"""Ponto de entrada da aplicação Amazônia Legal | ODS 13.

A interface de cada seção permanece nos módulos de pages/.
Este arquivo configura a aplicação e registra a navegação multipágina.
"""
import streamlit as st

st.set_page_config(
    page_title="Amazônia Legal | ODS 13",
    page_icon="🌳",
    layout="wide",
)

# Páginas existentes antes do TP5: mantidas.
home = st.Page("pages/inicio.py", title="Visão geral", icon="🌳", default=True)
indicadores = st.Page("pages/indicadores.py", title="Desmatamento", icon="📊")
noticias = st.Page("pages/noticias.py", title="Notícias e contexto", icon="📰")
dados = st.Page("pages/dados.py", title="Dados e arquivos", icon="📁")
api = st.Page("pages/api_interacao.py", title="API e contribuições", icon="🔌")

# Nova funcionalidade exigida pela Opção 1 do TP5.
conversa = st.Page(
    "pages/conversa.py",
    title="Memória conversacional",
    icon="💬",
)

navegacao = st.navigation(
    {
        "Projeto": [home],
        "Explorar": [indicadores, noticias, dados],
        "Inteligência Artificial": [conversa],
        "Integração": [api],
    }
)

st.sidebar.caption("Projeto de Bloco · IA Aplicada · ODS 13")
st.sidebar.markdown(
    "[Repositório GitHub](https://github.com/tassiana-bastos/amazon-carbon-ods13)"
)

navegacao.run()
