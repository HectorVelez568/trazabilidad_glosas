# routers/respuestas_glosa.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db_session
import schemas # Importa tus schemas
import crud # Importa tus funciones CRUD
import models # Asegúrate de importar los modelos si necesitas acceder a ellos directamente (ej: para errores)

router = APIRouter()

# Dependency para obtener la sesión de la base de datos
#def get_db_session():
#    db = get_db()
#    try:
#        yield db
#    finally:
#        db.close()

# ====================================================================
# Rutas para RespuestaGlosa
# ====================================================================

@router.post("/", response_model=schemas.RespuestaGlosaResponse, status_code=status.HTTP_201_CREATED)
def create_respuesta_glosa(respuesta_glosa: schemas.RespuestaGlosaCreate, db: Session = Depends(get_db_session)):
    # Opcional: Validar si la glosa existe
    db_glosa = crud.get_glosa(db, respuesta_glosa.id_glosa)
    if not db_glosa:
        raise HTTPException(status_code=404, detail="Glosa no encontrada")

    # Opcional: Validar si el usuario que responde existe
    db_usuario = crud.get_user(db, respuesta_glosa.usuario_que_responde)
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario respondedor no encontrado")

    return crud.create_respuesta_glosa(db=db, respuesta_glosa=respuesta_glosa)

@router.get("/{respuesta_id}", response_model=schemas.RespuestaGlosaResponse)
def read_respuesta_glosa(respuesta_id: int, db: Session = Depends(get_db_session)):
    db_respuesta = crud.get_respuesta_glosa(db, respuesta_id=respuesta_id)
    if db_respuesta is None:
        raise HTTPException(status_code=404, detail="Respuesta de Glosa no encontrada")
    return db_respuesta

@router.get("/", response_model=List[schemas.RespuestaGlosaResponse])
def read_respuestas_glosa(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    respuestas = crud.get_respuestas_glosa(db, skip=skip, limit=limit)
    return respuestas

@router.put("/{respuesta_id}", response_model=schemas.RespuestaGlosaResponse)
def update_respuesta_glosa_route(respuesta_id: int, respuesta_update: schemas.RespuestaGlosaUpdate, db: Session = Depends(get_db_session)):
    # Opcional: Validar que la glosa o el usuario respondedor existan si se actualizan
    if respuesta_update.id_glosa:
        db_glosa = crud.get_glosa(db, respuesta_update.id_glosa)
        if not db_glosa:
            raise HTTPException(status_code=404, detail="Nueva glosa no encontrada para la respuesta.")
    
    if respuesta_update.usuario_que_responde:
        db_usuario = crud.get_user(db, respuesta_update.usuario_que_responde)
        if not db_usuario:
            raise HTTPException(status_code=404, detail="Nuevo usuario respondedor no encontrado.")

    db_respuesta = crud.update_respuesta_glosa(db, respuesta_id=respuesta_id, respuesta_update=respuesta_update)
    if db_respuesta is None:
        raise HTTPException(status_code=404, detail="Respuesta de Glosa no encontrada")
    return db_respuesta

@router.delete("/{respuesta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_respuesta_glosa_route(respuesta_id: int, db: Session = Depends(get_db_session)):
    db_respuesta = crud.delete_respuesta_glosa(db, respuesta_id=respuesta_id)
    if db_respuesta is None:
        raise HTTPException(status_code=404, detail="Respuesta de Glosa no encontrada")
    # Nota: Aquí podrías añadir lógica para eliminar adjuntos relacionados
    return {} # Devuelve una respuesta vacía para 204 No Content

