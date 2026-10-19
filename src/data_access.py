from pathlib import Path
import csv
import streamlit as st
ROOT=Path(__file__).resolve().parents[1]
DEFORESTATION_CSV=ROOT/"data"/"raw"/"terrabrasilis_legal_amazon_23_08_2026_1787514448882.csv"
NEWS_CSV=ROOT/"data"/"processed"/"agencia_brasil_meio_ambiente.csv"
def parse_area(value):
    value=str(value or "").strip().replace(".","").replace(",",".")
    try: return float(value)
    except ValueError: return None
@st.cache_data(ttl=600,show_spinner=False)
def load_deforestation(path_string,modified_ns):
    rows=[]
    with Path(path_string).open("r",encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f,delimiter=";"):
            try:
                area=parse_area(r.get("area km²")); year=int(r["year"]); uf=r["uf"].strip()
                if area is not None and uf: rows.append({"year":year,"area_km2":area,"uf":uf})
            except (ValueError,KeyError,AttributeError): pass
    return rows
def get_deforestation():
    return load_deforestation(str(DEFORESTATION_CSV),DEFORESTATION_CSV.stat().st_mtime_ns) if DEFORESTATION_CSV.exists() else []
@st.cache_data(ttl=600,show_spinner=False)
def load_news(path_string,modified_ns):
    p=Path(path_string)
    with p.open("r",encoding="utf-8-sig",newline="") as f:
        sample=f.read(2048); f.seek(0)
        delim=";" if sample.splitlines() and sample.splitlines()[0].count(";")>sample.splitlines()[0].count(",") else ","
        rows=list(csv.DictReader(f,delimiter=delim))
    for r in rows: r["origem"]=r.get("origem") or "coletada"
    return rows
def get_news():
    return load_news(str(NEWS_CSV),NEWS_CSV.stat().st_mtime_ns) if NEWS_CSV.exists() else []
