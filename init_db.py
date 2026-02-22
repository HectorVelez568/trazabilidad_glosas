# init_db.py
import asyncio
from database import Base, engine
from models import *  # Importa todos los modelos de tu proyecto

async def init():
    # Crea todas las tablas definidas en tus modelos
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init())
