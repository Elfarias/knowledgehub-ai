import os
import chromadb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(name="knowledgehub_docs")

# Recupera todos os metadados cadastrados
results = collection.get(include=["metadatas"])
metadatas = results.get("metadatas", [])

# Extrai os nomes de arquivos únicos (campo "source")
documentos_ingestados = sorted(list(set(m.get("source") for m in metadatas if m)))

print(f"Total de chunks no ChromaDB: {collection.count()}")
print(f"Total de documentos únicos: {len(documentos_ingestados)}\n")
print("📄 Documentos já ingestados:")
for doc in documentos_ingestados:
    print(f"  - {doc}")