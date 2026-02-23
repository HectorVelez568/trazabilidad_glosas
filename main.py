from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
import io
import os
from datetime import date, timedelta

# DB
from database import engine, Base, SessionLocal

# MODELOS (IMPORTANTE)
import models

# ROUTERS
from routers import auth
from routers import usuarios
from routers import instituciones
from routers import motivos_glosa
from routers import facturas
from routers import glosas
from routers import respuestas_glosa
from routers import adjuntos

# =========================
# CREAR TABLAS
# =========================
print("\n--- Tablas registradas ---")
for table in Base.metadata.tables:
    print("-", table)
print("--------------------------\n")

Base.metadata.create_all(bind=engine)

# =========================
# APP
# =========================
app = FastAPI(
    title="API de Trazabilidad de Glosas",
    version="1.0"
)

# =========================
# STATIC (SEGURO)
# =========================
if os.path.exists("static"):
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"message": "API funcionando correctamente 🚀"}

@app.get("/api/health")
def health():
    return {"status": "ok"}

# =========================
# ROUTERS
# =========================
app.include_router(auth.router)
app.include_router(usuarios.router, prefix="/users")
app.include_router(instituciones.router, prefix="/instituciones")
app.include_router(motivos_glosa.router, prefix="/motivos-glosa")
app.include_router(facturas.router, prefix="/facturas")
app.include_router(glosas.router, prefix="/glosas")
app.include_router(respuestas_glosa.router, prefix="/respuestas-glosa")
app.include_router(adjuntos.router, prefix="/adjuntos")

# =========================
# SEMÁFORO
# =========================
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

# =========================
# DASHBOARD
# =========================
@app.get("/dashboard")
def dashboard(request: Request):
    db: Session = SessionLocal()

    hoy = date.today()
    limite = hoy + timedelta(days=5)

    total_facturas = db.query(models.Factura).count()
    total_glosas = db.query(models.Glosa).count()

    glosas_vencidas = db.query(models.Glosa).filter(
        models.Glosa.fecha_vencimiento_respuesta < hoy,
        models.Glosa.estado_glosa != "Respondida"
    ).all()

    glosas_por_vencer = db.query(models.Glosa).filter(
        models.Glosa.fecha_vencimiento_respuesta <= limite,
        models.Glosa.fecha_vencimiento_respuesta >= hoy,
        models.Glosa.estado_glosa != "Respondida"
    ).all()

    db.close()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_facturas": total_facturas,
        "total_glosas": total_glosas,
        "vencidas": glosas_vencidas,
        "por_vencer": glosas_por_vencer
    })

# =========================
# VER GLOSAS
# =========================
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
            "motivo": motivo,
            "color": calcular_semaforo(g)
        })

    db.close()

    return templates.TemplateResponse("glosas.html", {
        "request": request,
        "data": data
    })

# =========================
# ACTUALIZAR ESTADO
# =========================
@app.post("/actualizar-estado-glosa/{id}")
def actualizar_estado(id: int, estado: str = Form(...)):
    db: Session = SessionLocal()

    glosa = db.query(models.Glosa).filter(
        models.Glosa.id_glosa == id
    ).first()

    if glosa:
        glosa.estado_glosa = estado
        db.commit()

    db.close()

    return RedirectResponse("/glosas-view", status_code=303)

# =========================
# IMPORTAR FACTURAS
# =========================
@app.post("/importar-facturas")
async def importar_facturas(file: UploadFile = File(...)):
    db: Session = SessionLocal()

    try:
        df = pd.read_excel(file.file)
        df.columns = df.columns.str.strip().str.lower()

        for _, row in df.iterrows():
            factura = models.Factura(
                numero_factura=str(row.get("numero_factura")),
                nombre_eps=str(row.get("nombre_eps")),
                valor_total_factura=float(row.get("valor_total")),
                estado_factura="Radicada"
            )
            db.add(factura)

        db.commit()
        return {"mensaje": "Facturas cargadas"}

    except Exception as e:
        db.rollback()
        return {"error": str(e)}

    finally:
        db.close()

# =========================
# REPORTE
# =========================
@app.get("/reporte-facturas")
def reporte():
    db: Session = SessionLocal()

    try:
        data = []

        facturas = db.query(models.Factura).all()

        for f in facturas:
            data.append({
                "Factura": f.numero_factura,
                "Valor": float(f.valor_total_factura)
            })

        df = pd.DataFrame(data)

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)

        output.seek(0)

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=reporte.xlsx"}
        )

    finally:
        db.close()