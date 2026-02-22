# auth/auth.py

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

from sqlalchemy.orm import Session
# Importar get_db_session desde database para usarlo en las dependencias
from database import get_db_session # <-- ¡CAMBIO CRUCIAL AQUÍ!
import crud # Necesitaremos crud para buscar usuarios
import schemas # Asegúrate de que schemas esté importado

# Cargar variables de entorno del archivo .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Contexto para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de seguridad OAuth2 para FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # La URL donde el cliente puede obtener un token

# Funciones de Hashing de Contraseñas
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con una contraseña hasheada."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashea una contraseña para almacenarla de forma segura."""
    return pwd_context.hash(password)

# Funciones para JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token de acceso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """Decodifica un token JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no válidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ====================================================================
# Dependencias de Seguridad
# ====================================================================

# Dependencia para obtener el usuario actual a partir del token JWT
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_session)) -> schemas.UsuarioResponse:
    """Obtiene el usuario autenticado a partir del token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        user_id: int = payload.get("sub") # 'sub' es el estándar para el sujeto (subject) del token
        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    user = crud.get_user(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
        
    return user


# Dependencias de autorización por rol
def get_current_active_user(current_user: schemas.UsuarioResponse = Depends(get_current_user)) -> schemas.UsuarioResponse:
    """Dependencia para verificar que el usuario está activo."""
    return current_user # La verificación de activo ya se hace en get_current_user

def get_current_admin_user(current_user: schemas.UsuarioResponse = Depends(get_current_active_user)) -> schemas.UsuarioResponse:
    """Dependencia para usuarios con rol 'ADMIN'."""
    if current_user.rol != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador"
        )
    return current_user

# Puedes crear más dependencias según los roles que tengas:
def get_current_facturador_ips_user(current_user: schemas.UsuarioResponse = Depends(get_current_active_user)) -> schemas.UsuarioResponse:
    """Dependencia para usuarios con rol 'FACTURADOR_IPS'."""
    if current_user.rol != "FACTURADOR_IPS" and current_user.rol != "ADMIN": # Los admin suelen tener todos los permisos
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de facturador IPS"
        )
    return current_user

def get_current_auditor_ips_user(current_user: schemas.UsuarioResponse = Depends(get_current_active_user)) -> schemas.UsuarioResponse:
    """Dependencia para usuarios con rol 'AUDITOR_IPS'."""
    if current_user.rol not in ["AUDITOR_IPS", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de auditor IPS"
        )
    return current_user

def get_current_gerente_ips_user(current_user: schemas.UsuarioResponse = Depends(get_current_active_user)) -> schemas.UsuarioResponse:
    """Dependencia para usuarios con rol 'GERENTE_IPS'."""
    if current_user.rol not in ["GERENTE_IPS", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de gerente IPS"
        )
    return current_user

def get_current_auditor_eps_user(current_user: schemas.UsuarioResponse = Depends(get_current_active_user)) -> schemas.UsuarioResponse:
    """Dependencia para usuarios con rol 'AUDITOR_EPS'."""
    if current_user.rol not in ["AUDITOR_EPS", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de auditor EPS"
        )
    return current_user

def get_current_usuario_eps_user(current_user: schemas.UsuarioResponse = Depends(get_current_active_user)) -> schemas.UsuarioResponse:
    """Dependencia para usuarios con rol 'USUARIO_EPS'."""
    if current_user.rol not in ["USUARIO_EPS", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de usuario EPS"
        )
    return current_user