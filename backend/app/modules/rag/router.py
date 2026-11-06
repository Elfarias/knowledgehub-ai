from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.infrastructure.database.session import get_db
from backend.app.modules.chat.models import QueryLogModel

router = APIRouter()

@router.post("/query")
async def process_rag_query(payload: QueryPayload, db: AsyncSession = Depends(get_db)):
    # 1. Executa busca no ChromaDB e gera resposta com o Gemini
    answer, sources = run_rag_pipeline(payload.query, payload.top_k)
    
    # 2. Persiste o log de auditoria de forma assíncrona no PostgreSQL
    db_log = QueryLogModel(
        query=payload.query,
        answer=answer,
        sources=sources
    )
    db.add(db_log)
    await db.commit()
    
    return {"answer": answer, "sources": sources}