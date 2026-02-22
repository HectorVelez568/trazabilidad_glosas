import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

# 🔥 TOMAR DESDE VARIABLE DE ENTORNO
DATABASE_URL = os.getenv("DATABASE_URL")

# ⚠️ FALLBACK SOLO PARA LOCAL
if not DATABASE_URL:
    DATABASE_URL = "postgresql+psycopg://glosas_user:Glosas_2025*@localhost:5432/trazabilidad_glosas"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db_session() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()