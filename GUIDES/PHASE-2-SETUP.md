# 📚 Guia Prático: Fase 2 — Ingestão, Processamento e Vetorização Documental

Este documento detalha o passo a passo executado para construir o pipeline de ingestão de documentos, fatiamento de texto (*chunking*) com rastreabilidade de metadados e persistência vetorial no **KnowledgeHub AI**.

## 1. Visão Geral da Fase

Com a infraestrutura e ambiente isolados na Fase 1, o objetivo da Fase 2 foi transformar arquivos PDF corporativos brutos em blocos de texto pesquisáveis (*chunks*), convertê-los em vetores numéricos (embeddings) e persisti-los localmente no banco vetorial.

### Principais Objetivos Técnicos:

* **Extração de Texto Estruturado:** Ler arquivos PDF página a página garantindo a captura correta do conteúdo.
* **Chunking Inteligente:** Dividir o texto em blocos menores com janela deslizante e sobreposição (*overlap*) para evitar quebra de contexto.
* **Rastreabilidade de Metadados:** Associar a cada chunk o nome do arquivo de origem, caminho local, número da página e identificador único.
* **Persistência Vetorial Local:** Gerar embeddings usando um modelo multilíngue e salvar os vetores no **ChromaDB**.

---

## 2. Conceitos & Decisões de Engenharia

### 2.1 Extração com PyMuPDF (`fitz`)
Optou-se pelo PyMuPDF devido à sua velocidade extrema e precisão no mapeamento de páginas. Diferente de leitores que concatenam todo o arquivo em uma única string, o PyMuPDF permite iterar página por página, preservando a numeração exata para fins de citação de evidências no RAG.

### 2.2 Estratégia de Chunking
* **Tamanho do Chunk:** ~500 caracteres.
* **Sobreposição (Overlap):** 50 caracteres.
* **Motivação:** Chunks muito grandes diluem a relevância semântica durante a busca; chunks muito pequenos perdem o contexto da frase. O *overlap* atua como uma margem de segurança nas transições entre blocos.

### 2.3 Modelo de Embeddings e Banco Vetorial
* **Modelo:** `intfloat/multilingual-e5-large` (via `sentence-transformers`).
* **Banco Vetorial:** ChromaDB rodando localmente de forma persistente em `data/chroma_db/`.
* **Motivação:** Desempenho estado da arte para recuperação semântica em textos corporativos em português rodando 100% em CPU local.

---

## 3. Passo a Passo da Implementação

### Passo 3.1: Implementação do Processador de PDFs
Criamos o serviço responsável pela extração por página e fatiamento contextual em `backend/app/services/pdf_processor.py`:

```python
"""
Módulo de Processamento de PDFs e Chunking.
Responsável pela extração de texto estruturado e divisão com rastreabilidade de metadados.
"""

from pathlib import Path
from typing import List, Dict, Any
import fitz  # PyMuPDF


def extract_text_with_metadata(pdf_path: str | Path) -> List[Dict[str, Any]]:
    """
    Lê um arquivo PDF página por página usando PyMuPDF.
    Retorna uma lista de dicionários contendo o texto e os metadados da página.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")

    doc = fitz.open(pdf_path)
    extracted_pages = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        text = page.get_text("text").strip()

        # Descarta páginas totalmente vazias
        if text:
            extracted_pages.append({
                "file_name": pdf_path.name,
                "path": str(pdf_path),
                "page": page_index + 1,  # Numeração humana (inicia em 1)
                "text": text
            })

    doc.close()
    return extracted_pages


def create_chunks(
    extracted_pages: List[Dict[str, Any]], 
    chunk_size: int = 500, 
    overlap: int = 50
) -> List[Dict[str, Any]]:
    """
    Divide o texto extraído das páginas em chunks de tamanho fixo com sobreposição (overlap),
    preservando os metadados de origem de cada trecho.
    """
    all_chunks = []
    chunk_counter = 0

    for page_info in extracted_pages:
        text = page_info["text"]
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk_counter += 1
                all_chunks.append({
                    "chunk_id": f"{page_info['file_name']}_p{page_info['page']}_c{chunk_counter}",
                    "text": chunk_text,
                    "metadata": {
                        "source": page_info["file_name"],
                        "file_path": page_info["path"],
                        "page": page_info["page"],
                        "char_length": len(chunk_text)
                    }
                })

            # Avança a janela mantendo o overlap
            start += (chunk_size - overlap)

    return all_chunks
```

### Passo 3.2: Implementação da Persistência no ChromaDB
Criamos a interface de comunicação com o banco vetorial em `backend/app/vectorstore/chroma_manager.py`:

```python
"""
Gerenciador do Banco Vetorial ChromaDB.
Responsável por carregar o modelo de embeddings local, criar a coleção 
e persistir os chunks com seus metadados de rastreabilidade.
"""

from pathlib import Path
from typing import List, Dict, Any
import chromadb
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
        
        # Inicializa o cliente persistente do ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        
        # Carrega o modelo de embeddings local
        print(f"🔄 Carregando modelo de embeddings '{model_name}'...")
        self.embedding_model = SentenceTransformer(model_name)
        
        # Cria ou obtém a coleção no ChromaDB
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "KnowledgeHub AI Corporate Documents Collection"}
        )
        print(f"✅ Conectado à coleção ChromaDB: '{self.collection_name}'")

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Recebe a lista de chunks gerada pelo pdf_processor, calcula os embeddings
        e os armazena no ChromaDB junto com os metadados de rastreabilidade.
        """
        if not chunks:
            print("⚠️ Nenhum chunk fornecido para adição.")
            return

        ids = [chunk["chunk_id"] for chunk in chunks]
        texts = [chunk["text"] for chunk in chunks]
        metadados = [chunk["metadata"] for chunk in chunks]

        print(f"🔄 Calculando embeddings para {len(texts)} chunks...")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True).tolist()

        # Insere ou atualiza no ChromaDB
        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadados
        )
        print(f"✅ {len(ids)} chunks vetorizados e salvos com sucesso no ChromaDB!")
```

