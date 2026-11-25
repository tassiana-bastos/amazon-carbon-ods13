from __future__ import annotations

import csv
import json
import logging
import os
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

CSV_PATH = ROOT / "data" / "raw" / "terrabrasilis_legal_amazon_23_08_2026_1787514448882.csv"
OBS_PATH = ROOT / "data" / "processed" / "observacoes.jsonl"
NEWS_PATH = ROOT / "data" / "processed" / "agencia_brasil_meio_ambiente.csv"
CONVERSATIONS_DIR = ROOT / "data" / "conversas"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL", "nvidia/nemotron-3.5-lightning:free"
).strip()
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "").strip()
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "Amazonia Legal ODS 13").strip()
MAX_MESSAGE_CHARS = 2000
MAX_HISTORY_MESSAGES = 5  # janela recente; as notas preservam entidades anteriores
MAX_OUTPUT_TOKENS = 1500
PROVIDER_TIMEOUT_SECONDS = 25

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
_FILE_LOCKS: dict[str, threading.RLock] = {}
_LOCKS_GUARD = threading.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="API Amazônia Legal — ODS 13",
    description=(
        "API de consulta ao PRODES/TerraBrasilis, observações e memória "
        "conversacional com LLM via OpenRouter."
    ),
    version="3.0.0",
    lifespan=lifespan,
)


# ----------------------------- Schemas -----------------------------

class ObservationIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    titulo: str = Field(..., min_length=3, max_length=120)
    texto: str = Field(..., min_length=5, max_length=2000)
    fonte: Optional[str] = Field(default=None, max_length=500)


