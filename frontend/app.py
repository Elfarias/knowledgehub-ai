"""
Interface Web em Streamlit para o KnowledgeHub AI.
Conecta-se ao serviço FastAPI na porta 8000 para consulta RAG e exibição de fontes.
"""

import os
import streamlit as st
import requests

# Configuração visual e título da aplicação
st.set_page_config(
    page_title="KnowledgeHub AI",
    page_icon="🧠",
    layout="wide"
)

# URL base da API FastAPI (permite customização por variável de ambiente em containers/deploy)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

st.title("🧠 KnowledgeHub AI — Assistente Corporativo")
st.caption("Consulte a base de conhecimento interna com respostas fundamentadas em evidências documentais.")

# --- BARRA LATERAL: Status da API e Parâmetros ---
with st.sidebar:
    st.header("⚙️ Status & Configurações")
    
    # Validação do Health Check da API FastAPI
    try:
        health_resp = requests.get(f"{API_BASE_URL}/health", timeout=3)
        if health_resp.status_code == 200:
            health_data = health_resp.json()
            st.success("🟢 API Conectada")
            st.metric(label="Documentos Indexados", value=health_data.get("documents_indexed", 0))
            st.info(f"**Provedor LLM:**\n{health_data.get('llm_provider', 'N/A')}")
        else:
            st.error("🔴 API com Instabilidade")
    except Exception:
        st.error("🔴 API Offline\n\nCertifique-se de que o Uvicorn está rodando na porta 8000.")

    st.divider()
    
    # Parâmetro Top-K para controle de recuperação
    top_k = st.slider(
        "Quantidade de fontes a recuperar (Top-K):",
        min_value=1,
        max_value=10,
        value=3,
        help="Quantidade de trechos (chunks) que o ChromaDB buscará para montar o contexto do LLM."
    )

# --- HISTÓRICO DE CHAT DA SESSÃO ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe o histórico de mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📚 Fontes Consultadas"):
                for idx, src in enumerate(message["sources"], 1):
                    st.write(f"**{idx}.** Documento: `{src.get('source')}` | Página: `{src.get('page')}`")

# --- ENTRADA DA PERGUNTA DO USUÁRIO ---
if prompt := st.chat_input("Faça uma pergunta sobre as políticas corporativas..."):
    # 1. Registra e exibe a pergunta do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Chama a API RAG FastAPI e exibe a resposta
    with st.chat_message("assistant"):
        with st.spinner("Buscando no banco vetorial e sintetizando a resposta..."):
            try:
                payload = {"query": prompt, "top_k": top_k}
                response = requests.post(f"{API_BASE_URL}/api/v1/query", json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "Sem resposta do servidor.")
                    sources = data.get("sources", [])
                    
                    st.markdown(answer)
                    
                    if sources:
                        with st.expander("📚 Fontes Consultadas"):
                            for idx, src in enumerate(sources, 1):
                                st.write(f"**{idx}.** Documento: `{src.get('source')}` | Página: `{src.get('page')}`")
                    
                    # Salva a resposta no histórico da sessão
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                else:
                    st.error(f"Não foi possível processar a resposta da API (Código {response.status_code}).")
            
            except requests.exceptions.ConnectionError:
                st.error(f"Não foi possível conectar à API. Verifique se o servidor FastAPI está em execução em {API_BASE_URL}.")
            except requests.exceptions.Timeout:
                st.error("O processamento da consulta excedeu o tempo limite. Tente novamente em instantes.")
            except Exception:
                st.error("Ocorreu uma falha inesperada durante a comunicação. Por favor, tente novamente.")