"""
Transaction Repository - Consultas específicas de transacciones.

Métodos:
- Total gastado por categoría
- Transacciones de un mes
- Transacciones por rango de fecha
- Transacciones por cuenta
- Gasto promedio mensual
"""

from datetime import datetime, date
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database.models import Transaction, Category, Account


class TransactionRepository:
    """Repositorio para operaciones con transacciones"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Obtiene una transacción por ID"""
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Obtiene todas las transacciones"""
        return self.db.query(Transaction).offset(skip).limit(limit).all()
    
    def create(self, data: dict) -> Transaction:
        """Crea una nueva transacción"""
        transaction = Transaction(**data)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def update(self, transaction_id: int, data: dict) -> Optional[Transaction]:
        """Actualiza una transacción"""
        transaction = self.get_by_id(transaction_id)
        if transaction:
            for key, value in data.items():
                if value is not None:
                    setattr(transaction, key, value)
            self.db.commit()
            self.db.refresh(transaction)
        return transaction
    
    def delete(self, transaction_id: int) -> bool:
        """Elimina una transacción"""
        transaction = self.get_by_id(transaction_id)
        if transaction:
            self.db.delete(transaction)
            self.db.commit()
            return True
        return False
    
    # ==================== CONSULTAS ANALÍTICAS ====================
    
    def get_total_by_category(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Total gastado/ingresado por categoría en un período.
        
        Args:
            start_date: Fecha inicial (default: primer día del mes)
            end_date: Fecha final (default: hoy)
        
        Returns:
            Lista de dicts: [
                {"categoria_id": 1, "categoria_nombre": "Comida", "tipo": "gasto", "total": 250.50},
                ...
            ]
        """
        if start_date is None:
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if end_date is None:
            end_date = datetime.utcnow()
        
        results = self.db.query(
            Category.id.label("categoria_id"),
            Category.nombre.label("categoria_nombre"),
            Category.tipo,
            func.sum(Transaction.cantidad).label("total"),
            func.count(Transaction.id).label("cantidad_transacciones")
        ).join(
            Category, Transaction.categoria_id == Category.id
        ).filter(
            and_(
                Transaction.fecha >= start_date,
                Transaction.fecha <= end_date
            )
        ).group_by(
            Category.id, Category.nombre, Category.tipo
        ).order_by(
            func.sum(Transaction.cantidad).desc()
        ).all()
        
        return [
            {
                "categoria_id": r.categoria_id,
                "categoria_nombre": r.categoria_nombre,
                "tipo": r.tipo,
                "total": float(r.total) if r.total else 0.0,
                "cantidad_transacciones": r.cantidad_transacciones
            }
            for r in results
        ]
    
    def get_by_month(self, *args) -> List[Transaction]:
        """
        Obtiene todas las transacciones de un mes específico.
        
        Args:
            year: Año (ej: 2025)
            month: Mes (ej: 11)
        
        Returns:
            Lista de transacciones del mes
        """
        # Flexible signature:
        # - get_by_month(year, month)
        # - get_by_month(account_id, month, year)
        if len(args) == 2:
            year, month = args
            account_id = None
        elif len(args) == 3:
            account_id, month, year = args
        else:
            raise TypeError("get_by_month expects (year, month) or (account_id, month, year)")

        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)

        q = self.db.query(Transaction).filter(
            and_(
                Transaction.fecha >= start,
                Transaction.fecha < end
            )
        )

        if 'account_id' in locals() and account_id is not None:
            q = q.filter(Transaction.account_id == account_id)

        return q.order_by(Transaction.fecha.desc()).all()
    
    def get_by_date_range(self, *args) -> List[Transaction]:
        """
        Obtiene transacciones en un rango de fechas.
        
        Args:
            start_date: Fecha inicio
            end_date: Fecha fin
        
        Returns:
            Lista de transacciones
        """
        # Flexible signature:
        # - get_by_date_range(start_date, end_date)
        # - get_by_date_range(account_id, start_date, end_date)
        if len(args) == 2:
            start_date, end_date = args
            account_id = None
        elif len(args) == 3:
            account_id, start_date, end_date = args
        else:
            raise TypeError("get_by_date_range expects (start_date, end_date) or (account_id, start_date, end_date)")

        q = self.db.query(Transaction).filter(
            and_(
                Transaction.fecha >= start_date,
                Transaction.fecha <= end_date
            )
        )

        if 'account_id' in locals() and account_id is not None:
            q = q.filter(Transaction.account_id == account_id)

        return q.order_by(Transaction.fecha.desc()).all()
    
    def get_by_account(
        self,
        account_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transaction]:
        """
        Obtiene transacciones de una cuenta específica.
        
        Args:
            account_id: ID de la cuenta
            skip: Paginación (saltar registros)
            limit: Límite de registros
        
        Returns:
            Lista de transacciones de la cuenta
        """
        return self.db.query(Transaction).filter(
            Transaction.account_id == account_id
        ).order_by(
            Transaction.fecha.desc()
        ).offset(skip).limit(limit).all()
    
    def get_balance_summary(self, account_id: Optional[int] = None, start_date: Optional[datetime] = None) -> Dict:
        """
        Resumen de ingresos vs gastos desde una fecha.
        
        Args:
            start_date: Fecha inicial (default: primer día del mes)
        
        Returns:
            {
                "total_ingresos": 5000.0,
                "total_gastos": 2500.0,
                "balance": 2500.0
            }
        """
        if start_date is None:
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        end_date = datetime.utcnow()

        q = self.db.query(
            Transaction.tipo,
            func.sum(Transaction.cantidad).label("total")
        ).filter(
            and_(
                Transaction.fecha >= start_date,
                Transaction.fecha <= end_date
            )
        )

        if account_id is not None:
            q = q.filter(Transaction.account_id == account_id)

        results = q.group_by(Transaction.tipo).all()

        totals = {r.tipo: float(r.total) if r.total else 0.0 for r in results}

        ingresos = totals.get("ingreso", 0.0)
        gastos = totals.get("gasto", 0.0)

        return {
            "total_ingresos": ingresos,
            "total_gastos": gastos,
            "balance_neto": ingresos - gastos,
            "periodo_inicio": start_date,
            "periodo_fin": end_date
        }
    
    def get_average_monthly_expense(self, account_id: int, months: int = 3) -> float:
        """
        Calcula el gasto promedio mensual de los últimos N meses.
        
        Args:
            months: Número de meses a analizar (default: 3)
        
        Returns:
            Gasto promedio mensual
        """
        from dateutil.relativedelta import relativedelta
        
        start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_date = start_date - relativedelta(months=months)

        total_expenses = self.db.query(
            func.sum(Transaction.cantidad)
        ).filter(
            and_(
                Transaction.fecha >= start_date,
                Transaction.tipo == "gasto",
                Transaction.account_id == account_id
            )
        ).scalar()
        
        return float(total_expenses) / months if total_expenses else 0.0
    
    def get_top_categories(
        self,
        account_id: int,
        limit: int = 5,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtiene las TOP N categorías por gasto/ingreso.
        
        Args:
            limit: Número de categorías a retornar
            start_date: Fecha inicial
            end_date: Fecha final
            transaction_type: Filtrar por tipo (ingreso/gasto)
        
        Returns:
            Lista de categorías ordenadas por monto
        """
        if start_date is None:
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if end_date is None:
            end_date = datetime.utcnow()
        
        query = self.db.query(
            Category.id,
            Category.nombre,
            func.sum(Transaction.cantidad).label("total")
        ).join(
            Category, Transaction.categoria_id == Category.id
        ).filter(
            and_(
                Transaction.fecha >= start_date,
                Transaction.fecha <= end_date
            )
        )
        # filtrar por cuenta
        query = query.filter(Transaction.account_id == account_id)
        
        if transaction_type:
            query = query.filter(Transaction.tipo == transaction_type)
        
        results = query.group_by(
            Category.id, Category.nombre
        ).order_by(
            func.sum(Transaction.cantidad).desc()
        ).limit(limit).all()
        
        return [
            {
                "categoria_id": r.id,
                "categoria_nombre": r.nombre,
                "total": float(r.total) if r.total else 0.0
            }
            for r in results
        ]
