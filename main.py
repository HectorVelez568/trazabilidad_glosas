# C:\trazabilidad_glosas_api\main.py
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi import Form
from fastapi import UploadFile, File
import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from datetime import date, timedelta

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Importa engine y Base de database.py
from database import engine, Base

# Importa el módulo models completo. Esto es VITAL para registrar tus clases ORM con Base.metadata.
import models
from fastapi.responses import RedirectResponse


# Importa todos tus routers individualmente para incluirlos en la app
from routers import auth
from routers import usuarios # Usualmente llamado 'users' en lugar de 'usuarios'
from routers import instituciones
from routers import motivos_glosa
from routers import facturas
from routers import glosas
from routers import respuestas_glosa # NUEVO router para respuestas
from routers import adjuntos # NUEVO router para adjuntos

from sqlalchemy.orm import Session
from database import SessionLocal
import models
from fastapi import Request



# --- CREACIÓN DE TABLAS DE LA BASE DE DATOS ---
# Esta línea DEBE ejecutarse DESPUÉS de que el módulo 'models' ha sido importado.
# Es la que le dice a SQLAlchemy que cree las tablas en la base de datos
# si no existen, basándose en las definiciones de tus clases en models.py.
# --- CREACIÓN DE TABLAS DE LA BASE DE DATOS ---
print("\n--- Tablas registradas con Base.metadata antes de la creación ---")
for table_name, table_obj in Base.metadata.tables.items():
    print(f"- {table_name}")
print("----------------------------------------------------------\n")

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="API de Trazabilidad de Glosas",
    description="API REST para la gestión y trazabilidad de glosas médico-hospitalarias.",
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

from datetime import date

# ================= SEMÁFORO DE ALERTAS =================
def calcular_semaforo(glosa):
    hoy = date.today()

    if not glosa.fecha_vencimiento_respuesta:
        return "secondary"

    if glosa.estado_glosa == "Respondida":
        return "success"

    if glosa.fecha_vencimiento_respuesta < hoy:
        return "danger"

    if (glosa.fecha_vencimiento_respuesta - hoy).days <= 5:
        return "warning"

    return "success"

# --- CONFIGURACIÓN CORS ---
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    # Agrega la IP específica de tu máquina si el frontend se abre desde otra IP
    "http://192.168.1.24",     # Ejemplo si accedes solo por IP
    "http://192.168.1.24:5500", # Ejemplo si usas Live Server en esa IP
    "http://192.168.1.24:8000", # Ejemplo si FastAPI está en esa IP y el frontend también
    # Si vas a abrir el archivo HTML directamente en el navegador,
    # la 'origin' puede ser 'null' o 'file://'.
    # Para desarrollo, puedes permitir todas las origenes (NO PARA PRODUCCIÓN):
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Lista de orígenes permitidos
    allow_credentials=True,      # Permite el envío de cookies y credenciales
    allow_methods=["*"],         # Permite todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],         # Permite todos los encabezados
)


# --- RUTAS DE BIENVENIDA Y HEALTH CHECK ---
@app.get("/")
async def read_root():
    """Ruta de bienvenida para la API."""
    return {"message": "¡Bienvenido a la API de Trazabilidad de Glosas!"}

@app.get("/api/health")
async def read_api_health():
    """Endpoint para verificar el estado de salud de la API."""
    return {"status": "ok", "message": "API de Trazabilidad de Glosas funcionando"}


# --- INCLUSIÓN DE ROUTERS DE LA API ---
# Es buena práctica añadir el prefix y tags para una mejor organización en la documentación (Swagger UI)
app.include_router(auth.router, tags=["Autenticación"]) # Sin prefijo si el endpoint /token va en la raíz
app.include_router(usuarios.router, prefix="/users", tags=["Usuarios"]) # Asumo 'users' por convención
app.include_router(instituciones.router, prefix="/instituciones", tags=["Instituciones"])
app.include_router(motivos_glosa.router, prefix="/motivos-glosa", tags=["Motivos de Glosa"])
app.include_router(facturas.router, prefix="/facturas", tags=["Facturas"])
app.include_router(glosas.router, prefix="/glosas", tags=["Glosas"])
app.include_router(respuestas_glosa.router, prefix="/respuestas-glosa", tags=["Respuestas de Glosa"])
app.include_router(adjuntos.router, prefix="/adjuntos", tags=["Adjuntos"])

@app.get("/dashboard")
def dashboard(request: Request):
    db: Session = SessionLocal()

    hoy = date.today()
    limite = hoy + timedelta(days=5)

    total_facturas = db.query(models.Factura).count()
    total_glosas = db.query(models.Glosa).count()

    # 🚨 ALERTAS
    glosas_vencidas = db.query(models.Glosa).filter(
        models.Glosa.fecha_vencimiento_respuesta < hoy,
        models.Glosa.estado_glosa != "Respondida"
    ).all()

    glosas_por_vencer = db.query(models.Glosa).filter(
        models.Glosa.fecha_vencimiento_respuesta <= limite,
        models.Glosa.fecha_vencimiento_respuesta >= hoy,
        models.Glosa.estado_glosa != "Respondida"
    ).all()

    glosas_sin_respuesta = db.query(models.Glosa).filter(
        models.Glosa.estado_glosa == "Pendiente"
    ).all()

    glosas_alto_valor = db.query(models.Glosa).filter(
        models.Glosa.valor_glosado > 1000000
    ).all()

    db.close()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total_facturas": total_facturas,
            "total_glosas": total_glosas,
            "vencidas": glosas_vencidas,
            "por_vencer": glosas_por_vencer,
            "sin_respuesta": glosas_sin_respuesta,
            "alto_valor": glosas_alto_valor
        }
    )