class PedidoAnalise(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    texto: str = Field(..., min_length=15, max_length=4000)


class NovaMensagem(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    mensagem: str = Field(..., min_length=2, max_length=MAX_MESSAGE_CHARS)


# ----------------------------- Data layer -----------------------------

def parse_area(value):
    try:
        return float(str(value).strip().replace(".", "").replace(",", "."))
    except (ValueError, TypeError):
        return None


def rows():
    if not CSV_PATH.exists():
        raise HTTPException(status_code=503, detail="Base PRODES/TerraBrasilis indisponível.")
    output = []
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file, delimiter=";"):
            try:
                year = int(row["year"])
                area = parse_area(row.get("area km²", row.get("area_km2")))
                uf = row["uf"].strip()
                if area is not None and uf:
                    output.append({"year": year, "area_km2": area, "uf": uf})
            except (ValueError, KeyError, AttributeError, TypeError):
                continue
    return output


def formatar_fatos_prodes(anos_relevantes: Optional[set[int]] = None) -> str:
    """Monta fatos compactos a partir dos registros reais; não pede ao LLM para calcular."""
    data = rows()
    if not data:
        return "A base PRODES não contém registros válidos."
    years = sorted({r["year"] for r in data})
    latest = years[-1]
    selected_years = sorted(set(years[-4:]) | (set(anos_relevantes or set()) & set(years)))
    grouped = {}
    for item in data:
        grouped.setdefault((item["year"], item["uf"]), 0.0)
        grouped[(item["year"], item["uf"])] += item["area_km2"]

    lines = [
        f"Base: PRODES/TerraBrasilis; {len(data)} registros; "
        f"{len({r['uf'] for r in data})} UFs; anos disponíveis: {years[0]}–{latest}.",
        "Valores abaixo são os registros por UF e ano, em km²; use-os como fatos, sem extrapolar:",
    ]
    for year in selected_years:
        pairs = sorted(
            [(uf, value) for (y, uf), value in grouped.items() if y == year],
            key=lambda x: x[1], reverse=True
        )
        if pairs:
            lines.append(
                f"{year}: " + "; ".join(f"{uf}={value:.0f}" for uf, value in pairs)
            )
    lines.append(
        "Atenção: os valores são taxas/estimativas anuais do conjunto fornecido; "
        "não representam estoque de carbono nem medição direta de carbono irrecuperável."
    )
    return "\n".join(lines)


def resumo_dados():
    data = rows()
    totals = {}
    for item in data:
        totals[item["uf"]] = totals.get(item["uf"], 0.0) + item["area_km2"]
    return {
        "total_registros": len(data),
        "estados": sorted(totals),
        "ano_minimo": min((r["year"] for r in data), default=None),
        "ano_maximo": max((r["year"] for r in data), default=None),
        "ranking": [
            {"uf": uf, "soma_valores_km2": round(value, 2)}
            for uf, value in sorted(totals.items(), key=lambda item: item[1], reverse=True)
        ],
    }


# ----------------------------- Conversational memory -----------------------------

UF_ALIASES = {
    "acre": "Acre (AC)", "ac": "Acre (AC)",
    "alagoas": "Alagoas (AL)", "al": "Alagoas (AL)",
    "amapa": "Amapá (AP)", "amapá": "Amapá (AP)", "ap": "Amapá (AP)",
    "amazonas": "Amazonas (AM)", "am": "Amazonas (AM)",
    "bahia": "Bahia (BA)", "ba": "Bahia (BA)",
    "ceara": "Ceará (CE)", "ceará": "Ceará (CE)", "ce": "Ceará (CE)",
    "distrito federal": "Distrito Federal (DF)", "df": "Distrito Federal (DF)",
    "espirito santo": "Espírito Santo (ES)", "espírito santo": "Espírito Santo (ES)", "es": "Espírito Santo (ES)",
    "goias": "Goiás (GO)", "goiás": "Goiás (GO)", "go": "Goiás (GO)",
    "maranhao": "Maranhão (MA)", "maranhão": "Maranhão (MA)", "ma": "Maranhão (MA)",
    "mato grosso": "Mato Grosso (MT)", "mt": "Mato Grosso (MT)",
    "mato grosso do sul": "Mato Grosso do Sul (MS)", "ms": "Mato Grosso do Sul (MS)",
    "minas gerais": "Minas Gerais (MG)", "mg": "Minas Gerais (MG)",
    "para": "Pará (PA)", "pará": "Pará (PA)", "pa": "Pará (PA)",
    "paraiba": "Paraíba (PB)", "paraíba": "Paraíba (PB)", "pb": "Paraíba (PB)",
    "parana": "Paraná (PR)", "paraná": "Paraná (PR)", "pr": "Paraná (PR)",
    "pernambuco": "Pernambuco (PE)", "pe": "Pernambuco (PE)",
    "piaui": "Piauí (PI)", "piauí": "Piauí (PI)", "pi": "Piauí (PI)",
    "rio de janeiro": "Rio de Janeiro (RJ)", "rj": "Rio de Janeiro (RJ)",
    "rio grande do norte": "Rio Grande do Norte (RN)", "rn": "Rio Grande do Norte (RN)",
    "rio grande do sul": "Rio Grande do Sul (RS)", "rs": "Rio Grande do Sul (RS)",
    "rondonia": "Rondônia (RO)", "rondônia": "Rondônia (RO)", "ro": "Rondônia (RO)",
    "roraima": "Roraima (RR)", "rr": "Roraima (RR)",
    "santa catarina": "Santa Catarina (SC)", "sc": "Santa Catarina (SC)",
    "sao paulo": "São Paulo (SP)", "são paulo": "São Paulo (SP)", "sp": "São Paulo (SP)",
    "sergipe": "Sergipe (SE)", "se": "Sergipe (SE)",
    "tocantins": "Tocantins (TO)", "to": "Tocantins (TO)",
}
UF_PATTERN = re.compile(
    r"\b(" + "|".join(
        re.escape(k) for k in sorted(UF_ALIASES, key=len, reverse=True)
    ) + r")\b",
    re.IGNORECASE
)


def extrair_notas(messages: list[dict]) -> list[str]:
    """Memória de entidades: Python guarda estados citados ao longo de toda a conversa."""
    seen = []
    for message in messages:
        if message.get("role") != "user":
            continue
        text = message.get("content", "").casefold()
        for match in UF_PATTERN.finditer(text):
            alias = match.group(0).casefold()
            note = UF_ALIASES.get(alias)
            if note and note not in seen:
                seen.append(note)
    return seen


def conversation_path(conversation_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{32}", conversation_id or ""):
        raise HTTPException(status_code=422, detail="Identificador de conversa inválido.")
    return CONVERSATIONS_DIR / f"{conversation_id}.json"


def file_lock(conversation_id: str):
    with _LOCKS_GUARD:
        return _FILE_LOCKS.setdefault(conversation_id, threading.RLock())


def load_conversation(conversation_id: str) -> dict:
    path = conversation_path(conversation_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.exception("Falha ao ler conversa %s", conversation_id)
        raise HTTPException(status_code=500, detail="Não foi possível ler a conversa.") from exc


def save_conversation(conversation_id: str, data: dict):
    path = conversation_path(conversation_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)



def recuperar_noticias(pergunta: str, limite: int = 3) -> list[dict]:
    """Recuperação lexical simples sobre o CSV de notícias coletadas via scraping."""
    if not NEWS_PATH.exists():
        return []
    stopwords = {
        "sobre", "qual", "quais", "como", "para", "porque", "isso", "essa",
        "este", "esta", "anos", "ano", "mais", "menos", "entre", "tambem",
        "também", "desmatamento", "amazonia", "amazônia", "noticia", "notícia",
    }
    terms = {
        term for term in re.findall(r"[^\W\d_]{3,}", pergunta.casefold(), flags=re.UNICODE)
        if term not in stopwords
    }
    if not terms:
        return []
    candidates = []
    try:
        with NEWS_PATH.open("r", encoding="utf-8-sig", newline="") as file:
            sample = file.read(2048)
            file.seek(0)
            delimiter = ";" if sample.splitlines() and sample.splitlines()[0].count(";") > sample.splitlines()[0].count(",") else ","
            for row in csv.DictReader(file, delimiter=delimiter):
                title = row.get("titulo", "")
                body = row.get("texto", "")
                searchable = f"{title} {body}".casefold()
                score = sum(1 for term in terms if term in searchable)
                if score:
                    candidates.append((score, {
                        "titulo": title,
                        "data_publicacao": row.get("data_publicacao", ""),
                        "url": row.get("url", ""),
                        "trecho": re.sub(r"\s+", " ", body).strip()[:900],
                    }))
    except (OSError, csv.Error):
        logger.exception("Não foi possível recuperar notícias.")
        return []
    candidates.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in candidates[:limite]]


def formatar_contexto_noticias(noticias: list[dict]) -> str:
    if not noticias:
        return "Nenhuma notícia do CSV apresentou correspondência lexical suficiente para esta pergunta."
    blocks = []
    for index, item in enumerate(noticias, 1):
        blocks.append(
            f"[{index}] {item['titulo']} ({item['data_publicacao']}). "
            f"Trecho: {item['trecho']} Fonte/URL: {item['url']}"
        )
    return "\n".join(blocks)


def system_prompt(notes: list[str], facts: str, news_context: str) -> str:
    notes_text = ", ".join(notes) if notes else "Nenhum estado foi anotado até agora."
    return f"""Você é o assistente analítico do projeto Amazônia Legal | ODS 13.
Responda em português, com clareza, concisão e rigor. Seu papel é ajudar a interpretar
os dados de desmatamento e o contexto ambiental, não substituir especialistas.

REGRAS OBRIGATÓRIAS:
1. Use somente os fatos quantitativos fornecidos abaixo. Não invente números, estados,
   anos, rankings ou tendências. Se o dado não estiver disponível, diga isso.
2. Para perguntas de acompanhamento (ex.: "e no ano anterior?", "quanto ela caiu?"),
   use o histórico da conversa e as notas de estados para resolver os referentes.
3. Se comparar anos, informe estado, anos, valores e diferença apenas quando todos
   os valores estiverem presentes. Se necessário, peça esclarecimento.
4. Diferencie taxa anual de desmatamento, área acumulada e carbono. A base não mede
   diretamente carbono irrecuperável nem prova causalidade.
5. Quando usar fatos do PRODES, identifique a fonte como PRODES/TerraBrasilis.
6. Para notícias, não afirme conteúdo que não esteja no contexto fornecido.
7. Se a pergunta não puder ser respondida com os dados disponíveis, explique a limitação.

NOTAS EXTRAÍDAS PELO PYTHON (entidades citadas ao longo de toda a conversa):
{notes_text}

FATOS CALCULADOS PELO PYTHON A PARTIR DA BASE PRODES:
{facts}

NOTÍCIAS RECUPERADAS DO CSV DA AGÊNCIA BRASIL (cite título e URL quando usadas):
{news_context}
"""


def call_openrouter(messages: list[dict]) -> str:
    if not OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="OPENROUTER_API_KEY não configurada. Defina a variável no arquivo .env ou no ambiente do servidor."
        )
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "X-Title": OPENROUTER_APP_NAME,
    }
    if OPENROUTER_SITE_URL:
        headers["HTTP-Referer"] = OPENROUTER_SITE_URL
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": MAX_OUTPUT_TOKENS,
    }
    try:
        response = requests.post(
            OPENROUTER_URL, headers=headers, json=payload,
            timeout=(8, PROVIDER_TIMEOUT_SECONDS)
        )
    except requests.Timeout as exc:
        raise HTTPException(status_code=504, detail="Tempo limite da API de IA excedido. Tente novamente.") from exc
    except requests.RequestException as exc:
        logger.warning("Falha de conexão com provedor LLM: %s", exc)
        raise HTTPException(status_code=502, detail="Não foi possível conectar ao provedor de IA.") from exc

    if response.status_code == 429:
        raise HTTPException(status_code=503, detail="O modelo está temporariamente limitado (rate limit). Aguarde alguns instantes e tente novamente.")
    if response.status_code in (401, 403):
        raise HTTPException(status_code=503, detail="A autenticação da API de IA falhou. Verifique OPENROUTER_API_KEY.")
    if response.status_code >= 400:
        logger.warning("OpenRouter HTTP %s: %s", response.status_code, response.text[:500])
        raise HTTPException(status_code=502, detail=f"Provedor de IA retornou HTTP {response.status_code}.")

    try:
        body = response.json()
        content = body["choices"][0]["message"].get("content")
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="Resposta inesperada do provedor de IA.") from exc
    if not isinstance(content, str) or not content.strip():
        raise HTTPException(status_code=502, detail="O modelo retornou resposta vazia. Tente novamente.")
    return content.strip()


