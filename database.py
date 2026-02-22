from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator # Necesario para el tipo de retorno

# URL de conexión a tu base de datos PostgreSQL
# Asegúrate de reemplazar 'tu_contraseña_segura'
DATABASE_URL = "postgresql+psycopg://glosas_user:Glosas_2025*@localhost:5432/trazabilidad_glosas"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Función DE DEPENDENCIA ÚNICA para obtener la sesión de DB.
# Ahora se llamará get_db_session y se importará en todos los routers.
def get_db_session() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()