"""
Script de Validação do Pipeline RAG Completo (Fase 4).
Realiza a busca semântica dos trechos mais relevantes e gera a resposta fundamentada via DeepSeek.
"""

from pathlib import Path
import os
import sys
from dotenv import load_dotenv

# Carrega o .env explicitamente na raiz do projeto
load_dotenv()

# Adiciona a pasta backend ao path para importações dos módulos
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.vectorstore.chroma_manager import ChromaManager
from app.services.llm_service import GeminiService


def main():
    query = "Quero saber sobre classificação de fornecedores  e requisitos de homologação?"

    print("🔄 Inicializando o banco vetorial ChromaDB...")
    chroma_mgr = ChromaManager()

    # Recupera a chave explicitamente para validação
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Erro: OPENROUTER_API_KEY não encontrada pelo script de teste!")
        return

    print("🔄 Conectando ao serviço LLM (DeepSeek via OpenRouter)...")
    gemini_svc = GeminiService(api_key=api_key)

    print(f"\n🔍 Buscando contexto relevante para a pergunta:\n   ➡️ \"{query}\"")
    results = chroma_mgr.query_similarity(query, n_results=3)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    context_chunks = []
    for doc, meta in zip(documents, metadatas):
        context_chunks.append({
            "text": doc,
            "metadata": meta
        })

    print(f"✅ {len(context_chunks)} chunks recuperados com sucesso.")
    print("\n🤖 Enviando contexto e pergunta a LLM...\n")
    print("=" * 70)

    answer = gemini_svc.generate_answer(query, context_chunks)

    print("💬 RESPOSTA DO KNOWLEDGEHUB AI:\n")
    print(answer)
    print("=" * 70)


if __name__ == "__main__":
    main()