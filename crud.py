# crud.py

from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas # <--- ¡ASEGÚRATE DE QUE ESTA LÍNEA ESTÉ AQUÍ!
from datetime import datetime, date, timezone
from typing import List, Optional, TypeVar, Type, Any
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

# Importar funciones de hashing desde auth.auth
# Asegúrate de que esta ruta de importación sea correcta.
# Si tu archivo de lógica de auth está en C:\trazabilidad_glosas_api\auth\auth.py
# entonces 'from auth.auth import' es la forma correcta.
from auth.auth import get_password_hash, verify_password

# ====================================================================
# Funciones CRUD para Usuario
# ====================================================================

def get_user(db: Session, user_id: int):
    return db.query(models.Usuario).filter(models.Usuario.id_usuario == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UsuarioCreate):
    # Hashear la contraseña antes de almacenarla
    password_to_store = get_password_hash(user.password)
    db_user = models.Usuario(
        nombre_completo=user.nombre_completo,
        email=user.email,
        password_hash=password_to_store, # Almacena la contraseña hasheada
        rol=user.rol,
        telefono=user.telefono,
        fecha_creacion=datetime.now(),
        activo=True # Los nuevos usuarios están activos por defecto
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UsuarioUpdate):
    db_user = db.query(models.Usuario).filter(models.Usuario.id_usuario == user_id).first()
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True) # Usa model_dump para Pydantic v2
        
        # Si la contraseña se va a actualizar, hashearla
        if "password" in update_data and update_data["password"] is not None:
            update_data["password_hashed"] = get_password_hash(update_data["password"])
            del update_data["password"] # Eliminar el campo de contraseña sin hashear
        
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.Usuario).filter(models.Usuario.id_usuario == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user


# ====================================================================
# Funciones CRUD para Institucion
# ====================================================================

def get_institucion(db: Session, institucion_id: int):
    return db.query(models.Institucion).filter(models.Institucion.id_institucion == institucion_id).first()

def get_institucion_by_nit(db: Session, nit: str):
    return db.query(models.Institucion).filter(models.Institucion.nit == nit).first()

def get_instituciones(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Institucion).offset(skip).limit(limit).all()

def create_institucion(db: Session, institucion: schemas.InstitucionCreate):
    db_institucion = models.Institucion(**institucion.model_dump())
    db.add(db_institucion)
    db.commit()
    db.refresh(db_institucion)
    return db_institucion

def update_institucion(db: Session, institucion_id: int, institucion_update: schemas.InstitucionUpdate):
    db_institucion = db.query(models.Institucion).filter(models.Institucion.id_institucion == institucion_id).first()
    if db_institucion:
        update_data = institucion_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_institucion, key, value)
        db.commit()
        db.refresh(db_institucion)
    return db_institucion

def delete_institucion(db: Session, institucion_id: int):
    db_institucion = db.query(models.Institucion).filter(models.Institucion.id_institucion == institucion_id).first()
    if db_institucion:
        db.delete(db_institucion)
        db.commit()
    return db_institucion

# ====================================================================
# Funciones CRUD para MotivoGlosa
# ====================================================================

def get_motivo_glosa(db: Session, motivo_glosa_id: int):
    return db.query(models.MotivoGlosa).filter(models.MotivoGlosa.id_motivo_glosa == motivo_glosa_id).first()

def get_motivo_glosa_by_codigo(db: Session, codigo: str):
    return db.query(models.MotivoGlosa).filter(models.MotivoGlosa.codigo_motivo == codigo).first()

def get_motivos_glosa(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MotivoGlosa).offset(skip).limit(limit).all()

def create_motivo_glosa(db: Session, motivo_glosa: schemas.MotivoGlosaCreate):
    db_motivo_glosa = models.MotivoGlosa(**motivo_glosa.model_dump())
    db.add(db_motivo_glosa)
    db.commit()
    db.refresh(db_motivo_glosa)
    return db_motivo_glosa

