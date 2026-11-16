import os
import requests
import streamlit as st

st.title("🤖 Análise de texto com IA local")
st.write("Envie um trecho de notícia ou relato ambiental para classificar seu tema com o modelo executado localmente pela API FastAPI.")
api_url = st.text_input("URL base da API", value=os.getenv("API_BASE_URL", "http://127.0.0.1:8000")).rstrip("/")
texto = st.text_area("Texto ambiental", height=180, max_chars=4000, placeholder="Ex.: Incêndios florestais avançam em áreas de vegetação no Pará...")
if st.button("Analisar texto", type="primary"):
    if len(texto.strip()) < 15:
        st.warning("Informe um texto com pelo menos 15 caracteres.")
    else:
        try:
            with st.spinner("O modelo local está analisando o texto..."):
                response = requests.post(f"{api_url}/processar_texto", json={"texto": texto.strip()}, timeout=120)
            if response.status_code == 422:
                st.error("A API recusou os dados enviados. Verifique o tamanho e o formato do texto.")
                st.json(response.json())
            elif response.status_code == 503:
                st.error("O modelo local não está disponível. Confira se o download foi realizado e reinicie a API.")
                st.caption(response.json().get("detail", "Serviço indisponível."))
            else:
                response.raise_for_status()
                result = response.json()
                st.success("Análise concluída.")
                st.metric("Categoria identificada", result["categoria"].replace("_", " ").title())
                st.write(f"**Tipo de análise:** {result['tipo_analise']}")
                st.write(f"**Confiança indicativa:** {result['confianca']:.0%}")
                st.write(f"**Modelo:** `{result['modelo']}`")
                st.info(result["aviso"])
                with st.expander("Ver resposta JSON da API"):
                    st.json(result)
        except requests.Timeout:
            st.error("A análise excedeu o tempo limite. Tente novamente com um texto menor.")
        except requests.ConnectionError:
            st.error("Não foi possível conectar à API. Inicie `uvicorn api.main:app --reload` em outro terminal.")
        except requests.RequestException as exc:
            st.error(f"Falha ao consultar a API: {exc}")

st.caption("A classificação é executada no ambiente local. Não envie dados pessoais ou confidenciais.")
