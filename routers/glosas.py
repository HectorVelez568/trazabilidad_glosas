# routers/glosas.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db_session

import schemas
import crud
import models
from auth.auth import get_current_active_user, get_current_auditor_ips_user, get_current_auditor_eps_user, get_current_admin_user

router = APIRouter(
    # prefix="/glosas", # Asegúrate de que este prefix esté configurado en main.py si lo necesitas
    tags=["Glosas"]
)

# ====================================================================
# Rutas para Glosa
# ====================================================================

@router.post("/", response_model=schemas.Glosa, status_code=status.HTTP_201_CREATED)
def create_glosa(glosa: schemas.GlosaCreate, db: Session = Depends(get_db_session)):
    db_factura = crud.get_factura(db, glosa.id_factura)
    if not db_factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    db_motivo_glosa = crud.get_motivo_glosa(db, glosa.id_motivo_glosa)
    if not db_motivo_glosa:
        raise HTTPException(status_code=404, detail="Motivo de glosa no encontrado")

    if glosa.usuario_responsable:
        db_usuario = crud.get_user(db, glosa.usuario_responsable)
        if not db_usuario:
            raise HTTPException(status_code=404, detail="Usuario responsable no encontrado")

    return crud.create_glosa(db=db, glosa=glosa)

@router.get("/{glosa_id}", response_model=schemas.Glosa)
def read_glosa(glosa_id: int, db: Session = Depends(get_db_session)):
    db_glosa = crud.get_glosa(db, glosa_id=glosa_id)
    if db_glosa is None:
        raise HTTPException(status_code=404, detail="Glosa no encontrada")
    return db_glosa

@router.get("/", response_model=List[schemas.Glosa])
def read_glosas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    glosas = crud.get_glosas(db, skip=skip, limit=limit)
    return glosas

# ====================================================================
# RUTA DE ACTUALIZACIÓN DE GLOSA CONSOLIDADA (SOLO UNA DEFINICIÓN)
# Se combina la lógica de validación con la dependencia de usuario
# ====================================================================
@router.put("/{glosa_id}", response_model=schemas.Glosa, operation_id="update_glosa_by_id") # <-- Añadimos un operation_id único
def update_glosa_route(
    glosa_id: int,
    glosa_update: schemas.GlosaUpdate, # Nombre más claro para los datos de actualización
    db: Session = Depends(get_db_session),
    # Aquí puedes elegir la dependencia de usuario que necesites:
    # get_current_active_user, get_current_auditor_ips_user, get_current_admin_user, etc.
    current_user: schemas.UsuarioResponse = Depends(get_current_active_user)
):
    # 1. Verificar si la glosa existe
    db_glosa = crud.get_glosa(db, glosa_id=glosa_id)
    if not db_glosa:
        raise HTTPException(status_code=404, detail="Glosa no encontrada")
    
    # 2. Validaciones de IDs relacionados (factura, motivo, usuario responsable)
    if glosa_update.id_factura is not None: # Usar 'is not None' para diferenciar de 0 o False si fueran esos valores
        db_factura = crud.get_factura(db, glosa_update.id_factura)
        if not db_factura:
            raise HTTPException(status_code=404, detail="Nueva factura no encontrada para la glosa.")

    if glosa_update.id_motivo_glosa is not None:
        db_motivo_glosa = crud.get_motivo_glosa(db, glosa_update.id_motivo_glosa)
        if not db_motivo_glosa:
            raise HTTPException(status_code=404, detail="Nuevo motivo de glosa no encontrado.")

    if glosa_update.usuario_responsable is not None:
        db_usuario = crud.get_user(db, glosa_update.usuario_responsable)
        if not db_usuario:
            raise HTTPException(status_code=404, detail="Nuevo usuario responsable no encontrado.")

    # 3. Opcional: Implementar lógica de permisos más granular basada en current_user
    # Por ejemplo, solo el usuario responsable o un admin pueden actualizar la glosa
    # if current_user.id_usuario != db_glosa.usuario_responsable and current_user.rol != "ADMIN":
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para actualizar esta glosa")

    # 4. Realizar la actualización
    updated_glosa = crud.update_glosa(db, db_glosa=db_glosa, glosa_update=glosa_update)
    # Nota: crud.update_glosa ya debería manejar si no hay glosa, pero la comprobación inicial es buena.
    # Si crud.update_glosa devuelve None en caso de fallo, podrías añadir una comprobación aquí también.
    
    return updated_glosa

@router.delete("/{glosa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_glosa_route(glosa_id: int, db: Session = Depends(get_db_session)):
    db_glosa = crud.delete_glosa(db, glosa_id=glosa_id)
    if db_glosa is None:
        raise HTTPException(status_code=404, detail="Glosa no encontrada")
    return {} # Las eliminaciones exitosas a menudo devuelven un cuerpo vacío con 204 No Content