def update_motivo_glosa(db: Session, motivo_glosa_id: int, motivo_glosa_update: schemas.MotivoGlosaUpdate):
    db_motivo_glosa = db.query(models.MotivoGlosa).filter(models.MotivoGlosa.id_motivo_glosa == motivo_glosa_id).first()
    if db_motivo_glosa:
        update_data = motivo_glosa_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_motivo_glosa, key, value)
        db.commit()
        db.refresh(db_motivo_glosa)
    return db_motivo_glosa

def delete_motivo_glosa(db: Session, motivo_glosa_id: int):
    db_motivo_glosa = db.query(models.MotivoGlosa).filter(models.MotivoGlosa.id_motivo_glosa == motivo_glosa_id).first()
    if db_motivo_glosa:
        db.delete(db_motivo_glosa)
        db.commit()
    return db_motivo_glosa


# ====================================================================
# Funciones CRUD para Factura
# ====================================================================

def get_factura(db: Session, factura_id: int):
    return db.query(models.Factura).filter(models.Factura.id_factura == factura_id).first()

def get_factura_by_numero(db: Session, numero_factura: str):
    return db.query(models.Factura).filter(models.Factura.numero_factura == numero_factura).first()

def get_facturas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Factura).offset(skip).limit(limit).all()

def create_factura(db: Session, factura: schemas.FacturaCreate):
    db_factura = models.Factura(**factura.model_dump())
    db.add(db_factura)
    db.commit()
    db.refresh(db_factura)
    return db_factura

def update_factura(db: Session, factura_id: int, factura_update: schemas.FacturaUpdate):
    db_factura = db.query(models.Factura).filter(models.Factura.id_factura == factura_id).first()
    if db_factura:
        update_data = factura_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_factura, key, value)
        db.commit()
        db.refresh(db_factura)
    return db_factura

def delete_factura(db: Session, factura_id: int):
    db_factura = db.query(models.Factura).filter(models.Factura.id_factura == factura_id).first()
    if db_factura:
        db.delete(db_factura)
        db.commit()
    return db_factura

# ====================================================================
# Funciones CRUD para Glosa
# ====================================================================

def get_glosa(db: Session, glosa_id: int):
    return db.query(models.Glosa).filter(models.Glosa.id_glosa == glosa_id).first()

def get_glosas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Glosa).offset(skip).limit(limit).all()

def create_glosa(db: Session, glosa: schemas.GlosaCreate):
    glosa_data = glosa.model_dump()
    if "fecha_registro_glosa" in glosa_data:
        del glosa_data["fecha_registro_glosa"]
    if "fecha_ultima_actualizacion" in glosa_data:
        del glosa_data["fecha_ultima_actualizacion"]
    if glosa_data.get("usuario_responsable") == 0:
        glosa_data["usuario_responsable"] = None
    db_glosa = models.Glosa(**glosa_data)

    try:
        db.add(db_glosa)
        db.commit()
        db.refresh(db_glosa) # Refresca el objeto para obtener el id_glosa y los valores default generados
        return db_glosa
    except IntegrityError as e:
        db.rollback() # Revierte la transacción en caso de error de integridad
        print(f"Error de integridad al crear glosa: {e.orig}")
        raise e # Re-lanza la excepción si quieres ver el traceback completo para depuración
    except Exception as e:
        db.rollback() # Revierte cualquier otra excepción inesperada
        print(f"Error inesperado al crear glosa: {e}")
        raise e

def update_glosa(db: Session, glosa_id: int, glosa_update: schemas.GlosaUpdate) -> Optional[models.Glosa]:
    """
    Actualiza una glosa existente en la base de datos.
    """
    db_glosa = db.query(models.Glosa).filter(models.Glosa.id_glosa == glosa_id).first()
    if db_glosa:
        update_data = glosa_update.model_dump(exclude_unset=True) # exclude_unset=True para actualizar solo los campos provistos
        for key, value in update_data.items():
            setattr(db_glosa, key, value)
        db_glosa.fecha_ultima_actualizacion = datetime.now(timezone.utc) # Actualizar el timestamp
        db.add(db_glosa) # O db.merge(db_glosa) en algunos casos, pero add funciona con objetos existentes
        db.commit()
        db.refresh(db_glosa)
    return db_glosa

