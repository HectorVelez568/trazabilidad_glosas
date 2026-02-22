import psycopg2
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "admin123"
password_hash = pwd_context.hash(password)

conn = psycopg2.connect(
    host="localhost",
    database="trazabilidad_glosas",
    user="postgres",
    password="postgres"
)

cur = conn.cursor()

cur.execute("""
INSERT INTO usuario (
    nombre_completo,
    email,
    password_hash,
    rol,
    telefono,
    fecha_creacion,
    activo
)
VALUES (%s,%s,%s,%s,%s,NOW(),true)
""",(
    "Administrador",
    "admin@localhost.com",
    password_hash,
    "admin",
    "3000000000"
))

conn.commit()

print("Usuario creado correctamente")

cur.close()
conn.close()