# ----------------------------- Existing routes -----------------------------

@app.get("/", tags=["Saúde"])
def root():
    return {"api": "Amazônia Legal — ODS 13", "status": "online", "docs": "/docs"}


@app.get("/saude", tags=["Saúde"])
def health():
    return {
        "api": "Amazônia Legal — ODS 13",
        "status": "online",
        "llm_configurado": bool(OPENROUTER_API_KEY),
        "provedor": "OpenRouter",
        "modelo": OPENROUTER_MODEL,
    }


@app.get("/desmatamento", tags=["Desmatamento"])
def get_deforestation(
    uf: Optional[str] = Query(None, description="Nome do estado, por exemplo Pará"),
    ano_inicio: Optional[int] = Query(None, ge=1980, le=2100),
    ano_fim: Optional[int] = Query(None, ge=1980, le=2100),
    limite: int = Query(5000, ge=1, le=20000),
):
    if ano_inicio is not None and ano_fim is not None and ano_inicio > ano_fim:
        raise HTTPException(status_code=422, detail="ano_inicio não pode superar ano_fim.")
    data = rows()
    if uf:
        data = [r for r in data if r["uf"].casefold() == uf.casefold()]
    if ano_inicio is not None:
        data = [r for r in data if r["year"] >= ano_inicio]
    if ano_fim is not None:
        data = [r for r in data if r["year"] <= ano_fim]
    return {
        "total": len(data),
        "filtros": {"uf": uf, "ano_inicio": ano_inicio, "ano_fim": ano_fim},
        "dados": data[:limite],
    }


