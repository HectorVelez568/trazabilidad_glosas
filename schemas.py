# schemas.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal # Para DECIMAL de SQLAlchemy

# NUEVO: Esquemas para Autenticación
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None # Usamos user_id para el 'sub' del token

# Configuración base para Pydantic
class ConfigBase(BaseModel):
    class Config:
        from_attributes = True # updated from orm_mode = True # For Pydantic v2

# ====================================================================
# Esquemas para Usuario
# ====================================================================
class UsuarioBase(ConfigBase):
    nombre_completo: str
    email: EmailStr
    rol: str # Ej. 'ADMIN', 'FACTURADOR_IPS', 'AUDITOR_IPS', 'GERENTE_IPS', 'AUDITOR_EPS', 'USUARIO_EPS'
    telefono: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    password: str = Field(min_length=8) # Contraseña solo para creación

class UsuarioResponse(UsuarioBase):
    id_usuario: int
    fecha_creacion: datetime
    ultima_conexion: Optional[datetime] = None
    activo: bool

class UsuarioUpdate(ConfigBase):
    nombre_completo: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8) # Permite actualizar contraseña
    rol: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None # Permite activar/desactivar usuario

# ====================================================================
# Esquemas para Institucion
# ====================================================================
class InstitucionBase(ConfigBase):
    nit: str
    razon_social: str
    nombre_comercial: Optional[str] = None
    tipo_institucion: str # CHECK 'IPS', 'EPS'
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email_contacto: Optional[EmailStr] = None
    activo: Optional[bool] = True

class InstitucionCreate(InstitucionBase):
    pass

class InstitucionResponse(InstitucionBase):
    id_institucion: int
    fecha_registro: datetime

class InstitucionUpdate(ConfigBase):
    nit: Optional[str] = None
    razon_social: Optional[str] = None
    nombre_comercial: Optional[str] = None
    tipo_institucion: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email_contacto: Optional[EmailStr] = None
    activo: Optional[bool] = None

# ====================================================================
# Esquemas para MotivoGlosa
# ====================================================================
class MotivoGlosaBase(ConfigBase):
    codigo_motivo: str
    descripcion_motivo: str
    aplica_a: Optional[str] = None # Ej. 'Facturacion', 'Autorizacion', 'Soportes', 'Tarifas'

class MotivoGlosaCreate(MotivoGlosaBase):
    pass

class MotivoGlosaResponse(MotivoGlosaBase):
    id_motivo_glosa: int
    fecha_creacion: datetime

class MotivoGlosaUpdate(ConfigBase):
    codigo_motivo: Optional[str] = None
    descripcion_motivo: Optional[str] = None
    aplica_a: Optional[str] = None

# ====================================================================
# Esquemas para Factura
# ====================================================================
class FacturaBase(ConfigBase):
    numero_factura: str
    id_institucion_emisora: int
    id_institucion_receptora: int
    fecha_emision: date
    valor_total_factura: Decimal = Field(..., decimal_places=2) # Asegura 2 decimales
    estado_factura: str = "Emitida" # Ej. Emitida, Glosada, Pagada
    observaciones: Optional[str] = None

class FacturaCreate(FacturaBase):
    pass

class FacturaResponse(FacturaBase):
    id_factura: int

class FacturaUpdate(ConfigBase):
    numero_factura: Optional[str] = None
    id_institucion_emisora: Optional[int] = None
    id_institucion_receptora: Optional[int] = None
    fecha_emision: Optional[date] = None
    valor_total_factura: Optional[Decimal] = Field(None, decimal_places=2)
    estado_factura: Optional[str] = None
    observaciones: Optional[str] = None

# ====================================================================
# Esquemas para Glosa
# ====================================================================

# GlosaCreate: Lo que el cliente envía para crear una glosa.
# No debe incluir campos generados por la DB como id_glosa, fecha_registro_glosa, etc.
class GlosaCreate(BaseModel): # Hereda de BaseModel directamente para la entrada
    id_factura: int
    id_motivo_glosa: int
    fecha_glosa: date # Este campo debe ser 'date' y requerido para la creación.
    valor_glosado: Decimal # <-- CAMBIADO de float a Decimal
    observaciones_glosa: Optional[str] = None
    estado_glosa: Optional[str] = "Pendiente" # Si quieres que el cliente pueda enviarlo, o que tenga un default.
    usuario_responsable: Optional[int] = None
    fecha_vencimiento_respuesta: Optional[date] = None

