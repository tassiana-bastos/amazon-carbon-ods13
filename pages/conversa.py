import os
import requests
import pandas as pd
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT = 35

st.title("💬 Conversa com os dados")
st.caption(
    "Memória conversacional com LLM via OpenRouter. O painel calcula os indicadores; "
    "o modelo interpreta os fatos e mantém o contexto da conversa."
)

def api_error(response):
    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text
    return str(detail)

def criar_conversa():
    response = requests.post(f"{API_BASE_URL}/conversas", timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()["conversation_id"]

def carregar_conversa(conversation_id):
    response = requests.get(f"{API_BASE_URL}/conversas/{conversation_id}", timeout=TIMEOUT)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()

# Session state mantém a experiência durante os reruns do Streamlit.
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = st.query_params.get("conversa", "")

if not st.session_state.conversation_id:
    try:
        st.session_state.conversation_id = criar_conversa()
        st.query_params["conversa"] = st.session_state.conversation_id
    except requests.RequestException as exc:
        st.error(f"Não foi possível iniciar uma conversa. Verifique se a API está online. Detalhe: {exc}")
        st.stop()

try:
    conversation = carregar_conversa(st.session_state.conversation_id)
    if conversation is None:
        st.session_state.conversation_id = criar_conversa()
        st.query_params["conversa"] = st.session_state.conversation_id
        conversation = carregar_conversa(st.session_state.conversation_id)
except requests.RequestException as exc:
    st.error(f"Não foi possível recuperar a conversa da API: {exc}")
    st.info("Inicie a API com `uvicorn api.main:app` e atualize esta página.")
    st.stop()

messages = conversation.get("messages", [])
notes = conversation.get("notas", [])

# Indicadores do conjunto de dados e gráfico complementar ao dashboard existente.
try:
    summary_response = requests.get(f"{API_BASE_URL}/resumo", timeout=TIMEOUT)
    summary_response.raise_for_status()
    summary = summary_response.json()
    col1, col2, col3 = st.columns(3)
    col1.metric("Registros PRODES", f"{summary.get('total_registros', 0):,}".replace(",", "."))
    col2.metric("Estados na base", len(summary.get("estados", [])))
    col3.metric("Período disponível", f"{summary.get('ano_minimo')}–{summary.get('ano_maximo')}")
    latest_year = summary.get("ano_maximo")
    if latest_year:
        latest_response = requests.get(
            f"{API_BASE_URL}/desmatamento",
            params={"ano_inicio": latest_year, "ano_fim": latest_year, "limite": 100},
            timeout=TIMEOUT,
        )
        latest_response.raise_for_status()
        latest_rows = latest_response.json().get("dados", [])
        if latest_rows:
            chart_df = pd.DataFrame(latest_rows).sort_values("area_km2", ascending=False)
            st.markdown(f"**Registros por UF em {latest_year} (km²)**")
            st.bar_chart(chart_df.set_index("uf")["area_km2"])
except (requests.RequestException, ValueError, KeyError) as exc:
    st.warning(f"Não foi possível carregar os indicadores do PRODES: {exc}")

with st.sidebar:
    st.subheader("Memória desta conversa")
    st.caption(f"ID: `{st.session_state.conversation_id}`")
    st.caption(f"Mensagens armazenadas: {len(messages)}")
    st.caption("Memória: notas de entidades extraídas por Python + janela recente de mensagens.")
    if notes:
        st.markdown("**Estados anotados ao longo da conversa**")
        for note in notes:
            st.write(f"• {note}")
    else:
        st.caption("Nenhum estado identificado nas perguntas até agora.")
    st.divider()
    if st.button("🗑️ Apagar conversa", use_container_width=True):
        try:
            deleted = requests.delete(
                f"{API_BASE_URL}/conversas/{st.session_state.conversation_id}",
                timeout=TIMEOUT,
            )
            if deleted.status_code not in (200, 204):
                st.error(api_error(deleted))
            else:
                new_id = criar_conversa()
                st.session_state.conversation_id = new_id
                st.query_params["conversa"] = new_id
                st.rerun()
        except requests.RequestException as exc:
            st.error(f"Não foi possível apagar a conversa: {exc}")

st.markdown(
    "Exemplos: **Qual UF teve o maior valor em 2025?** · "
    "**E no ano anterior?** · **Quanto ela variou?** · "
    "**O que as notícias coletadas dizem sobre terras indígenas?**"
)

for message in messages:
    role = message.get("role", "assistant")
    if role not in ("user", "assistant"):
        continue
    with st.chat_message(role):
        st.markdown(message.get("content", ""))
        saved_sources = message.get("sources", [])
        if saved_sources:
            with st.expander("Fontes jornalísticas desta resposta"):
                for source in saved_sources:
                    st.markdown(
                        f"- [{source.get('titulo')}]({source.get('url')}) "
                        f"({source.get('data_publicacao')})"
                    )

prompt = st.chat_input("Pergunte sobre o desmatamento e o contexto ambiental…")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Consultando os dados e o modelo…"):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/conversas/{st.session_state.conversation_id}/mensagens",
                    json={"mensagem": prompt},
                    timeout=(8, 40),
                )
                if response.status_code >= 400:
                    st.error(api_error(response))
                else:
                    result = response.json()
                    st.markdown(result["resposta"])
                    sources = result.get("fontes_noticias", [])
                    if sources:
                        with st.expander("Notícias recuperadas para esta resposta"):
                            for source in sources:
                                st.markdown(
                                    f"- [{source.get('titulo')}]({source.get('url')}) "
                                    f"({source.get('data_publicacao')})"
                                )
                    st.caption(
                        f"Memória: {result.get('estrategia_memoria')}. "
                        f"O modelo leu {result.get('mensagens_lidas_pelo_modelo')} "
                        f"mensagens recentes; {result.get('total_mensagens')} mensagens estão armazenadas."
                    )
                    st.rerun()
            except requests.Timeout:
                st.error("A solicitação excedeu o tempo limite. Tente novamente.")
            except requests.RequestException as exc:
                st.error(f"Falha ao consultar a API: {exc}")

with st.expander("Como a memória funciona e quais são seus limites"):
    st.markdown(
        """
        - **Session state:** mantém o identificador da conversa durante a navegação no Streamlit.
        - **Persistência na API:** mensagens são gravadas em `data/conversas/` por identificador UUID.
        - **Notas por Python:** os estados citados pelo usuário são extraídos de todo o histórico e preservados mesmo quando mensagens antigas saem da janela.
        - **Janela recente:** o LLM recebe até cinco mensagens recentes, além das notas e dos fatos calculados pelo Python.
        - **Privacidade:** a conversa pode ser apagada pelo botão lateral. Os arquivos de conversas e a chave da API não devem ser enviados ao Git.
        - **Limites:** a extração de notas reconhece nomes/siglas de estados; não é uma memória semântica geral. O LLM é externo e pode estar sujeito a limites, latência e indisponibilidade.
        """
    )