@app.get("/resumo", tags=["Desmatamento"])
def get_summary():
    return resumo_dados()


@app.post("/observacoes", status_code=201, tags=["Observações"])
def create_observation(payload: ObservationIn):
    OBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = payload.model_dump()
    record["criado_em"] = datetime.now(timezone.utc).isoformat()
    with OBS_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")
    return {"mensagem": "Observação registrada.", "observacao": record}


# Mantida para compatibilidade com clientes TP4; a classificação agora usa a API remota.
@app.post("/processar_texto", tags=["Inteligência Artificial"])
def processar_texto(pedido: PedidoAnalise):
    prompt = (
        "Classifique o texto ambiental em uma categoria: desmatamento, queimadas, "
        "conservacao, mudancas_climaticas ou outros. Responda somente JSON com a chave categoria.\n"
        f"Texto: {pedido.texto}"
    )
    result = call_openrouter([
        {"role": "system", "content": "Você é um classificador temático ambiental. Não invente fatos."},
        {"role": "user", "content": prompt},
    ])
    match = re.search(r"\b(desmatamento|queimadas|conservacao|mudancas_climaticas|outros)\b", result.casefold())
    category = match.group(1) if match else "outros"
    return {
        "texto_processado": pedido.texto,
        "tipo_analise": "classificacao_tematica",
        "categoria": category,
        "confianca": 0.5,
        "modelo": OPENROUTER_MODEL,
        "aviso": "Classificação indicativa gerada por IA via API; confiança não calibrada.",
    }


