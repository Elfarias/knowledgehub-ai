"""
Gerenciador do Banco Vetorial ChromaDB.
Responsável por carregar o modelo de embeddings local, criar a coleção 
e persistir os chunks com seus metadados de rastreabilidade.
"""

from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
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
        
        # Carrega o modelo de embeddings local (executando na CPU)
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
        # O modelo e5 costuma se beneficiar do prefixo 'passage: ' para indexação, 
        # mas podemos passar o texto direto para simplicidade do MVP.
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True).tolist()

        # Insere no ChromaDB
        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadados
        )
        print(f"✅ {len(ids)} chunks vetorizados e salvos com sucesso no ChromaDB!")

    def query_similarity(self, query_text: str, n_results: int = 3) -> Dict[str, Any]:
        """
        Realiza uma busca semântica por similaridade no banco vetorial,
        retornando os trechos mais relevantes e suas evidências (metadados).
        """
        # Para busca com e5, o prefixo 'query: ' melhora a recuperação semântica
        query_embedding = self.embedding_model.encode([f"query: {query_text}"]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        return results