# routers/instituciones.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db_session
import schemas
import crud

router = APIRouter()

# Dependency para obtener la sesión de la base de datos
#def get_db_session():
#    db = get_db()
#    try:
#        yield db
#    finally:
#        db.close()

# ====================================================================
# Rutas para Institucion
# ====================================================================

@router.post("/", response_model=schemas.InstitucionResponse, status_code=status.HTTP_201_CREATED)
def create_institucion(institucion: schemas.InstitucionCreate, db: Session = Depends(get_db_session)):
    db_institucion = crud.get_institucion_by_nit(db, nit=institucion.nit)
    if db_institucion:
        raise HTTPException(status_code=400, detail="El NIT de la institución ya está registrado")
    return crud.create_institucion(db=db, institucion=institucion)

@router.get("/{institucion_id}", response_model=schemas.InstitucionResponse)
def read_institucion(institucion_id: int, db: Session = Depends(get_db_session)):
    db_institucion = crud.get_institucion(db, institucion_id=institucion_id)
    if db_institucion is None:
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    return db_institucion

@router.get("/", response_model=List[schemas.InstitucionResponse])
def read_instituciones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    instituciones = crud.get_instituciones(db, skip=skip, limit=limit)
    return instituciones

@router.put("/{institucion_id}", response_model=schemas.InstitucionResponse)
def update_institucion_route(institucion_id: int, institucion_update: schemas.InstitucionUpdate, db: Session = Depends(get_db_session)):
    db_institucion = crud.update_institucion(db, institucion_id=institucion_id, institucion_update=institucion_update)
    if db_institucion is None:
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    return db_institucion

@router.delete("/{institucion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_institucion_route(institucion_id: int, db: Session = Depends(get_db_session)):
    db_institucion = crud.delete_institucion(db, institucion_id=institucion_id)
    if db_institucion is None:
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    return {} # Devuelve una respuesta vacía para 204 No Content