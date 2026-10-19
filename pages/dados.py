import io
import pandas as pd
import streamlit as st
from src.data_access import get_deforestation
st.title("📁 Dados e arquivos")
df=pd.DataFrame(get_deforestation())
if not df.empty:
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button("Baixar base de desmatamento",df.to_csv(index=False).encode("utf-8-sig"),"desmatamento_amazonia.csv","text/csv")
else: st.warning("Base quantitativa indisponível.")
st.divider(); st.subheader("Upload validado de notícias CSV")
st.write("Colunas obrigatórias: titulo, data_publicacao, texto, url. O upload fica na sessão e não sobrescreve a base oficial.")
up=st.file_uploader("Selecione CSV",type=["csv"])
if up:
    try:
        raw=up.getvalue(); sample=raw.decode("utf-8-sig"); sep=";" if sample.splitlines()[0].count(";")>sample.splitlines()[0].count(",") else ","
        incoming=pd.read_csv(io.BytesIO(raw),sep=sep,dtype=str).fillna("")
        required={"titulo","data_publicacao","texto","url"}; missing=required-set(incoming.columns)
        if missing: st.error("Colunas ausentes: "+", ".join(sorted(missing)))
        elif incoming.empty: st.warning("O CSV não contém linhas.")
        else:
            incoming["origem"]="enviada"; st.session_state["uploaded_news"]=incoming; st.success(f"{len(incoming)} linha(s) validadas."); st.dataframe(incoming,use_container_width=True,hide_index=True)
    except Exception as e: st.error(f"Falha ao ler CSV: {e}")
if "uploaded_news" in st.session_state:
    st.download_button("Baixar CSV validado",st.session_state["uploaded_news"].to_csv(index=False).encode("utf-8-sig"),"noticias_validadas.csv","text/csv")
st.caption("Cache de leitura: 10 minutos. A chave inclui a data de modificação do arquivo.")
