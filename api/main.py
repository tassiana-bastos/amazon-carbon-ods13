from pathlib import Path
import csv,json
from datetime import datetime,timezone
from typing import Optional
from fastapi import FastAPI,HTTPException,Query
from pydantic import BaseModel,Field
ROOT=Path(__file__).resolve().parents[1]
CSV_PATH=ROOT/"data"/"raw"/"terrabrasilis_legal_amazon_23_08_2026_1787514448882.csv"
OBS_PATH=ROOT/"data"/"processed"/"observacoes.jsonl"
app=FastAPI(title="API Amazônia Legal — ODS 13",description="API acadêmica para consulta de dados PRODES e registro de observações.",version="1.0.0")
class ObservationIn(BaseModel):
    titulo:str=Field(...,min_length=3,max_length=120,description="Título curto.")
    texto:str=Field(...,min_length=5,max_length=2000,description="Texto da observação.")
    fonte:Optional[str]=Field(default=None,max_length=500,description="URL ou referência opcional.")
def area(v):
    try:return float(str(v).strip().replace(".","").replace(",","."))
    except (ValueError,TypeError):return None
def rows():
    if not CSV_PATH.exists(): raise HTTPException(503,detail="Base de desmatamento indisponível.")
    out=[]
    with CSV_PATH.open("r",encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f,delimiter=";"):
            try:
                y=int(r["year"]); a=area(r.get("area km²")); uf=r["uf"].strip()
                if a is not None and uf: out.append({"year":y,"area_km2":a,"uf":uf})
            except (ValueError,KeyError,AttributeError): pass
    return out
@app.get("/",tags=["Saúde"])
def root():
    """Retorna status da API e caminho da documentação."""
    return {"api":"Amazônia Legal — ODS 13","status":"online","docs":"/docs"}
@app.get("/desmatamento",tags=["Desmatamento"])
def get_deforestation(uf:Optional[str]=Query(None,description="Nome do estado, por exemplo Pará"),ano_inicio:Optional[int]=Query(None,ge=1980,le=2100),ano_fim:Optional[int]=Query(None,ge=1980,le=2100),limite:int=Query(5000,ge=1,le=20000)):
    """Consulta os registros com filtros opcionais de UF e intervalo de anos."""
    if ano_inicio and ano_fim and ano_inicio>ano_fim: raise HTTPException(422,detail="ano_inicio não pode superar ano_fim.")
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
    return {"total_registros":len(data),"estados":sorted(totals),"ano_minimo":min((r["year"] for r in data),default=None),"ano_maximo":max((r["year"] for r in data),default=None),"ranking":[{"uf":u,"soma_valores_km2":round(v,2)} for u,v in sorted(totals.items(),key=lambda x:x[1],reverse=True)]}
@app.post("/observacoes",status_code=201,tags=["Observações"])
def create_observation(payload:ObservationIn):
    """Registra uma observação submetida por cliente em JSONL com timestamp UTC."""
    OBS_PATH.parent.mkdir(parents=True,exist_ok=True); record=payload.model_dump(); record["criado_em"]=datetime.now(timezone.utc).isoformat()
    with OBS_PATH.open("a",encoding="utf-8") as f:f.write(json.dumps(record,ensure_ascii=False)+"\n")
    return {"mensagem":"Observação registrada.","observacao":record}
