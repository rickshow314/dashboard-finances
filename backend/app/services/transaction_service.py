"""
Transaction Service - Lógica de negocio para transacciones.

Orquesta operaciones entre repositorios y aplica reglas de negocio.
"""

from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.repositories.transaction_repository import TransactionRepository
from app.schemas.schemas import TransactionCreate, TransactionUpdate, TransactionResponse


class TransactionService:
    """Servicio para operaciones con transacciones"""
    
    def __init__(self, db: Session):
        self.db = db
        self._transaction_repo = TransactionRepository(db)
    
    def create_transaction(self, data: TransactionCreate) -> Dict:
        """
        Crea una nueva transacción con validaciones.
        
        Args:
            data: Schema con datos de la transacción
        
        Returns:
            Transacción creada
        """
        transaction_dict = data.dict()
        transaction = self._transaction_repo.create(transaction_dict)
        
        return {
            "id": transaction.id,
            "fecha": transaction.fecha,
            "cantidad": transaction.cantidad,
            "descripcion": transaction.descripcion,
            "tipo": transaction.tipo.value,
            "account_id": transaction.account_id,
            "categoria_id": transaction.categoria_id,
            "created_at": transaction.created_at
        }

    # Backwards-compatible wrapper expected by tests
    def create(self, transaction_obj):
        if hasattr(transaction_obj, 'dict'):
            data = transaction_obj.dict()
        elif isinstance(transaction_obj, dict):
            data = transaction_obj
        else:
            data = {
                "fecha": getattr(transaction_obj, 'fecha', None),
                "cantidad": getattr(transaction_obj, 'cantidad', None),
                "descripcion": getattr(transaction_obj, 'descripcion', None),
                "tipo": getattr(transaction_obj, 'tipo', None),
                "account_id": getattr(transaction_obj, 'account_id', None),
                "categoria_id": getattr(transaction_obj, 'categoria_id', None)
            }

        transaction = self._transaction_repo.create(data)
        return transaction
    
    def get_transaction(self, transaction_id: int) -> Optional[Dict]:
        """Obtiene una transacción por ID"""
        transaction = self._transaction_repo.get_by_id(transaction_id)
        if transaction:
            return TransactionResponse.from_orm(transaction).dict()
        return None
    
    def get_all_transactions(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Obtiene todas las transacciones formateadas"""
        transactions = self._transaction_repo.get_all(skip, limit)
        return [
            {
                "id": t.id,
                "fecha": t.fecha,
                "cantidad": float(t.cantidad),
                "descripcion": t.descripcion,
                "tipo": t.tipo.value if hasattr(t.tipo, 'value') else str(t.tipo),
                "account_id": t.account_id,
                "categoria_id": t.categoria_id,
                "created_at": t.created_at,
                "updated_at": t.updated_at
            }
            for t in transactions
        ]
    
    def update_transaction(self, transaction_id: int, data: TransactionUpdate) -> Optional[Dict]:
        """Actualiza una transacción"""
        transaction_dict = data.dict(exclude_unset=True)
        transaction = self._transaction_repo.update(transaction_id, transaction_dict)
        
        if transaction:
            return TransactionResponse.from_orm(transaction).dict()
        return None
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Elimina una transacción"""
        return self._transaction_repo.delete(transaction_id)
    
    # ==================== SERVICIOS ANALÍTICOS ====================
    
    def get_monthly_summary(self, *args) -> Dict:
        """
        Obtiene un resumen completo del mes.
        
        Args:
            year: Año
            month: Mes
        
        Returns:
            {
                "periodo": "Noviembre 2025",
                "transacciones": [...],
                "resumen": {
                    "total_ingresos": 5000.0,
                    "total_gastos": 2500.0,
                    "balance": 2500.0
                },
                "por_categoria": [...]
            }
        """
        # Flexible signature:
        # - get_monthly_summary(year, month)
        # - get_monthly_summary(account_id, month, year)
        if len(args) == 2:
            month, year = args
            account_id = None
        elif len(args) == 3:
            account_id, month, year = args
        else:
            raise TypeError("get_monthly_summary expects (year, month) or (account_id, month, year)")

        if account_id is None:
            transactions = self._transaction_repo.get_by_month(year, month)
        else:
            transactions = self._transaction_repo.get_by_month(account_id, month, year)

        # determine start date
        start_dt = datetime(year, month, 1)
        balance = self._transaction_repo.get_balance_summary(account_id, start_dt)
        top_categories = self._transaction_repo.get_top_categories(account_id, limit=10, start_date=start_dt)
        
        return {
            "periodo": f"Mes {month}/{year}",
            "cantidad_transacciones": len(transactions),
            "resumen": balance,
            "top_categorias": top_categories
        }
    
    def get_expense_analysis(self, *args) -> Dict:
        """
        Análisis detallado de gastos en un período.
        
        Args:
            start_date: Fecha inicio
            end_date: Fecha fin
        
        Returns:
            Análisis de gastos por categoría
        """
        # Allow call as (account_id) or (start_date, end_date)
        if len(args) == 1 and isinstance(args[0], int):
            account_id = args[0]
            # default to current month
            end_date = datetime.utcnow()
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif len(args) == 2:
            start_date, end_date = args
        else:
            raise TypeError("get_expense_analysis expects (account_id) or (start_date, end_date)")

        total_by_category = self._transaction_repo.get_total_by_category(start_date=start_date, end_date=end_date)
        
        # Filtrar solo gastos
        gastos = [
            c for c in total_by_category 
            if c["tipo"] == "gasto"
        ]
        
        total_gasto = sum(c["total"] for c in gastos)
        
        # Calcular porcentaje
        for gasto in gastos:
            gasto["porcentaje"] = (
                (gasto["total"] / total_gasto * 100) if total_gasto > 0 else 0
            )
        
        return {
            "periodo_inicio": start_date,
            "periodo_fin": end_date,
            "total_gastos": total_gasto,
            "cantidad_categorias": len(gastos),
            "gastos_por_categoria": gastos
        }
    
    def get_income_analysis(self, *args) -> Dict:
        """
        Análisis detallado de ingresos en un período.
        
        Args:
            start_date: Fecha inicio
            end_date: Fecha fin
        
        Returns:
            Análisis de ingresos por categoría
        """
        # Allow call as (account_id) or (start_date, end_date)
        if len(args) == 1 and isinstance(args[0], int):
            account_id = args[0]
            end_date = datetime.utcnow()
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif len(args) == 2:
            start_date, end_date = args
        else:
            raise TypeError("get_income_analysis expects (account_id) or (start_date, end_date)")

        total_by_category = self._transaction_repo.get_total_by_category(start_date=start_date, end_date=end_date)
        
        # Filtrar solo ingresos
        ingresos = [
            c for c in total_by_category 
            if c["tipo"] == "ingreso"
        ]
        
        total_ingreso = sum(c["total"] for c in ingresos)
        
        # Calcular porcentaje
        for ingreso in ingresos:
            ingreso["porcentaje"] = (
                (ingreso["total"] / total_ingreso * 100) if total_ingreso > 0 else 0
            )
        
        return {
            "periodo_inicio": start_date,
            "periodo_fin": end_date,
            "total_ingresos": total_ingreso,
            "cantidad_categorias": len(ingresos),
            "ingresos_por_categoria": ingresos
        }
