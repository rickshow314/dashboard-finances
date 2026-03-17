"""
Analytics Router - Endpoints para consultas analíticas.

Proporciona endpoints para obtener análisis e insights de datos financieros.
Usa Services que a su vez usan Repositories.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.services.transaction_service import TransactionService
from app.services.account_service import AccountService
from app.services.budget_service import BudgetService

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Analytics - Análisis Financiero"],
    responses={404: {"description": "No encontrado"}}
)


# ==================== ENDPOINTS DE TRANSACCIONES ====================

@router.get("/transactions/monthly-summary", summary="Resumen mensual")
def get_monthly_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un resumen completo del mes:
    - Total de transacciones
    - Ingresos vs Gastos
    - Top categorías
    
    Ejemplo: `/api/v1/analytics/transactions/monthly-summary?year=2025&month=11`
    """
    try:
        service = TransactionService(db)
        return service.get_monthly_summary(year, month)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions/expense-analysis", summary="Análisis de gastos")
def get_expense_analysis(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """
    Análisis detallado de gastos en un período:
    - Total gastado
    - Gastos por categoría con porcentajes
    - Tendencias
    
    Ejemplo: `/api/v1/analytics/transactions/expense-analysis?start_date=2025-11-01T00:00:00&end_date=2025-11-30T23:59:59`
    """
    try:
        service = TransactionService(db)
        return service.get_expense_analysis(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions/income-analysis", summary="Análisis de ingresos")
def get_income_analysis(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """
    Análisis detallado de ingresos en un período:
    - Total ingresado
    - Ingresos por categoría con porcentajes
    - Tendencias
    """
    try:
        service = TransactionService(db)
        return service.get_income_analysis(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== ENDPOINTS DE CUENTAS ====================

@router.get("/accounts/balance", summary="Saldos de todas las cuentas")
def get_all_balances(db: Session = Depends(get_db)):
    """
    Obtiene el saldo actual de todas las cuentas:
    - Saldo inicial
    - Ingresos totales
    - Gastos totales
    - Saldo actual
    """
    try:
        service = AccountService(db)
        return {
            "cuentas": service.get_all_balances(),
            "resumen": service.get_total_balance()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/accounts/{account_id}/balance", summary="Saldo de una cuenta")
def get_account_balance(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el saldo detallado de una cuenta específica.
    
    Ejemplo: `/api/v1/analytics/accounts/1/balance`
    """
    try:
        service = AccountService(db)
        balance = service.get_balance_for_account(account_id)
        if not balance:
            raise HTTPException(status_code=404, detail="Cuenta no encontrada")
        return balance
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/accounts/health", summary="Salud financiera")
def get_financial_health(db: Session = Depends(get_db)):
    """
    Calcula un índice de salud financiera general:
    - Saldo total consolidado
    - Número de cuentas
    - Estado: Saludable | Neutral | Crítica
    """
    try:
        service = AccountService(db)
        return service.get_financial_health()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== ENDPOINTS DE PRESUPUESTOS ====================

@router.get("/budgets/summary", summary="Resumen de presupuestos")
def get_budgets_summary(db: Session = Depends(get_db)):
    """
    Obtiene un resumen de todos los presupuestos:
    - Total de presupuestos
    - Cuántos OK, en alerta, excedidos
    - Detalles de cada uno
    """
    try:
        service = BudgetService(db)
        return service.get_all_budgets_summary()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/budgets/alerts", summary="Presupuestos que necesitan atención")
def get_budget_alerts(db: Session = Depends(get_db)):
    """
    Obtiene presupuestos que están en alerta o han sido excedidos:
    - Presupuestos en alerta (80% del límite)
    - Presupuestos excedidos
    """
    try:
        service = BudgetService(db)
        return service.get_budget_alerts()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/budgets/{budget_id}/status", summary="Estado de un presupuesto")
def get_budget_status(
    budget_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado actual de un presupuesto:
    - Monto límite vs Gasto real
    - Dinero restante
    - Porcentaje usado
    - Estado (OK, ALERTA, EXCEDIDO)
    
    Ejemplo: `/api/v1/analytics/budgets/1/status`
    """
    try:
        service = BudgetService(db)
        status = service.get_budget_status(budget_id)
        if not status:
            raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
