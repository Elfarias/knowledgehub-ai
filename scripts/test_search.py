"""
Script de Teste de Recuperação (Retrieval) da Fase 3.
Permite realizar buscas semânticas no ChromaDB e validar a rastreabilidade dos chunks.
"""

from pathlib import Path
import sys

# Adiciona o diretório backend ao path para permitir imports
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.vectorstore.chroma_manager import ChromaManager


def main():
    print("🔄 Inicializando conexão com o ChromaDB para testes de busca...")
    chroma_mgr = ChromaManager()

    # Pergunta de teste relacionada aos documentos corporativos da ABC Indústria
    # (Você pode alterar esta query para testar outros tópicos presentes nos seus PDFs)
    query_text = "Quais são as diretrizes de segurança da informação?"
    
    print(f"\n🔍 Realizando busca semântica para a query:\n   ➡️ \"{query_text}\"\n")

    # Executa a busca retornando os 3 chunks mais relevantes
    results = chroma_mgr.query_similarity(query_text, n_results=3)

    # Processa e exibe os resultados formatados
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        print("⚠️ Nenhum resultado encontrado para a busca.")
        return

    print(f"📊 {len(documents)} resultados mais relevantes encontrados:\n")
    print("=" * 70)

    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), start=1):
        print(f"[{i}] Relevância/Distância: {dist:.4f}")
        print(f"    📄 Fonte: {meta.get('source')}")
        print(f"    📖 Página: {meta.get('page')}")
        print(f"    🆔 Chunk ID: {meta.get('file_path', 'N/A')}")
        print(f"    💬 Trecho recuperado:")
        print(f"    \"{doc}\"")
        print("-" * 70)


if __name__ == "__main__":
    main()