@app.get("/glosas-view")
def ver_glosas(request: Request):
    db: Session = SessionLocal()

    glosas = db.query(models.Glosa).all()

    data = []
    for g in glosas:

        factura = db.query(models.Factura).filter(
            models.Factura.id_factura == g.id_factura
        ).first()

        motivo = db.query(models.MotivoGlosa).filter(
            models.MotivoGlosa.id_motivo_glosa == g.id_motivo_glosa
        ).first()

        data.append({
            "glosa": g,
            "factura": factura,
            "motivo": motivo,   # 🔥 NUEVO
            "color": calcular_semaforo(g)
        })

    db.close()

    return templates.TemplateResponse(
        "glosas.html",
        {
            "request": request,
            "data": data
        }
    )

@app.post("/actualizar-estado-glosa/{id}")
async def actualizar_estado_glosa(id: int, estado: str = Form(...)):
    db: Session = SessionLocal()

    try:
        glosa = db.query(models.Glosa).filter(
            models.Glosa.id_glosa == id
        ).first()

        if glosa:
            glosa.estado_glosa = estado
            db.commit()

    finally:
        db.close()

    return RedirectResponse(url="/glosas-view", status_code=303)

@app.get("/glosa/{glosa_id}")
def detalle_glosa(glosa_id: int, request: Request):
    db: Session = SessionLocal()

    glosa = db.query(models.Glosa).filter(
        models.Glosa.id_glosa == glosa_id
    ).first()

    respuestas = db.query(models.RespuestaGlosa).filter(
        models.RespuestaGlosa.id_glosa == glosa_id
    ).order_by(models.RespuestaGlosa.fecha_creacion.desc()).all()

    db.close()

    return templates.TemplateResponse(
        "detalle_glosa.html",
        {
            "request": request,
            "glosa": glosa,
            "respuestas": respuestas
        }
    )

@app.post("/glosa/{glosa_id}")
def responder_glosa(
    glosa_id: int,
    request: Request,
    respuesta: str = Form(...),
    valor_aceptado: float = Form(...),       # 🔥 NUEVO
    valor_no_aceptado: float = Form(...)     # 🔥 NUEVO
):
    db: Session = SessionLocal()

    glosa = db.query(models.Glosa).filter(
        models.Glosa.id_glosa == glosa_id
    ).first()

    # 🔥 VALIDACIÓN
    if (valor_aceptado + valor_no_aceptado) != float(glosa.valor_glosado):
        db.close()
        return {"error": "La suma no coincide con el valor glosado"}

    nueva_respuesta = models.RespuestaGlosa(
        id_glosa=glosa_id,
        usuario_que_responde=1,
        tipo_respuesta="Respuesta IPS",
        argumento_respuesta=respuesta,
        estado_posterior_glosa="Respondida",
        valor_aceptado=valor_aceptado,
        valor_no_aceptado=valor_no_aceptado
    )

    glosa.estado_glosa = "Respondida"

    db.add(nueva_respuesta)
    db.commit()
    db.close()

    return RedirectResponse(url=f"/glosa/{glosa_id}", status_code=303)



@app.get("/importar-facturas-view")
def vista_importar_facturas(request: Request):
    return templates.TemplateResponse(
        "importar_facturas.html",
        {"request": request}
    )


@app.post("/importar-facturas")
async def importar_facturas(file: UploadFile = File(...)):
    db: Session = SessionLocal()

    try:
        df = pd.read_excel(file.file)

        # Limpiar columnas
        df.columns = df.columns.str.strip().str.lower()

        registros_creados = 0

        for _, row in df.iterrows():

            # =========================
            # 🔥 MAPEO NIT → ID REAL
            # =========================
            nit_emisora = str(row.get("id_emisora")).strip()
            nit_receptora = str(row.get("id_receptora")).strip()

            inst_emisora = db.query(models.Institucion).filter(
                models.Institucion.nit == nit_emisora
            ).first()

            inst_receptora = db.query(models.Institucion).filter(
                models.Institucion.nit == nit_receptora
            ).first()

            if not inst_emisora:
                print(f"❌ No existe emisora: {nit_emisora}")
                continue

            if not inst_receptora:
                print(f"❌ No existe receptora: {nit_receptora}")
                continue

            # =========================
            # CREAR FACTURA
            # =========================
            factura = models.Factura(
                numero_factura=str(row.get("numero_factura")),
                id_institucion_emisora=inst_emisora.id_institucion,
                id_institucion_receptora=inst_receptora.id_institucion,
                fecha_emision=row.get("fecha_emision"),
                fecha_radicado=row.get("fecha_radicado"),
                nombre_eps=str(row.get("nombre_eps")),
                valor_total_factura=float(row.get("valor_total")),
                estado_factura="Radicada"
            )

            db.add(factura)
            registros_creados += 1

        db.commit()
        db.close()

        return {"mensaje": f"{registros_creados} facturas importadas correctamente"}

    except Exception as e:
        db.rollback()
        db.close()
        return {"error": str(e)}

