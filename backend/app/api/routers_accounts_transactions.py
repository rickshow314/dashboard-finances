"""
Account & Transaction CRUD Routers - Endpoints para operaciones CRUD básicas.

Proporciona endpoints para crear, leer, actualizar y eliminar cuentas y transacciones.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.services.account_service import AccountService
from app.services.transaction_service import TransactionService
from app.schemas.schemas import (
    AccountCreate, AccountUpdate, AccountResponse,
    TransactionCreate, TransactionUpdate, TransactionResponse
)

router = APIRouter(
    prefix="/api/v1",
    tags=["CRUD - Accounts & Transactions"],
    responses={404: {"description": "No encontrado"}}
)


# ==================== CUENTAS ====================

@router.post("/accounts", response_model=dict, summary="Crear cuenta", status_code=201)
def create_account(
    data: AccountCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva cuenta financiera.
    
    - nombre: Nombre de la cuenta (ej: "Mi Tarjeta Crédito")
    - tipo: "efectivo", "tarjeta", "broker", "ahorro", "otro"
    - moneda: "USD", "EUR", "MXN", "ARS", "OTHER"
    - saldo_inicial: Dinero inicial (opcional)
    """
    try:
        service = AccountService(db)
        return service.create_account(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/accounts", response_model=list, summary="Listar cuentas")
def list_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtiene lista de todas las cuentas"""
    try:
        service = AccountService(db)
        return service.get_all_accounts(skip, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/accounts/{account_id}", response_model=dict, summary="Obtener cuenta")
def get_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene detalles completos de una cuenta incluyendo saldo"""
    try:
        service = AccountService(db)
        account = service.get_account(account_id)
        
        if not account:
            raise HTTPException(status_code=404, detail="Cuenta no encontrada")
        
        return account
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/accounts/{account_id}", response_model=dict, summary="Actualizar cuenta")
def update_account(
    account_id: int,
    data: AccountUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza datos de una cuenta"""
    try:
        service = AccountService(db)
        account = service.update_account(account_id, data)
        if not account:
            raise HTTPException(status_code=404, detail="Cuenta no encontrada")
        return account
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/accounts/{account_id}", summary="Eliminar cuenta")
def delete_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """Elimina una cuenta y todas sus transacciones asociadas"""
    try:
        service = AccountService(db)
        if not service.delete_account(account_id):
            raise HTTPException(status_code=404, detail="Cuenta no encontrada")
        return {"mensaje": "Cuenta eliminada"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== TRANSACCIONES ====================

@router.post("/transactions", response_model=dict, summary="Crear transacción", status_code=201)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva transacción (ingreso/gasto).
    
    - fecha: Fecha de la transacción
    - cantidad: Monto (debe ser positivo)
    - descripcion: Detalles de la transacción
    - tipo: "ingreso" o "gasto"
    - account_id: ID de la cuenta
    - categoria_id: ID de la categoría
    """
    try:
        service = TransactionService(db)
        return service.create_transaction(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions", response_model=list, summary="Listar transacciones")
def list_transactions(
    account_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtiene lista de transacciones"""
    try:
        service = TransactionService(db)
        return service.get_all_transactions(skip, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions/{transaction_id}", response_model=dict, summary="Obtener transacción")
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene detalles de una transacción específica"""
    try:
        service = TransactionService(db)
        transaction = service.get_transaction(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/transactions/{transaction_id}", response_model=dict, summary="Actualizar transacción")
def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza una transacción"""
    try:
        service = TransactionService(db)
        transaction = service.update_transaction(transaction_id, data)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/transactions/{transaction_id}", summary="Eliminar transacción")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """Elimina una transacción"""
    try:
        service = TransactionService(db)
        if not service.delete_transaction(transaction_id):
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        return {"mensaje": "Transacción eliminada"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
