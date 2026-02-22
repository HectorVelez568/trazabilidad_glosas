# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, BigInteger, ForeignKey, Float, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy import Date
from datetime import datetime, date, timezone
from database import Base # Importamos Base desde nuestro nuevo módulo database
from sqlalchemy.sql import func # Para timestamps automáticos
#from sqlalchemy.ext.declarative import declarative_base / eliminada

# ====================================================================
# Usuario Model
# ====================================================================
class Usuario(Base):
    # CORREGIDO: El nombre de la tabla de Usuario debe ser consistente en singular
    __tablename__ = "usuario" 

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False)
    telefono = Column(String(20), nullable=True)
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    ultima_conexion = Column(DateTime, nullable=True)
    activo = Column(Boolean, default=True)

    glosas_creadas = relationship("Glosa", back_populates="responsable")
    respuestas_creadas = relationship("RespuestaGlosa", back_populates="respondedor")
    adjuntos_subidos = relationship("Adjunto", back_populates="uploader")

    def __repr__(self):
        return f"<Usuario(id={self.id_usuario}, email='{self.email}', rol='{self.rol}')>"


# ====================================================================
# Institucion Model
# ====================================================================
class Institucion(Base):
    __tablename__ = "institucion"
    id_institucion = Column(BigInteger, primary_key=True, index=True)
    nit = Column(String(20), unique=True, nullable=False)
    razon_social = Column(String(255), nullable=False)
    nombre_comercial = Column(String(255), nullable=True)
    tipo_institucion = Column(String(10), nullable=False) # CHECK 'IPS', 'EPS'
    direccion = Column(String(255), nullable=True)
    telefono = Column(String(50), nullable=True)
    email_contacto = Column(String(100), nullable=True)
    fecha_registro = Column(DateTime, default=datetime.now)
    activo = Column(Boolean, default=True, nullable=False)

    # Relaciones inversas (backrefs)
    facturas_emitidas = relationship("Factura", foreign_keys="Factura.id_institucion_emisora", back_populates="institucion_emisora")
    facturas_recibidas = relationship("Factura", foreign_keys="Factura.id_institucion_receptora", back_populates="institucion_receptora")


# ====================================================================
# MotivoGlosa Model
# ====================================================================
class MotivoGlosa(Base):
    __tablename__ = "motivo_glosa"
    id_motivo_glosa = Column(BigInteger, primary_key=True, index=True)
    codigo_motivo = Column(String(10), unique=True, nullable=False)
    descripcion_motivo = Column(String(255), nullable=False)
    aplica_a = Column(String(50), nullable=True) # Ej. 'Facturacion', 'Autorizacion', 'Soportes', 'Tarifas'
    fecha_creacion = Column(DateTime, default=datetime.now)

    # Relación inversa (backref)
    glosas = relationship("Glosa", back_populates="motivo_glosa_obj")


# ====================================================================
# Factura Model
# ====================================================================
class Factura(Base):
    __tablename__ = "factura"

    id_factura = Column(BigInteger, primary_key=True, index=True)
    numero_factura = Column(String(50), unique=True, nullable=False)

    id_institucion_emisora = Column(BigInteger, ForeignKey('institucion.id_institucion'), nullable=False)
    id_institucion_receptora = Column(BigInteger, ForeignKey('institucion.id_institucion'), nullable=False)

    fecha_emision = Column(Date, nullable=False)
    fecha_radicado = Column(Date, nullable=True)   # ✅ NUEVO

    nombre_eps = Column(String(150), nullable=True)  # ✅ NUEVO

    valor_total_factura = Column(DECIMAL(18,2), nullable=False)
    estado_factura = Column(String(50), nullable=False, default='Emitida')
    observaciones = Column(Text, nullable=True)

    # Relaciones
    glosas = relationship("Glosa", back_populates="factura")
    institucion_emisora = relationship("Institucion", foreign_keys=[id_institucion_emisora], back_populates="facturas_emitidas")
    institucion_receptora = relationship("Institucion", foreign_keys=[id_institucion_receptora], back_populates="facturas_recibidas")


