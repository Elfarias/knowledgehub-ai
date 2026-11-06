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
    
    Retorna uma lista de dicionários contendo o texto e os metadados da página:
    [
        {
            "file_name": "Politica_RH.pdf",
            "page": 1,
            "text": "Conteúdo da página 1..."
        }, ...
    ]
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