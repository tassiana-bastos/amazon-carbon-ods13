from contextlib import asynccontextmanager
from pathlib import Path
import csv,json, logging, threading, torch
from datetime import datetime,timezone
from typing import Optional, Literal
from fastapi import FastAPI,HTTPException,Query
from pydantic import BaseModel,Field, ConfigDict
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT=Path(__file__).resolve().parents[1]
CSV_PATH=ROOT/"data"/"raw"/"terrabrasilis_legal_amazon_23_08_2026_1787514448882.csv"
OBS_PATH=ROOT/"data"/"processed"/"observacoes.jsonl"

MODEL_DIR = ROOT / "models" / "qwen2.5-1.5b-instruct"
MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
MAX_INPUT_CHARS = 4000
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MOTORES = {}
MODEL_LOCK = threading.Lock()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # O modelo é carregado uma única vez, quando a API inicia.
    try:
        if not MODEL_DIR.exists():
            raise OSError(f"Modelo local não encontrado em {MODEL_DIR}. Execute: python -m src.baixar_modelo")
        tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR), local_files_only=True)
        model = AutoModelForCausalLM.from_pretrained(
            str(MODEL_DIR),
            local_files_only=True,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
        )
        model.eval()
        MOTORES["tokenizer"] = tokenizer
        MOTORES["model"] = model
        logger.info("Modelo %s carregado localmente.", MODEL_ID)
    except Exception as exc:
        # A API continua de pé para que /saude e as demais rotas funcionem.
        logger.exception("Falha ao carregar o modelo local")
        MOTORES.clear()
        MOTORES["erro"] = str(exc)
    yield
    MOTORES.clear()

app=FastAPI(title="API Amazônia Legal — ODS 13",description="Consulta à série PRODES e análise textual local com modelo Hugging Face.",version="2.0.0",lifespan=lifespan)
class ObservationIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    titulo:str=Field(...,min_length=3,max_length=120)
    texto:str=Field(...,min_length=5,max_length=2000)
    fonte:Optional[str]=Field(default=None,max_length=500)

