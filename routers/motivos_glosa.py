# routers/motivos_glosa.py

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
# Rutas para MotivoGlosa
# ====================================================================

@router.post("/", response_model=schemas.MotivoGlosaResponse, status_code=status.HTTP_201_CREATED)
def create_motivo_glosa(motivo_glosa: schemas.MotivoGlosaCreate, db: Session = Depends(get_db_session)):
    db_motivo = crud.get_motivo_glosa_by_codigo(db, codigo=motivo_glosa.codigo_motivo)
    if db_motivo:
        raise HTTPException(status_code=400, detail="El código de motivo de glosa ya está registrado")
    return crud.create_motivo_glosa(db=db, motivo_glosa=motivo_glosa)

@router.get("/{motivo_glosa_id}", response_model=schemas.MotivoGlosaResponse)
def read_motivo_glosa(motivo_glosa_id: int, db: Session = Depends(get_db_session)):
    db_motivo = crud.get_motivo_glosa(db, motivo_glosa_id=motivo_glosa_id)
    if db_motivo is None:
        raise HTTPException(status_code=404, detail="Motivo de glosa no encontrado")
    return db_motivo

@router.get("/", response_model=List[schemas.MotivoGlosaResponse])
def read_motivos_glosa(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    motivos_glosa = crud.get_motivos_glosa(db, skip=skip, limit=limit)
    return motivos_glosa

@router.put("/{motivo_glosa_id}", response_model=schemas.MotivoGlosaResponse)
def update_motivo_glosa_route(motivo_glosa_id: int, motivo_glosa_update: schemas.MotivoGlosaUpdate, db: Session = Depends(get_db_session)):
    db_motivo = crud.update_motivo_glosa(db, motivo_glosa_id=motivo_glosa_id, motivo_glosa_update=motivo_glosa_update)
    if db_motivo is None:
        raise HTTPException(status_code=404, detail="Motivo de glosa no encontrado")
    return db_motivo

@router.delete("/{motivo_glosa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_motivo_glosa_route(motivo_glosa_id: int, db: Session = Depends(get_db_session)):
    db_motivo = crud.delete_motivo_glosa(db, motivo_glosa_id=motivo_glosa_id)
    if db_motivo is None:
        raise HTTPException(status_code=404, detail="Motivo de glosa no encontrado")
    return {} # Devuelve una respuesta vacía para 204 No Content