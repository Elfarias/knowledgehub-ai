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