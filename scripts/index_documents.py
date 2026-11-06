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