@app.post("/importar-glosas")
async def importar_glosas(file: UploadFile = File(...)):
    db: Session = SessionLocal()

    try:
        df = pd.read_excel(file.file)
        df.columns = df.columns.str.strip().str.lower()

        insertadas = 0
        facturas_no = []
        motivos_no = []
        errores = []

        for i, row in df.iterrows():
            try:
                numero = str(row["numero_factura"]).strip()
                codigo = str(row["codigo_motivo"]).strip()

                # limpiar .0 de Excel
                if ".0" in numero:
                    numero = numero.replace(".0", "")

                # ================= FACTURA =================
                factura = db.query(models.Factura).filter(
                    models.Factura.numero_factura == numero
                ).first()

                if not factura:
                    facturas_no.append(numero)
                    continue

                # ================= MOTIVO =================
                motivo = db.query(models.MotivoGlosa).filter(
                    models.MotivoGlosa.codigo_motivo == codigo
                ).first()

                if not motivo:
                    motivos_no.append(codigo)
                    continue

                # ================= VALIDAR DUPLICADO =================
                existe = db.query(models.Glosa).filter(
                    models.Glosa.id_factura == factura.id_factura,
                    models.Glosa.id_motivo_glosa == motivo.id_motivo_glosa,
                    models.Glosa.valor_glosado == float(row["valor_glosado"])
                ).first()

                if existe:
                    continue

                # ================= CREAR GLOSA =================
                glosa = models.Glosa(
                    id_factura=factura.id_factura,
                    id_motivo_glosa=motivo.id_motivo_glosa,
                    fecha_glosa=row["fecha_glosa"],
                    valor_glosado=float(row["valor_glosado"]),
                    estado_glosa="Pendiente",
                    observaciones_glosa=str(row.get("observacion", ""))
                )

                db.add(glosa)
                insertadas += 1

            except Exception as e:
                errores.append({
                    "fila": int(i),
                    "error": str(e)
                })

        db.commit()
        db.close()

        return {
            "insertadas": insertadas,
            "facturas_no_encontradas": list(set(facturas_no)),
            "motivos_no_encontrados": list(set(motivos_no)),
            "errores": errores
        }

    except Exception as e:
        db.rollback()
        db.close()
        return {"error": str(e)}

@app.get("/importar-glosas-view")
def vista_importar_glosas(request: Request):
    return templates.TemplateResponse(
        "importar_glosas.html",
        {"request": request}
    )    

from fastapi.responses import StreamingResponse
import io

from fastapi.responses import StreamingResponse
import io

@app.get("/reporte-facturas")
def reporte_facturas():
    db: Session = SessionLocal()

    try:
        data = []

        facturas = db.query(models.Factura).all()

        for f in facturas:
            for g in f.glosas:
                for r in g.respuestas:

                    data.append({
                        "Factura": f.numero_factura,
                        "Fecha Emisión": f.fecha_emision,
                        "EPS": f.nombre_eps,
                        "Valor Factura": float(f.valor_total_factura),
                        "Valor Glosado": float(g.valor_glosado),
                        "Valor Aceptado": float(r.valor_aceptado or 0),
                        "Valor No Aceptado": float(r.valor_no_aceptado or 0),
                        "Estado Glosa": g.estado_glosa,
                        "Estado Respuesta": r.estado_posterior_glosa,
                        "Fecha Respuesta": r.fecha_creacion,
                    })

        df = pd.DataFrame(data)

        # ===============================
        # 📊 RESUMEN GERENCIAL
        # ===============================
        resumen = df.groupby("EPS").agg({
            "Valor Factura": "sum",
            "Valor Glosado": "sum",
            "Valor Aceptado": "sum",
            "Valor No Aceptado": "sum"
        }).reset_index()

        resumen["% Recuperado"] = (
            resumen["Valor Aceptado"] / resumen["Valor Glosado"] * 100
        ).round(2)

        # ===============================
        # 📁 GENERAR EXCEL
        # ===============================
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Detalle")
            resumen.to_excel(writer, index=False, sheet_name="Resumen")

        output.seek(0)

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=reporte_glosas.xlsx"}
        )

    except Exception as e:
        return {"error": str(e)}

    finally:
        db.close()



# --- SERVIR ARCHIVOS ESTÁTICOS (FRONTEND) ---
# Esta ruta debe ser la ÚLTIMA para no interceptar las rutas de la API.
app.mount("/", StaticFiles(directory="static", html=True), name="static")