# ----------------------------- Conversation routes -----------------------------

@app.post("/conversas", status_code=201, tags=["Memória conversacional"])
def create_conversation():
    conversation_id = uuid.uuid4().hex
    now = datetime.now(timezone.utc).isoformat()
    data = {
        "conversation_id": conversation_id,
        "created_at": now,
        "updated_at": now,
        "messages": [],
    }
    with file_lock(conversation_id):
        save_conversation(conversation_id, data)
    return {"conversation_id": conversation_id, "messages": [], "notas": [], "mensagens_lidas_pelo_modelo": 0}


@app.get("/conversas/{conversation_id}", tags=["Memória conversacional"])
def get_conversation(conversation_id: str):
    with file_lock(conversation_id):
        data = load_conversation(conversation_id)
    messages = data.get("messages", [])
    return {
        "conversation_id": conversation_id,
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
        "messages": messages,
        "notas": extrair_notas(messages),
        "mensagens_lidas_pelo_modelo": min(len(messages), MAX_HISTORY_MESSAGES),
    }


@app.post("/conversas/{conversation_id}/mensagens", tags=["Memória conversacional"])
def send_message(conversation_id: str, payload: NovaMensagem):
    # O lock cobre leitura, chamada ao modelo e gravação para evitar perda de turnos concorrentes.
    with file_lock(conversation_id):
        data = load_conversation(conversation_id)
        history = data.get("messages", [])
        history.append({"role": "user", "content": payload.mensagem})
        notes = extrair_notas(history)
        visible_history = history[-MAX_HISTORY_MESSAGES:]
        question_context = " ".join(
            item["content"] for item in history[-3:] if item.get("role") == "user"
        )
        retrieved_news = recuperar_noticias(question_context)
        mentioned_years = {int(year) for year in re.findall(r"\b(?:19|20)\d{2}\b", question_context)}
        prompt_messages = [
            {"role": "system", "content": system_prompt(
                notes, formatar_fatos_prodes(mentioned_years), formatar_contexto_noticias(retrieved_news)
            )}
        ] + visible_history

        answer = call_openrouter(prompt_messages)
        history.append({
            "role": "assistant", "content": answer,
            "sources": [
                {"titulo": item["titulo"], "data_publicacao": item["data_publicacao"], "url": item["url"]}
                for item in retrieved_news
            ],
        })
        data["messages"] = history
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        save_conversation(conversation_id, data)

    return {
        "conversation_id": conversation_id,
        "resposta": answer,
        "notas": notes,
        "total_mensagens": len(history),
        "mensagens_lidas_pelo_modelo": len(visible_history),
        "estrategia_memoria": "notas_entidades_python + janela_recente_5_mensagens",
        "modelo": OPENROUTER_MODEL,
        "fontes_noticias": [
            {"titulo": item["titulo"], "data_publicacao": item["data_publicacao"], "url": item["url"]}
            for item in retrieved_news
        ],
    }


@app.delete("/conversas/{conversation_id}", status_code=204, tags=["Memória conversacional"])
def delete_conversation(conversation_id: str):
    path = conversation_path(conversation_id)
    with file_lock(conversation_id):
        if not path.exists():
            raise HTTPException(status_code=404, detail="Conversa não encontrada.")
        path.unlink()
    return Response(status_code=204)
