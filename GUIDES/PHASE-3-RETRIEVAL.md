# Guia Prático: Fase 3 — Motor de Recuperação e Consulta (Retrieval)

Este documento detalha o passo a passo executado para construir e validar o mecanismo de busca semântica por similaridade de vetores no **KnowledgeHub AI**.

## 1. Visão Geral da Fase

Após vetorizar e armazenar os chunks dos PDFs corporativos no **ChromaDB** durante a Fase 2, o objetivo da Fase 3 foi criar a camada de consulta (**Retrieval**). Esta camada converte perguntas em linguagem natural em vetores e recupera os trechos de documento estatisticamente mais relevantes, preservando a rastreabilidade (fontes e números de páginas).

### Principais Objetivos Técnicos:

* **Busca Semântica por Similaridade:** Realizar a busca utilizando a distância de cosseno entre o vetor da consulta e os vetores armazenados.
* **Preservação de Evidências:** Retornar não apenas o texto do chunk, mas os metadados associados (`source`, `page`, `file_path`).
* **Tratamento de Telemetria:** Configurar a inicialização do banco vetorial para evitar ruídos e logs desnecessários durante a execução local.

## 2. Conceitos & Decisões de Engenharia

### 2.1 Prefixo de Consulta para Modelos e5

O modelo `intfloat/multilingual-e5-large` utiliza uma arquitetura asimétrica para tarefas de recuperação semântica:
* **Passagens (Indexação):** Recomenda-se o prefixo `passage: ` (ou o texto bruto em tarefas diretas).
* **Consultas (Retrieval):** É fundamental incluir o prefixo `query: ` antes de calcular o embedding da pergunta do usuário. Isso ajusta o espaço vetorial para otimizar a correspondência entre perguntas e respostas/contextos.

### 2.2 Desativação de Telemetria no ChromaDB

Durante a execução em ambiente de desenvolvimento local, o cliente do ChromaDB tenta enviar eventos de telemetria anônimos que podem gerar *warnings* no terminal em determinadas versões. Para manter a execução limpa e determinística, a telemetria é desativada explicitamente via `Settings`:

```python
from chromadb.config import Settings

self.client = chromadb.PersistentClient(
path=str(self.persist_directory),
settings=Settings(anonymized_telemetry=False)
)
```

## 3. Código do Gerenciador de Busca (`backend/app/vectorstore/chroma_manager.py`)

Abaixo está o código atualizado do módulo gerenciador com o método `query_similarity`:

```python
"""
Gerenciador do Banco Vetorial ChromaDB.
Responsável por carregar o modelo de embeddings local, criar a coleção
e persistir os chunks com seus metadados de rastreabilidade.
"""

from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class ChromaManager:
def __init__(
self,
persist_directory: str = "data/chroma_db",
collection_name: str = "knowledgehub_docs",
model_name: str = "intfloat/multilingual-e5-large"
):
self.persist_directory = Path(persist_directory)
self.collection_name = collection_name

# Inicializa o cliente persistente desativando telemetria anônima
self.client = chromadb.PersistentClient(
path=str(self.persist_directory),
settings=Settings(anonymized_telemetry=False)
)

# Carrega o modelo de embeddings local (CPU)
print(f"🔄 Carregando modelo de embeddings '{model_name}'...")
self.embedding_model = SentenceTransformer(model_name)

# Obtém ou cria a coleção
self.collection = self.client.get_or_create_collection(
name=self.collection_name,
metadata={"description": "KnowledgeHub AI Corporate Documents Collection"}
)
print(f"✅ Conectado à coleção ChromaDB: '{self.collection_name}'")

def query_similarity(self, query_text: str, n_results: int = 3) -> Dict[str, Any]:
"""
Realiza uma busca semântica por similaridade no banco vetorial,
retornando os trechos mais relevantes e suas evidências (metadados).
"""
# Aplicação do prefixo 'query:' conforme boas práticas do modelo e5
query_embedding = self.embedding_model.encode([f"query: {query_text}"]).tolist()

results = self.collection.query(
query_embeddings=query_embedding,
n_results=n_results
)
return results
```

## 4. Script de Teste da Recuperação (`scripts/test_search.py`)

Script utilitário criado para validar a execução das consultas diretamente via linha de comando:

```python
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

query_text = "Quais são as diretrizes de segurança da informação?"

print(f"\n🔍 Realizando busca semântica para a query:\n ➡️ \"{query_text}\"\n")

results = chroma_mgr.query_similarity(query_text, n_results=3)

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
print(f" 📄 Fonte: {meta.get('source')}")
print(f" 📖 Página: {meta.get('page')}")
print(f" 🆔 Chunk ID: {meta.get('file_path', 'N/A')}")
print(f" 💬 Trecho recuperado:")
print(f" \"{doc}\"")
print("-" * 70)

if __name__ == "__main__":
main()
```

## 5. Resultados de Validação

Ao executar `python scripts/test_search.py` no terminal com o ambiente virtual ativo (`venv`), o sistema apresentou os seguintes trechos recuperados para a consulta *"Quais são as diretrizes de segurança da informação?"*:

* **Resultado 1 (Distância: 0.3292):** Documento `TI-004 - Uso Aceitável de Recursos.pdf`, Página 1. Retornou regras relativas ao uso de mídias removíveis (pen drives) e rede Wi-Fi de visitantes.
* **Resultado 2 (Distância: 0.3311):** Documento `TI-004 - Uso Aceitável de Recursos.pdf`, Página 1. Retornou o cabeçalho e os objetivos gerais das diretrizes de segurança de TI.
* **Resultado 3 (Distância: 0.3378):** Documento `RH-002 - Política de Home Office.pdf`, Página 2. Retornou os requisitos de uso de VPN, 2FA e privacidade em ambiente de trabalho remoto.

### Conclusão:
A busca por similaridade de cosseno demonstrou alta precisão semântica ao relacionar a pergunta a dois documentos distintos (`TI-004` e `RH-002`), com distâncias numéricas consistentes e rastreabilidade garantida.