def delete_glosa(db: Session, glosa_id: int):
    db_glosa = db.query(models.Glosa).filter(models.Glosa.id_glosa == glosa_id).first()
    if db_glosa:
        db.delete(db_glosa)
        db.commit()
    return db_glosa
    

def update_glosa(db: Session, glosa_id: int, glosa_update: schemas.GlosaUpdate):
    db_glosa = db.query(models.Glosa).filter(models.Glosa.id_glosa == glosa_id).first()
    if db_glosa:
        update_data = glosa_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_glosa, key, value)
        db.commit()
        db.refresh(db_glosa)
    return db_glosa

def delete_glosa(db: Session, glosa_id: int):
    db_glosa = db.query(models.Glosa).filter(models.Glosa.id_glosa == glosa_id).first()
    if db_glosa:
        db.delete(db_glosa)
        db.commit()
    return db_glosa

# ====================================================================
# Funciones CRUD para RespuestaGlosa
# ====================================================================

def get_respuesta_glosa(db: Session, respuesta_id: int):
    return db.query(models.RespuestaGlosa).filter(models.RespuestaGlosa.id_respuesta_glosa == respuesta_id).first()

def get_respuestas_glosa(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.RespuestaGlosa).offset(skip).limit(limit).all()

def create_respuesta_glosa(db: Session, respuesta_glosa: schemas.RespuestaGlosaCreate):
    db_respuesta_glosa = models.RespuestaGlosa(**respuesta_glosa.model_dump())
    db.add(db_respuesta_glosa)
    db.commit()
    db.refresh(db_respuesta_glosa)
    return db_respuesta_glosa

def update_respuesta_glosa(db: Session, respuesta_id: int, respuesta_update: schemas.RespuestaGlosaUpdate):
    db_respuesta = db.query(models.RespuestaGlosa).filter(models.RespuestaGlosa.id_respuesta_glosa == respuesta_id).first()
    if db_respuesta:
        update_data = respuesta_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_respuesta, key, value)
        db.commit()
        db.refresh(db_respuesta)
    return db_respuesta

def delete_respuesta_glosa(db: Session, respuesta_id: int):
    db_respuesta = db.query(models.RespuestaGlosa).filter(models.RespuestaGlosa.id_respuesta_glosa == respuesta_id).first()
    if db_respuesta:
        db.delete(db_respuesta)
        db.commit()
    return db_respuesta

# ====================================================================
# Funciones CRUD para Adjunto
# ====================================================================

def get_adjunto(db: Session, adjunto_id: int):
    return db.query(models.Adjunto).filter(models.Adjunto.id_adjunto == adjunto_id).first()

def get_adjuntos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Adjunto).offset(skip).limit(limit).all()

def create_adjunto(db: Session, adjunto: schemas.AdjuntoCreate):
    db_adjunto = models.Adjunto(**adjunto.model_dump())
    db.add(db_adjunto)
    db.commit()
    db.refresh(db_adjunto)
    return db_adjunto

def update_adjunto(db: Session, adjunto_id: int, adjunto_update: schemas.AdjuntoUpdate):
    db_adjunto = db.query(models.Adjunto).filter(models.Adjunto.id_adjunto == adjunto_id).first()
    if db_adjunto:
        update_data = adjunto_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_adjunto, key, value)
        db.commit()
        db.refresh(db_adjunto)
    return db_adjunto

def delete_adjunto(db: Session, adjunto_id: int):
    db_adjunto = db.query(models.Adjunto).filter(models.Adjunto.id_adjunto == adjunto_id).first()
    if db_adjunto:
        db.delete(db_adjunto)
        db.commit()
    return db_adjunto