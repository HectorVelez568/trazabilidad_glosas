# routers/auth.py

# routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db_session # <-- Asegúrate de que get_db esté importado aquí
import schemas
import crud
from auth.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_password, get_current_active_user, get_current_admin_user

router = APIRouter()

# Endpoint para obtener un token de acceso (login)
@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session)
):
    user = crud.get_user_by_email(db, email=form_data.username) # OAuth2PasswordRequestForm usa 'username' para el email
    # ¡LA CORRECCIÓN ESTÁ AQUÍ!
    if not user or not user.activo or not verify_password(form_data.password, user.password_hash): # CAMBIADO a .password_hash
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id_usuario)}, # El 'sub' (subject) es el identificador del usuario
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id_usuario, "user_name": user.nombre_completo} # Añadido user_id y user_name para el frontend

# Ejemplo de ruta protegida (para probar)
@router.get("/users/me/", response_model=schemas.UsuarioResponse)
async def read_users_me(current_user: schemas.UsuarioResponse = Depends(get_current_active_user)):
    return current_user

# Ejemplo de ruta solo para administradores
@router.get("/admin/test/", response_model=str)
async def admin_test(current_user: schemas.UsuarioResponse = Depends(get_current_admin_user)):
    return f"¡Hola Administrador {current_user.nombre_completo}! Tienes acceso total."

