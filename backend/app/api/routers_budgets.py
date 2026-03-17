"""
Budget CRUD Router - Endpoints para operaciones CRUD de presupuestos.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.budget_service import BudgetService
from app.schemas.schemas import BudgetCreate, BudgetUpdate, BudgetResponse

router = APIRouter(
    prefix="/api/v1",
    tags=["CRUD - Budgets"],
    responses={404: {"description": "No encontrado"}}
)


@router.post("/budgets", response_model=dict, summary="Crear presupuesto", status_code=201)
def create_budget(
    data: BudgetCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo presupuesto.
    
    - nombre: Nombre del presupuesto
    - monto_limite: Límite de gasto
    - categoria_id: ID de la categoría
    - fecha_inicio: Cuándo inicia (opcional)
    - fecha_fin: Cuándo termina (opcional)
    """
    try:
        service = BudgetService(db)
        return service.create_budget(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/budgets", response_model=list, summary="Listar presupuestos")
def list_budgets(
    db: Session = Depends(get_db)
):
    """Obtiene lista de presupuestos con estado"""
    try:
        service = BudgetService(db)
        all_budgets_summary = service.get_all_budgets_summary()
        if isinstance(all_budgets_summary, list):
            return all_budgets_summary
        return all_budgets_summary.get("detalles", [])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/budgets/{budget_id}", response_model=dict, summary="Obtener presupuesto")
def get_budget(
    budget_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene detalles de un presupuesto"""
    try:
        service = BudgetService(db)
        budget = service.get_budget(budget_id)
        if not budget:
            raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
        return budget
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/budgets/{budget_id}", response_model=dict, summary="Actualizar presupuesto")
def update_budget(
    budget_id: int,
    data: BudgetUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza un presupuesto"""
    try:
        service = BudgetService(db)
        budget = service.update_budget(budget_id, data)
        if not budget:
            raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
        return budget
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/budgets/{budget_id}", summary="Eliminar presupuesto")
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db)
):
    """Elimina un presupuesto"""
    try:
        service = BudgetService(db)
        if not service.delete_budget(budget_id):
            raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
        return {"mensaje": "Presupuesto eliminado"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
