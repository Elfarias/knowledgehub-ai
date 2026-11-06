"""
Script de Ingestão de Documentos do KnowledgeHub AI.
Lê os PDFs em backend/data/docs utilizando pypdf, realiza limpeza de texto,
gera chunks estruturados com rastreabilidade, calcula embeddings com multilingual-e5-large
e persiste os vetores no ChromaDB com caminho absoluto alinhado à API.
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Configuração de logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("IngestionPipeline")

# Definição estrita dos caminhos absolutos relativos a __file__
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Aponta para backend/
DOCS_DIR = os.path.join(BASE_DIR, "data", "docs")
CHROMA_DIR = os.path.join(BASE_DIR, "data", "chroma_db")
COLLECTION_NAME = "knowledgehub_docs"
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"


def clean_text(text: str) -> str:
    """Remove quebras de linha excessivas, caracteres espúrios e normaliza espaços."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_pages_from_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    """Extrai texto e metadados de cada página do PDF utilizando pypdf.PdfReader."""
    extracted_pages = []
    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)

    for idx, page in enumerate(reader.pages):
        raw_text = page.extract_text() or ""
        cleaned = clean_text(raw_text)
        if cleaned:
            extracted_pages.append({
                "file_name": pdf_path.name,
                "file_path": str(pdf_path.resolve()),
                "page": idx + 1,
                "total_pages": total_pages,
                "text": cleaned
            })

    return extracted_pages


def create_chunks(
    pages: List[Dict[str, Any]],
    chunk_size: int = 500,
    overlap: int = 50
) -> List[Dict[str, Any]]:
    """Fatia o texto de cada página em blocos menores com sobreposição (overlap)."""
    chunks = []
    chunk_counter = 0

    for page_info in pages:
        text = page_info["text"]
        text_len = len(text)
        start = 0

        while start < text_len:
            end = start + chunk_size
            chunk_content = text[start:end].strip()

            if chunk_content:
                chunk_counter += 1
                chunks.append({
                    "chunk_id": f"{page_info['file_name']}_p{page_info['page']}_c{chunk_counter}",
                    "text": chunk_content,
                    "metadata": {
                        "source": page_info["file_name"],
                        "file_path": page_info["file_path"],
                        "page": page_info["page"],
                        "char_length": len(chunk_content)
                    }
                })

            if end >= text_len:
                break
            start += (chunk_size - overlap)

    return chunks


def run_ingestion():
    logger.info("==================================================")
    logger.info("🚀 Iniciando Pipeline de Ingestão de Documentos")
    logger.info(f"📂 Diretório de Documentos: {DOCS_DIR}")
    logger.info(f"💾 Diretório do ChromaDB:    {CHROMA_DIR}")
    logger.info("==================================================")

    # 1. Validar e listar os PDFs
    docs_path = Path(DOCS_DIR)
    if not docs_path.exists():
        logger.error(f"❌ Diretório de documentos não encontrado: {DOCS_DIR}")
        return

    pdf_files = sorted(list(docs_path.glob("*.pdf")) + list(docs_path.glob("*/*.pdf")))
    if not pdf_files:
        logger.warning(f"⚠️ Nenhum arquivo PDF encontrado em {DOCS_DIR}")
        return

    logger.info(f"📄 Localizados {len(pdf_files)} arquivos PDF para processamento.")

    # 2. Extrair páginas e gerar chunks
    all_chunks = []
    for pdf_file in pdf_files:
        logger.info(f"📖 Processando: {pdf_file.name}...")
        pages = extract_pages_from_pdf(pdf_file)
        file_chunks = create_chunks(pages, chunk_size=500, overlap=50)
        logger.info(f"   ↳ {len(pages)} páginas com texto extraídas -> {len(file_chunks)} chunks gerados.")
        all_chunks.extend(file_chunks)

    if not all_chunks:
        logger.warning("⚠️ Nenhum chunk de texto pôde ser gerado dos PDFs informados.")
        return

    logger.info(f"📊 Total consolidado: {len(all_chunks)} chunks para indexação.")

    # 3. Inicializar ChromaDB e Modelo de Embeddings
    os.makedirs(CHROMA_DIR, exist_ok=True)
    logger.info(f"🔄 Conectando ao ChromaDB persistente em: {CHROMA_DIR}")
    chroma_client = chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(anonymized_telemetry=False)
    )
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "KnowledgeHub AI Corporate Documents Collection"}
    )

    logger.info(f"🔄 Carregando modelo de embeddings: {EMBEDDING_MODEL_NAME}...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    # 4. Calcular Embeddings e Upsert no ChromaDB
    texts = [chunk["text"] for chunk in all_chunks]
    ids = [chunk["chunk_id"] for chunk in all_chunks]
    metadatas = [chunk["metadata"] for chunk in all_chunks]

    logger.info("🧠 Gerando embeddings para todos os chunks...")
    embeddings = embedding_model.encode(texts, show_progress_bar=True).tolist()

    logger.info(f"💾 Inserindo/Upserting {len(ids)} chunks na coleção '{COLLECTION_NAME}'...")
    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings
    )

    # 5. Validação final
    total_in_collection = collection.count()
    logger.info("==================================================")
    logger.info("🎉 Ingestão Concluída com Sucesso!")
    logger.info(f"📁 Arquivos PDF processados: {len(pdf_files)}")
    logger.info(f"🧩 Chunks inseridos nesta execução: {len(ids)}")
    logger.info(f"📈 Total de chunks indexados no ChromaDB: {total_in_collection}")
    logger.info(f"📍 Banco persistido em: {CHROMA_DIR}")
    logger.info("==================================================")


if __name__ == "__main__":
    run_ingestion()
