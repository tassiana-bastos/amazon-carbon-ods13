import pandas as pd
import streamlit as st
from src.data_access import get_deforestation
st.title("📊 Desmatamento por estado e ano")
df=pd.DataFrame(get_deforestation())
if df.empty: st.error("Base indisponível em data/raw/."); st.stop()
states=sorted(df.uf.unique()); years=sorted(df.year.unique())
c1,c2=st.columns(2)
with c1: selected=st.multiselect("Estados",states,default=states)
with c2: start,end=st.select_slider("Intervalo de anos",options=years,value=(min(years),max(years)))
f=df[df.uf.isin(selected)&df.year.between(start,end)]
if f.empty: st.warning("Nenhum registro corresponde aos filtros."); st.stop()
c1,c2,c3=st.columns(3); c1.metric("Registros",len(f)); c2.metric("Soma dos valores (km²)",f"{f.area_km2.sum():,.2f}"); c3.metric("Estados",f.uf.nunique())
st.subheader("Série temporal"); st.line_chart(f.pivot_table(index="year",columns="uf",values="area_km2",aggfunc="sum").sort_index())
st.subheader("Ranking descritivo"); ranking=f.groupby("uf",as_index=False).area_km2.sum().sort_values("area_km2",ascending=False); st.bar_chart(ranking.set_index("uf"))
st.dataframe(f.sort_values(["year","uf"]),use_container_width=True,hide_index=True)
st.caption("A soma de valores anuais é um agregado comparativo, não uma área geográfica única acumulada.")