class PedidoAnalise(BaseModel):
    """Entrada validada para análise de texto ambiental."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, 
                              json_schema_extra={"examples": [{"texto": "A fumaça das queimadas atingiu comunidades no sul do Amazonas."}]},
    )
    texto: str = Field(..., min_length=15, max_length=MAX_INPUT_CHARS, description="Texto ambiental a classificar.")

class ResultadoAnalise(BaseModel):
    """Contrato estável da resposta produzida pelo modelo."""
    texto_processado: str
    tipo_analise: Literal["classificacao_tematica"]
    categoria: Literal["desmatamento", "queimadas", "conservacao", "mudancas_climaticas", "outros"]
    confianca: float = Field(ge=0.0, le=1.0)
    modelo: str
    aviso: str

class SaudeResponse(BaseModel):
    api: str
    status: Literal["online"]
    modelo_carregado: bool
    modelo: str

def area(v):
    try:return float(str(v).strip().replace(".","").replace(",","."))
    except (ValueError,TypeError):return None
def rows():
    if not CSV_PATH.exists(): raise HTTPException(status_code=503,detail="Base de desmatamento indisponível.")
    out=[]
    with CSV_PATH.open("r",encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f,delimiter=";"):
            try:
                y=int(r["year"]); a=area(r.get("area km²")); uf=r["uf"].strip()
                if a is not None and uf: out.append({"year":y,"area_km2":a,"uf":uf})
            except (ValueError,KeyError,AttributeError): continue
    return out

def analisar_texto_local(texto: str):
    """Usa Qwen para classificar o tema; não calcula indicadores numéricos."""
    if "model" not in MOTORES or "tokenizer" not in MOTORES:
        raise HTTPException(status_code=503, detail="Modelo LLM local indisponível. Verifique o download e reinicie a API.")

    tokenizer, model = MOTORES["tokenizer"], MOTORES["model"]
    categorias = ["desmatamento", "queimadas", "conservacao", "mudancas_climaticas", "outros"]
    definicoes = {
        "desmatamento": "perda, corte ou remoção da vegetação nativa e da cobertura florestal",
        "queimadas": "fogo, incêndios florestais, focos de calor ou fumaça causada por queimadas",
        "conservacao": "proteção da floresta, restauração, áreas protegidas, biodiversidade ou manejo sustentável",
        "mudancas_climaticas": "aquecimento global, emissões de gases de efeito estufa ou eventos climáticos",
        "outros": "assunto ambiental que não se enquadra claramente nas categorias anteriores",
    }
    prompt = (
        "Classifique o texto ambiental em UMA única categoria. Responda apenas com o nome exato da categoria.\n"
        + "Categorias e definições:\n"
        + "\n".join(f"- {k}: {v}" for k, v in definicoes.items())
        + f"\nTexto: {texto}\nCategoria:"
    )
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    with MODEL_LOCK, torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=12,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    generated = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    normalized = generated.strip().lower().replace(" ", "_").replace("-", "_").strip(".,:;\n")
    category = next((c for c in categorias if normalized.startswith(c)), "outros")

    # Estima confiança por comparação da sequência gerada com os nomes das categorias.
    # É uma pontuação heurística simples, não uma probabilidade calibrada.
    confidence = 0.75 if normalized.startswith(category) and category != "outros" else 0.50
    return category, confidence

@app.get("/",tags=["Saúde"])
def root():
    """Retorna status da API e caminho da documentação."""
    return {"api":"Amazônia Legal — ODS 13","status":"online","docs":"/docs"}

@app.get("/saude", response_model=SaudeResponse, tags=["Saúde"])
def health():
    return SaudeResponse(api="Amazônia Legal — ODS 13", status="online", modelo_carregado="model" in MOTORES, modelo=MODEL_ID)

@app.get("/desmatamento",tags=["Desmatamento"])
def get_deforestation(uf:Optional[str]=Query(None,description="Nome do estado, por exemplo Pará"),
                      ano_inicio:Optional[int]=Query(None,ge=1980,le=2100),ano_fim:Optional[int]=Query(None,ge=1980,le=2100),limite:int=Query(5000,ge=1,le=20000)):
    """Consulta os registros com filtros opcionais de UF e intervalo de anos."""
    if ano_inicio and ano_fim and ano_inicio>ano_fim: 
        raise HTTPException(422,detail="ano_inicio não pode superar ano_fim.")
    data=rows()
    if uf: data=[r for r in data if r["uf"].casefold()==uf.casefold()]
    if ano_inicio is not None: data=[r for r in data if r["year"]>=ano_inicio]
    if ano_fim is not None: data=[r for r in data if r["year"]<=ano_fim]
    return {"total":len(data[:limite]),"filtros":{"uf":uf,"ano_inicio":ano_inicio,"ano_fim":ano_fim},"dados":data[:limite]}

@app.get("/resumo",tags=["Desmatamento"])
def get_summary():
    """Retorna metadados e ranking descritivo agregado por estado."""
    data=rows(); totals={}
    for r in data: totals[r["uf"]]=totals.get(r["uf"],0)+r["area_km2"]
    return {"total_registros":len(data),"estados":sorted(totals),"ano_minimo":min((r["year"] for r in data),default=None),
            "ano_maximo":max((r["year"] for r in data),default=None),"ranking":[{"uf":u,"soma_valores_km2":round(v,2)} for u,v in sorted(totals.items(),key=lambda x:x[1],reverse=True)]}


@app.post("/observacoes",status_code=201,tags=["Observações"])
def create_observation(payload:ObservationIn):
    """Registra uma observação submetida por cliente em JSONL com timestamp UTC."""
    OBS_PATH.parent.mkdir(parents=True,exist_ok=True); record=payload.model_dump(); record["criado_em"]=datetime.now(timezone.utc).isoformat()
    with OBS_PATH.open("a",encoding="utf-8") as f:f.write(json.dumps(record,ensure_ascii=False)+"\n")
    return {"mensagem":"Observação registrada.","observacao":record}

@app.post(
    "/processar_texto",
    response_model=ResultadoAnalise,
    tags=["Inteligência Artificial"],
    summary="Classificar o tema de um texto ambiental com LLM local",
)
def processar_texto(pedido: PedidoAnalise):
    """Recebe um texto validado e retorna classificação temática feita pelo modelo local."""
    try:
        categoria, confianca = analisar_texto_local(pedido.texto)
        return ResultadoAnalise(
            texto_processado=pedido.texto,
            tipo_analise="classificacao_tematica",
            categoria=categoria,
            confianca=confianca,
            modelo=MODEL_ID,
            aviso="Classificação indicativa gerada por IA; confira o texto original antes de tomar decisões.",
        )
    except HTTPException:
        raise
    except (RuntimeError, OSError, ValueError) as exc:
        logger.exception("Erro ao processar texto")
        raise HTTPException(status_code=503, detail="Não foi possível processar o texto com o modelo local.") from exc
    except Exception as exc:
        logger.exception("Erro inesperado na análise")
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno ao processar o texto.") from exc


