from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.chat.service import create_query_log

router = APIRouter(prefix="/chat", tags=["Chat RAG"])

@router.post("/")
async def rag_chat_endpoint(
    prompt: str, 
    db: AsyncSession = Depends(get_db)
):
    print("--> A ENTRAR NO ENDPOINT DE CHAT RAG <---")
    
    # 1. Simulação do fluxo RAG
    llm_response = "Esta é a resposta gerada pelo sistema RAG com base nos dados recuperados."
    sources = [{"source": "documento_exemplo.pdf", "page": 1}]

    # 2. Gravação assíncrona do log de auditoria
    try:
        await create_query_log(
            db=db, 
            user_query=prompt, 
            llm_response=llm_response,
            sources=sources
        )
        print("--> LOG GRAVADO COM SUCESSO NO BANCO <---")
    except Exception as e:
        print(f"--> ERRO AO GRAVAR LOG: {e} <---")

    return {
        "query": prompt,
        "response": llm_response,
        "sources": sources
    }