# Glosa: ESTE ES TU ESQUEMA DE RESPUESTA.
# Es el que debe incluir TODOS los campos del modelo ORM Glosa,
# incluyendo los que la base de datos genera automáticamente.
# Esta clase es la que se usa en tu router como response_model=schemas.Glosa
class Glosa(ConfigBase): # <-- AHORA HEREDA DIRECTAMENTE DE ConfigBase
    id_glosa: int
    id_factura: int
    id_motivo_glosa: int
    fecha_glosa: date # Debe coincidir con el tipo en el ORM.
    valor_glosado: Decimal # <-- CAMBIADO de float a Decimal
    fecha_registro_glosa: Optional[datetime] = None # <--- ¡ESTE CAMPO ES VITAL! Debe ser `datetime` y NO `Optional[datetime]`
    estado_glosa: str # La base de datos siempre devuelve un valor para este campo.
    fecha_ultima_actualizacion: Optional[datetime] = None # Otro campo generado automáticamente por la DB.
    observaciones_glosa: Optional[str] = None
    usuario_responsable: Optional[int] = None
    fecha_vencimiento_respuesta: Optional[date] = None

# Eliminamos GlosaResponse ya que Glosa será el esquema de respuesta principal.
# class GlosaResponse(Glosa): # Esta clase era redundante.
#     id_glosa: int
#     fecha_registro_glosa: datetime # En el modelo es DateTime
#     fecha_ultima_actualizacion: datetime # En el modelo es DateTime
#     class Config:
#         from_attributes = True

class GlosaUpdate(ConfigBase):
    id_factura: Optional[int] = None
    id_motivo_glosa: Optional[int] = None
    fecha_glosa: Optional[date] = None
    valor_glosado: Optional[Decimal] = None # <-- CAMBIADO de float a Decimal
    observaciones_glosa: Optional[str] = None
    estado_glosa: Optional[str] = None
    usuario_responsable: Optional[int] = None
    fecha_vencimiento_respuesta: Optional[date] = None

# ====================================================================
# Esquemas para RespuestaGlosa
# ====================================================================
class RespuestaGlosaBase(ConfigBase):
    id_glosa: int
    fecha_respuesta: date # En el modelo es DateTime, pero en el schema de entrada puede ser Date
    usuario_que_responde: int
    tipo_respuesta: str # Ej. Reclamacion, Aceptacion Parcial, Anulacion
    valor_propuesto_conciliacion: Optional[Decimal] = Field(None, decimal_places=2)
    argumento_respuesta: str
    estado_posterior_glosa: str

class RespuestaGlosaCreate(RespuestaGlosaBase):
    pass

class RespuestaGlosaResponse(RespuestaGlosaBase):
    id_respuesta_glosa: int # Nombre consistente con el modelo
    fecha_respuesta: datetime # En el modelo es DateTime, la respuesta lo refleja

class RespuestaGlosaUpdate(ConfigBase):
    id_glosa: Optional[int] = None
    fecha_respuesta: Optional[date] = None # Ajusta a date o datetime según la entrada esperada
    usuario_que_responde: Optional[int] = None
    tipo_respuesta: Optional[str] = None
    valor_propuesto_conciliacion: Optional[Decimal] = Field(None, decimal_places=2)
    argumento_respuesta: Optional[str] = None
    estado_posterior_glosa: Optional[str] = None

# ====================================================================
# Esquemas para Adjunto
# ====================================================================
class AdjuntoBase(ConfigBase):
    id_glosa: Optional[int] = None
    id_respuesta_glosa: Optional[int] = None
    nombre_archivo: str
    tipo_mime: Optional[str] = None # Ej: application/pdf, image/jpeg
    ruta_almacenamiento: str # Ruta o URL donde se guarda el archivo
    tipo_documento: Optional[str] = None # Ej. PDF, JPG, HC, Autorizacion, RIPS
    usuario_que_sube: int # El usuario que sube es requerido en el modelo

class AdjuntoCreate(AdjuntoBase):
    pass

class AdjuntoResponse(AdjuntoBase):
    id_adjunto: int
    fecha_subida: datetime # En el modelo es DateTime

class AdjuntoUpdate(ConfigBase):
    id_glosa: Optional[int] = None
    id_respuesta_glosa: Optional[int] = None
    nombre_archivo: Optional[str] = None
    tipo_mime: Optional[str] = None
    ruta_almacenamiento: Optional[str] = None
    tipo_documento: Optional[str] = None
    usuario_que_sube: Optional[int] = None # Aunque en create es requerido, en update puede ser opcional