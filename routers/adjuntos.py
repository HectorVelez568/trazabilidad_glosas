# routers/adjuntos.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db_session
import schemas # Importa tus schemas
import crud # Importa tus funciones CRUD
import models # Asegúrate de importar los modelos si necesitas acceder a ellos directamente

router = APIRouter()

# Dependency para obtener la sesión de la base de datos
#def get_db_session():
#   db = get_db()
#    try:
#        yield db
#    finally:
#        db.close()

# ====================================================================
# Rutas para Adjunto
# ====================================================================

@router.post("/", response_model=schemas.AdjuntoResponse, status_code=status.HTTP_201_CREATED)
def create_adjunto(adjunto: schemas.AdjuntoCreate, db: Session = Depends(get_db_session)):
    # Validar que al menos uno de id_glosa o id_respuesta_glosa esté presente
    if not adjunto.id_glosa and not adjunto.id_respuesta_glosa:
        raise HTTPException(
            status_code=400,
            detail="Se debe especificar al menos 'id_glosa' o 'id_respuesta_glosa' para el adjunto."
        )

    # Opcional: Validar si la glosa existe (si se proporciona)
    if adjunto.id_glosa:
        db_glosa = crud.get_glosa(db, adjunto.id_glosa)
        if not db_glosa:
            raise HTTPException(status_code=404, detail="Glosa no encontrada para el adjunto.")

    # Opcional: Validar si la respuesta de glosa existe (si se proporciona)
    if adjunto.id_respuesta_glosa:
        db_respuesta = crud.get_respuesta_glosa(db, adjunto.id_respuesta_glosa)
        if not db_respuesta:
            raise HTTPException(status_code=404, detail="Respuesta de Glosa no encontrada para el adjunto.")
            
    # Opcional: Validar si el usuario que sube existe
    if adjunto.usuario_que_sube:
        db_usuario = crud.get_user(db, adjunto.usuario_que_sube)
        if not db_usuario:
            raise HTTPException(status_code=404, detail="Usuario que sube no encontrado.")

    return crud.create_adjunto(db=db, adjunto=adjunto)

@router.get("/{adjunto_id}", response_model=schemas.AdjuntoResponse)
def read_adjunto(adjunto_id: int, db: Session = Depends(get_db_session)):
    db_adjunto = crud.get_adjunto(db, adjunto_id=adjunto_id)
    if db_adjunto is None:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")
    return db_adjunto

@router.get("/", response_model=List[schemas.AdjuntoResponse])
def read_adjuntos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    adjuntos = crud.get_adjuntos(db, skip=skip, limit=limit)
    return adjuntos

@router.put("/{adjunto_id}", response_model=schemas.AdjuntoResponse)
def update_adjunto_route(adjunto_id: int, adjunto_update: schemas.AdjuntoUpdate, db: Session = Depends(get_db_session)):
    # Opcional: Validar que la glosa, respuesta de glosa o usuario existan si se actualizan
    if adjunto_update.id_glosa:
        db_glosa = crud.get_glosa(db, adjunto_update.id_glosa)
        if not db_glosa:
            raise HTTPException(status_code=404, detail="Nueva glosa no encontrada para el adjunto.")
    
    if adjunto_update.id_respuesta_glosa:
        db_respuesta = crud.get_respuesta_glosa(db, adjunto_update.id_respuesta_glosa)
        if not db_respuesta:
            raise HTTPException(status_code=404, detail="Nueva respuesta de glosa no encontrada para el adjunto.")

    if adjunto_update.usuario_que_sube:
        db_usuario = crud.get_user(db, adjunto_update.usuario_que_sube)
        if not db_usuario:
            raise HTTPException(status_code=404, detail="Nuevo usuario que sube no encontrado.")

    db_adjunto = crud.update_adjunto(db, adjunto_id=adjunto_id, adjunto_update=adjunto_update)
    if db_adjunto is None:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")
    return db_adjunto

@router.delete("/{adjunto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_adjunto_route(adjunto_id: int, db: Session = Depends(get_db_session)):
    db_adjunto = crud.delete_adjunto(db, adjunto_id=adjunto_id)
    if db_adjunto is None:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")
    return {} # Devuelve una respuesta vacía para 204 No Content