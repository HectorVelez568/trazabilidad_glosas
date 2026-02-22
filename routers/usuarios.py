# routers/usuarios.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

# Importaciones para la base de datos y esquemas
from database import get_db_session # <-- Asegúrate de que get_db esté importado aquí
import schemas
import crud

# Importa las dependencias de seguridad desde auth.auth
# Asegúrate de que los nombres de las funciones sean EXACTAMENTE los que tienes en auth/auth.py
from auth.auth import get_current_active_user, get_current_admin_user, get_current_facturador_ips_user, get_current_auditor_ips_user, get_current_gerente_ips_user, get_current_auditor_eps_user, get_current_usuario_eps_user

router = APIRouter()

# Dependency para obtener la sesión de la base de datos
# ESTA FUNCIÓN ES CRUCIAL. Debe estar definida en cada router que necesite una sesión DB.
#def get_db_session():
#    db = get_db()
#    try:
#        yield db
#    finally:
#        db.close()

# Rutas para Usuarios

@router.post("/", response_model=schemas.UsuarioResponse, status_code=status.HTTP_201_CREATED)
# Asegúrate de que "db: Session = Depends(get_db_session)" esté CORRECTAMENTE escrito aquí.
def create_user(user: schemas.UsuarioCreate, db: Session = Depends(get_db_session)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    return crud.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=schemas.UsuarioResponse)
# Aquí también, usando la dependencia correcta.
def read_user(user_id: int, db: Session = Depends(get_db_session), current_user: schemas.UsuarioResponse = Depends(get_current_active_user)): # Ejemplo de protección
    # Aquí podrías añadir lógica de autorización, ej. solo admin o el propio usuario puede verse
    if current_user.rol != "ADMIN" and current_user.id_usuario != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para ver este usuario")
    
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user

@router.get("/", response_model=List[schemas.UsuarioResponse])
# Aquí también, usando la dependencia correcta y un ejemplo de protección por rol.
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session), current_user: schemas.UsuarioResponse = Depends(get_current_admin_user)): # Solo administradores
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.put("/{user_id}", response_model=schemas.UsuarioResponse)
# Y aquí, usando la dependencia correcta.
def update_user_route(user_id: int, user_update: schemas.UsuarioUpdate, db: Session = Depends(get_db_session), current_user: schemas.UsuarioResponse = Depends(get_current_active_user)): # Protección
    # Lógica de autorización: solo admin puede actualizar cualquier usuario, el propio usuario puede actualizarse a sí mismo
    if current_user.rol != "ADMIN" and current_user.id_usuario != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para actualizar este usuario")
    
    db_user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# Y finalmente aquí, usando la dependencia correcta.
def delete_user_route(user_id: int, db: Session = Depends(get_db_session), current_user: schemas.UsuarioResponse = Depends(get_current_admin_user)): # Solo administradores
    db_user = crud.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {}