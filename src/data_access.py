
import os
import csv
from pathlib import Path

import requests
import streamlit as st

# ---------------------------------------------------------
# CONFIGURAÇÃO DA API
# ---------------------------------------------------------

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

NEWS_CSV = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "agencia_brasil_meio_ambiente.csv"
)

# ---------------------------------------------------------
# CONVERSÃO DOS DADOS
# ---------------------------------------------------------

def parse_area(value):
    if isinstance(value, (int, float)):
        return float(value)

    value = str(value or "").strip().replace(",", ".")

    try:
        return float(value)
    except ValueError:
        return None

# ---------------------------------------------------------
# CONSUMO DA API — DESMATAMENTO
# ---------------------------------------------------------

@st.cache_data(ttl=600, show_spinner=False)
def load_deforestation_from_api(base_url):

    response = requests.get(
        f"{base_url}/desmatamento",
        timeout=20
    )

    response.raise_for_status()

    payload = response.json()

    # A API utilizada pela página api_interacao.py
    # retorna os registros dentro da chave "dados".
    if isinstance(payload, dict):
        rows = payload.get("dados", [])
    elif isinstance(payload, list):
        rows = payload
    else:
        raise ValueError("Formato de resposta da API inválido.")

    if not isinstance(rows, list):
        raise ValueError("A chave 'dados' não contém uma lista.")

    normalized_rows = []

    for row in rows:
        try:
            year = int(row["year"])
            area = parse_area(
                row.get("area_km2", row.get("area km²"))
            )
            uf = str(row["uf"]).strip()

            if area is not None and uf:
                normalized_rows.append({
                    "year": year,
                    "area_km2": area,
                    "uf": uf
                })

        except (ValueError, KeyError, TypeError):
            continue

    return normalized_rows

def get_deforestation():

    try:
        return load_deforestation_from_api(API_BASE_URL)

    except requests.RequestException as error:
        st.error(
            f"Não foi possível consultar a API de desmatamento: {error}"
        )
        return []

    except (ValueError, TypeError) as error:
        st.error(f"Erro ao processar os dados da API: {error}")
        return []

# ---------------------------------------------------------
# LEITURA DAS NOTÍCIAS — CSV
# ---------------------------------------------------------

@st.cache_data(ttl=600, show_spinner=False)
def load_news(path_string, modified_ns):

    p = Path(path_string)

    with p.open("r", encoding="utf-8-sig", newline="") as f:

        sample = f.read(2048)
        f.seek(0)

        delim = (
            ";"
            if sample.splitlines()
            and sample.splitlines()[0].count(";")
            > sample.splitlines()[0].count(",")
            else ","
        )

        rows = list(
            csv.DictReader(f, delimiter=delim)
        )

    for row in rows:
        row["origem"] = row.get("origem") or "coletada"

    return rows

def get_news():

    if NEWS_CSV.exists():
        return load_news(
            str(NEWS_CSV),
            NEWS_CSV.stat().st_mtime_ns
        )

    return []