---

## 4. Scripts de Validação e Indexação

### 4.1 Validação do Fatiamento (`scripts/test_pdf_ingestion.py`)
Criamos um script para inspecionar visualmente a extração e fatiamento dos arquivos brutos na pasta `data/pdfs/`:

```python
"""
Script de Validação da Ingestão de PDFs da Fase 2.
Varre a pasta data/pdfs/ e exibe a extração e fatiamento dos arquivos reais.
"""

from pathlib import Path
import sys

# Adiciona a raiz do projeto ao sys.path para importar app.services
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.pdf_processor import extract_text_with_metadata, create_chunks


def main():
    pdf_dir = Path("data/pdfs")
    pdf_files = list(pdf_dir.glob("*.pdf")) + list(pdf_dir.glob("*/*.pdf"))

    print(f"🔍 Encontrados {len(pdf_files)} arquivos PDF na pasta 'data/pdfs/'\n")

    if not pdf_files:
        print("⚠️ Nenhum arquivo PDF encontrado em data/pdfs/. Adicione arquivos para testar.")
        return

    total_chunks = 0

    for pdf_file in pdf_files:
        print(f"📄 Processando: {pdf_file.name}")
        
        # 1. Extração por página
        pages = extract_text_with_metadata(pdf_file)
        print(f"   ├─ Páginas com texto extraídas: {len(pages)}")

        # 2. Geração dos Chunks
        chunks = create_chunks(pages, chunk_size=500, overlap=50)
        total_chunks += len(chunks)
        print(f"   └─ Chunks gerados: {len(chunks)}")

        # Exibe o primeiro chunk como amostra didática
        if chunks:
            sample = chunks[0]
            print(f"\n   📌 Exemplo de Chunk Rastreável [ID: {sample['chunk_id']}]:")
            print(f"   ├─ Fonte: {sample['metadata']['source']} (Pág. {sample['metadata']['page']})")
            print(f"   └─ Trecho: \"{sample['text'][:120]}...\"\n")
            print("-" * 60)

    print(f"✅ Ingestão concluída com sucesso! Total de {total_chunks} chunks prontos para vetorização.")


if __name__ == "__main__":
    main()
```

### 4.2 Script de Indexação Vetorial (`scripts/index_documents.py`)
Script que integra o extrator de PDF ao banco vetorial ChromaDB, realizando a indexação completa:

```python
"""
Script de Indexação de Documentos.
Lê os PDFs da pasta data/pdfs/, fatia em chunks e salva no ChromaDB local.
"""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.pdf_processor import extract_text_with_metadata, create_chunks
from app.vectorstore.chroma_manager import ChromaManager


def main():
    pdf_dir = Path("data/pdfs")
    pdf_files = list(pdf_dir.glob("*.pdf")) + list(pdf_dir.glob("*/*.pdf"))

    if not pdf_files:
        print("⚠️ Nenhum arquivo PDF encontrado em data/pdfs/.")
        return

    print(f"📂 Iniciando pipeline de indexação para {len(pdf_files)} arquivos...")

    all_chunks = []
    for pdf_file in pdf_files:
        pages = extract_text_with_metadata(pdf_file)
        chunks = create_chunks(pages, chunk_size=500, overlap=50)
        all_chunks.extend(chunks)

    print(f"📊 Total de chunks consolidados: {len(all_chunks)}")

    # Inicializa o gerenciador do ChromaDB
    chroma_mgr = ChromaManager()

    # Adiciona os chunks ao banco vetorial
    chroma_mgr.add_chunks(all_chunks)

    print("\n🎉 Indexação da Fase 2 concluída com sucesso! Os documentos estão salvos no ChromaDB.")


if __name__ == "__main__":
    main()
```

---

## 5. Resultados e Métricas Obtidas

Ao executar o comando no terminal com o ambiente virtual ativo:

```powershell
python scripts/index_documents.py
```

Obtivemos o seguinte resultado de execução:

```text
📂 Iniciando pipeline de indexação para 4 arquivos...
📊 Total de chunks consolidados: 30
🔄 Carregando modelo de embeddings 'intfloat/multilingual-e5-large'...
✅ Conectado à coleção ChromaDB: 'knowledgehub_docs'
🔄 Calculando embeddings para 30 chunks...
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:18<00:00, 18.85s/it]
✅ 30 chunks vetorizados e salvos com sucesso no ChromaDB!

🎉 Indexação da Fase 2 concluída com sucesso! Os documentos estão salvos no ChromaDB.
```

### Mapeamento das Métricas:
* **PDFs Processados:** 4 arquivos corporativos da *ABC Indústria*.
* **Chunks Gerados:** 30 trechos fatiados com overlap.
* **Tempo de Cálculo de Embeddings:** ~18.8 segundos em CPU local.
* **Persistência:** Gravados de forma permanente no ChromaDB (`data/chroma_db/`).