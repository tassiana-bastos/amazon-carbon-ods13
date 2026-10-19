import re
from collections import Counter
import io
import pandas as pd
import streamlit as st
from src.data_access import get_news

st.title("📰 Notícias e contexto")
st.write(
    "A coleta fica separada da interface. Esta página lê o CSV processado; "
    "não executa scraping a cada interação."
)

news = get_news()
# Notícias adicionadas por upload ficam na sessão e são incorporadas à visualização.
uploaded = st.session_state.get("uploaded_news")
if uploaded is not None and not uploaded.empty:
    news = list(news) + uploaded.to_dict(orient="records")

if not news:
    st.info(
        "Ainda não há data/processed/agencia_brasil_meio_ambiente.csv. "
        "Execute `python coleta_web.py` se a fonte estiver acessível e a coleta for permitida."
    )
    st.markdown(
        "Fontes previstas: matérias da Agência Brasil sobre Amazônia e meio ambiente. "
        "Consulte robots.txt e os termos da fonte."
    )
    st.stop()

df = pd.DataFrame(news)
for col in ["titulo", "data_publicacao", "texto", "url", "origem"]:
    if col not in df:
        df[col] = ""
df["origem"] = df["origem"].fillna("coletada").replace("", "coletada")
# Evita duplicações quando uma URL aparece tanto na base como no upload.
df = df.drop_duplicates(subset=["url"], keep="first")

term = st.text_input("Buscar no título e no texto")
origens = ["Todas"] + sorted(df.origem.astype(str).unique())
origem = st.selectbox("Origem", origens)
if origem != "Todas":
    df = df[df.origem == origem]
if term:
    df = df[
        df.titulo.fillna("").str.contains(term, case=False, regex=False)
        | df.texto.fillna("").str.contains(term, case=False, regex=False)
    ]

c1, c2, c3 = st.columns(3)
c1.metric("Notícias", len(df))
c2.metric("Palavras", sum(len(str(x).split()) for x in df.texto))
c3.metric("Caracteres", sum(len(str(x)) for x in df.texto))
st.dataframe(
    df[["titulo", "data_publicacao", "origem", "url"]],
    use_container_width=True,
    hide_index=True,
)
for _, r in df.iterrows():
    with st.expander(str(r.titulo or "Notícia sem título")):
        st.caption(f"{r.data_publicacao} · {r.origem}")
        st.write(str(r.texto)[:2500])
        if r.url:
            st.markdown(f"[Abrir fonte original]({r.url})")

st.subheader("Nuvem de palavras das notícias filtradas")
stop = set(
    "para com uma que dos das por como mais sobre entre sua seus seu suas não foi são "
    "após desde até pela pelo pelas pelos esse esta este isso também quando onde porque".split()
)
words = re.findall(
    r"\b[a-záàâãéêíóôõúç]{3,}\b",
    " ".join(df.texto.fillna("").astype(str)).lower(),
)
freq = Counter(word for word in words if word not in stop)
if freq:
    try:
        from wordcloud import WordCloud
        cloud = WordCloud(
            width=1200, height=500, background_color="white", max_words=100
        ).generate_from_frequencies(freq)
        st.image(cloud.to_array(), use_container_width=True)
    except ImportError:
        st.info("Instale a biblioteca `wordcloud` para gerar a nuvem de palavras.")
    st.subheader("Palavras mais frequentes")
    st.bar_chart(
        pd.DataFrame(freq.most_common(20), columns=["palavra", "frequência"])
        .set_index("palavra")
    )
else:
    st.info("Não existem textos suficientes para gerar a nuvem de palavras.")

st.subheader("Download do recorte atual")
csv_download = df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "⬇️ Baixar notícias filtradas em CSV",
    data=csv_download,
    file_name="noticias_amazonia_filtradas.csv",
    mime="text/csv",
)