# ====================================================================
# Glosa Model
# ====================================================================
class Glosa(Base):
    __tablename__ = "glosa" # Mantenemos 'glosa'
    id_glosa = Column(BigInteger, primary_key=True, index=True)
    id_factura = Column(BigInteger, ForeignKey('factura.id_factura'), nullable=False)
    id_motivo_glosa = Column(BigInteger, ForeignKey('motivo_glosa.id_motivo_glosa'), nullable=False)
    fecha_registro_glosa = Column(DateTime, default=datetime.now)
    fecha_glosa = Column(Date, nullable=False)
    valor_glosado = Column(DECIMAL(18,2), nullable=False)
    estado_glosa = Column(String(50), nullable=False, default='Pendiente')
    fecha_ultima_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    observaciones_glosa = Column(Text, nullable=True)
    # CORREGIDO: Apunta a 'usuario.id_usuario' si tu tabla Usuario se llama 'usuario'
    usuario_responsable = Column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True) 
    fecha_vencimiento_respuesta = Column(Date, nullable=True)

    # Relaciones - CONSOLIDADO y CORREGIDO
    factura = relationship("Factura", back_populates="glosas")
    motivo_glosa_obj = relationship("MotivoGlosa", back_populates="glosas")
    responsable = relationship("Usuario", back_populates="glosas_creadas") # Relación con Usuario
    
    # ÚNICA definición de relación para respuestas de glosa
    respuestas = relationship("RespuestaGlosa", back_populates="glosa", cascade="all, delete-orphan")
    # ÚNICA definición de relación para adjuntos
    adjuntos = relationship("Adjunto", back_populates="glosa", cascade="all, delete-orphan") 

    def __repr__(self):
        return f"<Glosa(id={self.id_glosa}, factura={self.id_factura}, estado={self.estado_glosa})>"


# ====================================================================
# RespuestaGlosa Model
# ====================================================================
class RespuestaGlosa(Base):
    __tablename__ = "respuestas_glosa"

    id_respuesta_glosa = Column(Integer, primary_key=True, index=True)
    id_glosa = Column(Integer, ForeignKey("glosa.id_glosa"), nullable=False)

    fecha_respuesta = Column(Date, default=date.today, nullable=False)
    usuario_que_responde = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)

    tipo_respuesta = Column(String(100), nullable=False)

    # 🔥 NUEVO
    valor_aceptado = Column(DECIMAL(10, 2), nullable=True)
    valor_no_aceptado = Column(DECIMAL(10, 2), nullable=True)

    argumento_respuesta = Column(Text, nullable=False)
    estado_posterior_glosa = Column(String(50), nullable=False)
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    fecha_ultima_actualizacion = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relaciones
    glosa = relationship("Glosa", back_populates="respuestas")
    respondedor = relationship("Usuario", back_populates="respuestas_creadas") # Relación con Usuario
    adjuntos = relationship("Adjunto", back_populates="respuesta_glosa", cascade="all, delete-orphan") 

    def __repr__(self):
        return f"<RespuestaGlosa(id={self.id_respuesta_glosa}, glosa_id={self.id_glosa}, tipo='{self.tipo_respuesta}')>"

# ====================================================================
# Adjunto Model (CORREGIDO)
# ====================================================================
class Adjunto(Base):
    __tablename__ = "adjuntos" # Se mantiene

    id_adjunto = Column(Integer, primary_key=True, index=True)
    # CORREGIDO: Apunta a 'glosa.id_glosa' (singular)
    id_glosa = Column(Integer, ForeignKey("glosa.id_glosa"), nullable=True) 
    id_respuesta_glosa = Column(Integer, ForeignKey("respuestas_glosa.id_respuesta_glosa"), nullable=True)
    nombre_archivo = Column(String(255), nullable=False)
    tipo_mime = Column(String(100), nullable=True)
    ruta_almacenamiento = Column(String(500), nullable=False)
    tipo_documento = Column(String(100), nullable=True)
    # CORREGIDO: Apunta a 'usuario.id_usuario' (singular)
    usuario_que_sube = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False) 
    fecha_subida = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relaciones
    glosa = relationship("Glosa", back_populates="adjuntos")
    respuesta_glosa = relationship("RespuestaGlosa", back_populates="adjuntos")
    uploader = relationship("Usuario", back_populates="adjuntos_subidos")

    def __repr__(self):
        return f"<Adjunto(id={self.id_adjunto}, nombre='{self.nombre_archivo}', glosa_id={self.id_glosa}, respuesta_id={self.id_respuesta_glosa})>"

