"""
Aplicação principal FastAPI para o KnowledgeHub AI.
Expõe endpoints para consulta RAG corporativa com citação de fontes, CORS, Health Check,
registo de auditoria em BD e endpoint de diagnóstico do ChromaDB.
"""

from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import os
import logging
import chromadb
from sentence_transformers import SentenceTransformer

from app.services.llm_service import GeminiService
from app.modules.chat.router import router as chat_router
from app.core.database import get_db
from app.modules.chat.service import create_query_log

# Configuração de logging estruturado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KnowledgeHubAPI")

app = FastAPI(
    title="KnowledgeHub AI API",
    description="API corporativa de RAG com citação de fontes, governança de dados, registo de auditoria em BD e segurança de nível de produção.",
    version="1.1.2"
)

# Middleware de cabeçalhos de segurança HTTP recomendados (OWASP / Lighthouse)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response

# Configuração de CORS com origens explícitas e configuráveis via ambiente
raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8501,http://127.0.0.1:8501,http://localhost:3000,http://127.0.0.1:3000"
)
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Registo dos routers modulares (ex: módulo de chat e logs de auditoria RAG)
app.include_router(chat_router)

# Inicialização segura dos serviços globais (ChromaDB, Embeddings, LLM com caminho absoluto)
try:
    llm_service = GeminiService()
    
    # Caminho absoluto fixo para a pasta data/chroma_db dentro de 'backend'
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CHROMA_DIR = os.path.join(BASE_DIR, "data", "chroma_db")
    DOCS_DIR = os.path.join(BASE_DIR, "data", "docs")
    
    EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"

    logger.info(f"🔄 Inicializando ChromaDB em: {CHROMA_DIR}")
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = chroma_client.get_or_create_collection(name="knowledgehub_docs")
    
    logger.info("🔄 Carregando modelo de embeddings...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    logger.info("✅ Serviços globais inicializados com sucesso para a API.")
except Exception as e:
    logger.error(f"❌ Erro crítico ao inicializar dependências da API: {e}")
    raise e


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=2,
        max_length=2000,
        description="Pergunta do usuário para a base corporativa",
        example="Quais são as regras para home office?"
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=20,
        description="Número de chunks relevantes a recuperar (entre 1 e 20)"
    )

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[Dict[str, Any]]


@app.get("/", tags=["Status"])
def read_root():
    return {
        "status": "online",
        "service": "KnowledgeHub AI API",
        "phase": "Produção - Modular com Auditoria PostgreSQL e Diagnóstico"
    }


@app.get("/health", tags=["Status"])
def health_check():
    """Valida a saúde do serviço, a conectividade com o ChromaDB e os módulos ativos."""
    try:
        count = collection.count()
        return {
            "status": "healthy",
            "chroma_db": "connected",
            "documents_indexed": count,
            "llm_provider": "OpenRouter / Gemini / NVIDIA Nemotron",
            "modules": ["chat_rag", "audit_logging", "chroma_debug"]
        }
    except Exception as e:
        logger.error(f"Health check falhou: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço degradado ou dependências inacessíveis."
        )


@app.get("/api/v1/debug/chroma", tags=["Debug"])
def debug_chroma_collection():
    """Retorna o número de documentos indexados e uma amostra do conteúdo no ChromaDB (somente em desenvolvimento)."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    if env not in ("development", "dev", "local"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Endpoint de debug desativado em ambiente de produção."
        )
    try:
        count = collection.count()
        sample = collection.peek(limit=5) if count > 0 else {"metadatas": [], "documents": []}
        
        return {
            "total_chunks_indexados": count,
            "amostra_metadados": sample.get("metadatas", []),
            "amostra_textos": sample.get("documents", [])
        }
    except Exception as e:
        logger.error(f"Erro ao acessar ChromaDB no endpoint de debug: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao obter diagnóstico do ChromaDB."
        )


@app.post("/api/v1/query", response_model=QueryResponse, tags=["RAG Query"])
async def query_knowledge_base(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        logger.info(f"🔍 Recebida requisição de consulta: '{request.query}'")
        
        # 1. Gerar embedding da query
        query_embedding = embedding_model.encode(request.query).tolist()

        # 2. Buscar chunks relevantes no ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=request.top_k
        )

        documents = results["documents"][0] if results["documents"] else []
        metadatas = results["metadatas"][0] if results["metadatas"] else []

        context_chunks = []
        for doc, meta in zip(documents, metadatas):
            context_chunks.append({
                "text": doc,
                "metadata": meta
            })

        if not context_chunks:
            answer = "Não possuo informações relevantes nos documentos internos para responder a esta solicitação."
            sources = []
        else:
            # 3. Gerar resposta fundamentada via LLM
            answer = llm_service.generate_answer(request.query, context_chunks)

            # 4. Extrair metadados das fontes consultadas
            sources = [
                {
                    "source": chunk["metadata"].get("source", "Desconhecido"),
                    "page": chunk["metadata"].get("page", "N/A")
                }
                for chunk in context_chunks
            ]

        # 5. Registo de auditoria no PostgreSQL
        await create_query_log(
            db=db,
            user_query=request.query,
            llm_response=answer,
            sources=sources
        )

        logger.info(f"✅ Resposta gerada e auditada com sucesso. Fontes consultadas: {len(sources)}")
        return QueryResponse(
            query=request.query,
            answer=answer,
            sources=sources
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao processar requisição de consulta: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no processamento da consulta RAG. Por favor, tente novamente mais tarde."
        )