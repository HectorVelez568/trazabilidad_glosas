# routers/facturas.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db_session
import schemas
import crud

router = APIRouter()

# Dependency para obtener la sesión de la base de datos
#def get_db_session():
#    db = get_db()
#    try:
#        yield db
#    finally:
#        db.close()

# ====================================================================
# Rutas para Factura
# ====================================================================

@router.post("/", response_model=schemas.FacturaResponse, status_code=status.HTTP_201_CREATED)
def create_factura(factura: schemas.FacturaCreate, db: Session = Depends(get_db_session)):
    db_factura = crud.get_factura_by_numero(db, numero_factura=factura.numero_factura)
    if db_factura:
        raise HTTPException(status_code=400, detail="El número de factura ya está registrado")
    
    # Opcional: Validar que las instituciones emisora y receptora existan
    db_institucion_emisora = crud.get_institucion(db, factura.id_institucion_emisora)
    if not db_institucion_emisora:
        raise HTTPException(status_code=404, detail="Institución emisora no encontrada")
    
    db_institucion_receptora = crud.get_institucion(db, factura.id_institucion_receptora)
    if not db_institucion_receptora:
        raise HTTPException(status_code=404, detail="Institución receptora no encontrada")

    return crud.create_factura(db=db, factura=factura)

@router.get("/{factura_id}", response_model=schemas.FacturaResponse)
def read_factura(factura_id: int, db: Session = Depends(get_db_session)):
    db_factura = crud.get_factura(db, factura_id=factura_id)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return db_factura

@router.get("/", response_model=List[schemas.FacturaResponse])
def read_facturas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    facturas = crud.get_facturas(db, skip=skip, limit=limit)
    return facturas

@router.put("/{factura_id}", response_model=schemas.FacturaResponse)
def update_factura_route(factura_id: int, factura_update: schemas.FacturaUpdate, db: Session = Depends(get_db_session)):
    # Opcional: Validar que las instituciones emisora y receptora existan si se actualizan
    if factura_update.id_institucion_emisora:
        db_institucion_emisora = crud.get_institucion(db, factura_update.id_institucion_emisora)
        if not db_institucion_emisora:
            raise HTTPException(status_code=404, detail="Nueva institución emisora no encontrada")
    
    if factura_update.id_institucion_receptora:
        db_institucion_receptora = crud.get_institucion(db, factura_update.id_institucion_receptora)
        if not db_institucion_receptora:
            raise HTTPException(status_code=404, detail="Nueva institución receptora no encontrada")

    db_factura = crud.update_factura(db, factura_id=factura_id, factura_update=factura_update)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return db_factura

@router.delete("/{factura_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_factura_route(factura_id: int, db: Session = Depends(get_db_session)):
    db_factura = crud.delete_factura(db, factura_id=factura_id)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return {} # Devuelve una respuesta vacía para 204 No Content