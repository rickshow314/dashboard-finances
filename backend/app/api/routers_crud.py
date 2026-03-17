"""
CRUD Routers - Endpoints para operaciones Create, Read, Update, Delete.

Proporciona endpoints CRUD estándar para todas las entidades.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services.category_service import CategoryService
from app.services.recurring_service import RecurringService
from app.services.goal_service import FinancialGoalService
from app.schemas.schemas import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    RecurringCreate, RecurringUpdate, RecurringResponse,
    FinancialGoalCreate, FinancialGoalUpdate, FinancialGoalResponse
)

router = APIRouter(
    prefix="/api/v1",
    tags=["CRUD Operations"],
    responses={404: {"description": "No encontrado"}}
)


# ==================== CATEGORÍAS ====================

@router.post("/categories", response_model=dict, summary="Crear categoría", status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db)
):
    """Crea una nueva categoría de gastos/ingresos"""
    try:
        service = CategoryService(db)
        return service.create_category(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/categories", response_model=list, summary="Listar categorías")
def list_categories(
    type: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene lista de categorías.
    
    Parámetros:
    - type: "ingreso" o "gasto" (opcional)
    - skip: Saltar registros
    - limit: Límite de registros
    """
    try:
        service = CategoryService(db)
        
        if type == "gasto":
            return service.get_expense_categories()
        elif type == "ingreso":
            return service.get_income_categories()
        else:
            return service.get_all_categories(skip, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/categories/{category_id}", response_model=dict, summary="Obtener categoría")
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene detalles de una categoría específica"""
    try:
        service = CategoryService(db)
        category = service.get_category(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/categories/{category_id}", response_model=dict, summary="Actualizar categoría")
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza una categoría"""
    try:
        service = CategoryService(db)
        category = service.update_category(category_id, data)
        if not category:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/categories/{category_id}", summary="Eliminar categoría")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Elimina una categoría"""
    try:
        service = CategoryService(db)
        if not service.delete_category(category_id):
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return {"mensaje": "Categoría eliminada"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== RECURRENTES ====================

@router.post("/recurring", response_model=dict, summary="Crear recurrente", status_code=201)
def create_recurring(
    data: RecurringCreate,
    db: Session = Depends(get_db)
):
    """Crea un nuevo gasto/ingreso recurrente"""
    try:
        service = RecurringService(db)
        return service.create_recurring(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recurring", response_model=list, summary="Listar recurrentes")
def list_recurring(
    db: Session = Depends(get_db)
):
    """Obtiene resumen de gastos/ingresos recurrentes"""
    try:
        service = RecurringService(db)
        return service.get_all_recurring(limit=1000)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recurring/{recurring_id}", response_model=dict, summary="Obtener recurrente")
def get_recurring(
    recurring_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene detalles de un recurrente"""
    try:
        service = RecurringService(db)
        recurring = service.get_recurring(recurring_id)
        if not recurring:
            raise HTTPException(status_code=404, detail="Recurrente no encontrado")
        return recurring
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/recurring/{recurring_id}", response_model=dict, summary="Actualizar recurrente")
def update_recurring(
    recurring_id: int,
    data: RecurringUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza un recurrente"""
    try:
        service = RecurringService(db)
        recurring = service.update_recurring(recurring_id, data)
        if not recurring:
            raise HTTPException(status_code=404, detail="Recurrente no encontrado")
        return recurring
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/recurring/{recurring_id}", summary="Eliminar recurrente")
def delete_recurring(
    recurring_id: int,
    db: Session = Depends(get_db)
):
    """Elimina un recurrente"""
    try:
        service = RecurringService(db)
        if not service.delete_recurring(recurring_id):
            raise HTTPException(status_code=404, detail="Recurrente no encontrado")
        return {"mensaje": "Recurrente eliminado"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recurring/projection/monthly", summary="Proyección mensual")
def get_monthly_projection(
    db: Session = Depends(get_db)
):
    """Obtiene la proyección de ingresos/gastos del próximo mes"""
    try:
        service = RecurringService(db)
        return service.get_monthly_projection()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recurring/alerts/expiring", summary="Recurrentes a punto de vencer")
def get_expiring_recurring(
    db: Session = Depends(get_db)
):
    """Obtiene recurrentes próximos a vencer"""
    try:
        service = RecurringService(db)
        return service.get_soon_to_expire_alert()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== OBJETIVOS FINANCIEROS ====================

@router.post("/goals", response_model=dict, summary="Crear objetivo", status_code=201)
def create_goal(
    data: FinancialGoalCreate,
    db: Session = Depends(get_db)
):
    """Crea un nuevo objetivo de ahorro"""
    try:
        service = FinancialGoalService(db)
        return service.create_goal(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/goals", response_model=list, summary="Listar objetivos")
def list_goals(
    db: Session = Depends(get_db)
):
    """Obtiene dashboard completo de objetivos"""
    try:
        service = FinancialGoalService(db)
        return service.get_all_goals(limit=1000)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/goals/{goal_id}", response_model=dict, summary="Obtener objetivo")
def get_goal(
    goal_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene detalles de un objetivo"""
    try:
        service = FinancialGoalService(db)
        goal = service.get_goal(goal_id)
        if not goal:
            raise HTTPException(status_code=404, detail="Objetivo no encontrado")
        return goal
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/goals/{goal_id}", response_model=dict, summary="Actualizar objetivo")
def update_goal(
    goal_id: int,
    data: FinancialGoalUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza un objetivo"""
    try:
        service = FinancialGoalService(db)
        goal = service.update_goal(goal_id, data)
        if not goal:
            raise HTTPException(status_code=404, detail="Objetivo no encontrado")
        return goal
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/goals/{goal_id}", summary="Eliminar objetivo")
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db)
):
    """Elimina un objetivo"""
    try:
        service = FinancialGoalService(db)
        if not service.delete_goal(goal_id):
            raise HTTPException(status_code=404, detail="Objetivo no encontrado")
        return {"mensaje": "Objetivo eliminado"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/goals/{goal_id}/save", summary="Agregar ahorros a objetivo")
def add_goal_savings(
    goal_id: int,
    amount: float,
    db: Session = Depends(get_db)
):
    """Añade dinero ahorrado a un objetivo"""
    try:
        if amount <= 0:
            raise HTTPException(status_code=400, detail="El monto debe ser positivo")
        
        service = FinancialGoalService(db)
        goal = service.update_goal_progress(goal_id, amount)
        
        if not goal:
            raise HTTPException(status_code=404, detail="Objetivo no encontrado")
        
        return {
            "mensaje": "Ahorros actualizado",
            "objetivo": goal
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/goals/by-priority/all", summary="Objetivos por prioridad")
def get_goals_by_priority(
    db: Session = Depends(get_db)
):
    """Obtiene objetivos agrupados por prioridad"""
    try:
        service = FinancialGoalService(db)
        return service.get_goals_by_priority()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
