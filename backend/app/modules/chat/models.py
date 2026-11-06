"""
Modelos relacionais para registro de consultas e auditoria (QueryLog).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, JSON
from app.core.database import Base

class QueryLogModel(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # Armazena a lista de fontes utilizadas em formato JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)