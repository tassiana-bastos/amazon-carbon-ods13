import os,requests
import streamlit as st
st.title("🔌 API e contribuições")
base=st.text_input("URL base da API",value=os.getenv("API_BASE_URL","http://127.0.0.1:8000")).rstrip("/")
c1,c2=st.columns(2)
with c1:
    if st.button("Consultar desmatamento pela API"):
        try:
            r=requests.get(f"{base}/desmatamento",timeout=8); r.raise_for_status(); data=r.json(); st.success(f"{len(data.get('dados',[]))} registros recebidos"); st.json(data)
        except requests.RequestException as e: st.error(f"API indisponível: {e}. Inicie `uvicorn api.main:app --reload`.")
with c2:
    if st.button("Consultar resumo pela API"):
        try:
            r=requests.get(f"{base}/resumo",timeout=8); r.raise_for_status(); st.json(r.json())
        except requests.RequestException as e: st.error(f"API indisponível: {e}")
st.divider(); st.subheader("Enviar observação ambiental (POST)")
with st.form("observacao"):
    titulo=st.text_input("Título",max_chars=120); texto=st.text_area("Observação",max_chars=2000); fonte=st.text_input("Fonte/URL (opcional)")
    submit=st.form_submit_button("Enviar")
if submit:
    if len(titulo.strip())<3 or len(texto.strip())<5: st.warning("Título (mín. 3 caracteres) e texto (mín. 5) são obrigatórios.")
    else:
        try:
            r=requests.post(f"{base}/observacoes",json={"titulo":titulo.strip(),"texto":texto.strip(),"fonte":fonte.strip() or None},timeout=8); r.raise_for_status(); st.success("Observação registrada."); st.json(r.json())
        except requests.RequestException as e: st.error(f"Falha no POST: {e}")
st.caption("A API local não possui autenticação. Não envie dados pessoais ou confidenciais.")
