"""
Account Repository - Consultas específicas de cuentas.

Métodos:
- Saldo actual por cuenta
- Saldo total de todas las cuentas
- Cuentas por tipo
- Evolución histórica del saldo
"""

from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.database.models import Account, Transaction


class AccountRepository:
    """Repositorio para operaciones con cuentas"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, account_id: int) -> Optional[Account]:
        """Obtiene una cuenta por ID"""
        return self.db.query(Account).filter(Account.id == account_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Account]:
        """Obtiene todas las cuentas"""
        return self.db.query(Account).offset(skip).limit(limit).all()
    
    def create(self, data: dict) -> Account:
        """Crea una nueva cuenta"""
        account = Account(**data)
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account
    
    def update(self, account_id: int, data: dict) -> Optional[Account]:
        """Actualiza una cuenta"""
        account = self.get_by_id(account_id)
        if account:
            for key, value in data.items():
                if value is not None:
                    setattr(account, key, value)
            self.db.commit()
            self.db.refresh(account)
        return account
    
    def delete(self, account_id: int) -> bool:
        """Elimina una cuenta"""
        account = self.get_by_id(account_id)
        if account:
            self.db.delete(account)
            self.db.commit()
            return True
        return False
    
    # ==================== CONSULTAS ANALÍTICAS ====================
    
    def get_current_balance(self, account_id: int) -> Dict:
        """
        Calcula el saldo actual de una cuenta.
        
        Fórmula: saldo_inicial + ingresos - gastos
        
        Args:
            account_id: ID de la cuenta
        
        Returns:
            {
                "account_id": 1,
                "nombre": "Mi Cuenta",
                "saldo_inicial": 1000.0,
                "ingresos": 5000.0,
                "gastos": 2500.0,
                "saldo_actual": 3500.0
            }
        """
        account = self.get_by_id(account_id)
        if not account:
            return None
        
        # Calcular ingresos y gastos
        result = self.db.query(
            func.sum(
                case(
                    (Transaction.tipo == "ingreso", Transaction.cantidad),
                    else_=0
                )
            ).label("total_ingresos"),
            func.sum(
                case(
                    (Transaction.tipo == "gasto", Transaction.cantidad),
                    else_=0
                )
            ).label("total_gastos")
        ).filter(
            Transaction.account_id == account_id
        ).first()
        
        ingresos = float(result.total_ingresos) if result.total_ingresos else 0.0
        gastos = float(result.total_gastos) if result.total_gastos else 0.0
        saldo_inicial = float(account.saldo_inicial) if account.saldo_inicial else 0.0
        
        saldo_actual = saldo_inicial + ingresos - gastos
        
        return {
            "account_id": account.id,
            "nombre": account.nombre,
            "tipo": account.tipo.value,
            "moneda": account.moneda.value,
            "saldo_inicial": saldo_inicial,
            "total_ingresos": ingresos,
            "total_gastos": gastos,
            "saldo_actual": saldo_actual
        }
    
    def get_all_balances(self) -> List[Dict]:
        """
        Obtiene el saldo actual de todas las cuentas.
        
        Returns:
            [
                {"account_id": 1, "nombre": "Efectivo", "saldo_actual": 500.0},
                {"account_id": 2, "nombre": "Tarjeta", "saldo_actual": 3000.0},
                ...
            ]
        """
        accounts = self.get_all(limit=1000)
        balances = []
        
        for account in accounts:
            balance = self.get_current_balance(account.id)
            if balance:
                balances.append(balance)
        
        return balances
    
    def get_total_balance(self) -> Dict:
        """
        Calcula el balance total de todas las cuentas.
        
        Returns:
            {
                "total_saldo_inicial": 2000.0,
                "total_ingresos": 10000.0,
                "total_gastos": 5000.0,
                "saldo_total": 7000.0,
                "cantidad_cuentas": 3
            }
        """
        accounts = self.get_all(limit=1000)
        
        total_saldo_inicial = sum(
            float(a.saldo_inicial) if a.saldo_inicial else 0.0 
            for a in accounts
        )
        
        result = self.db.query(
            func.sum(
                case(
                    (Transaction.tipo == "ingreso", Transaction.cantidad),
                    else_=0
                )
            ).label("total_ingresos"),
            func.sum(
                case(
                    (Transaction.tipo == "gasto", Transaction.cantidad),
                    else_=0
                )
            ).label("total_gastos")
        ).first()
        
        total_ingresos = float(result.total_ingresos) if result.total_ingresos else 0.0
        total_gastos = float(result.total_gastos) if result.total_gastos else 0.0
        
        saldo_total = total_saldo_inicial + total_ingresos - total_gastos
        
        return {
            "total_saldo_inicial": total_saldo_inicial,
            "total_ingresos": total_ingresos,
            "total_gastos": total_gastos,
            "saldo_total": saldo_total,
            "cantidad_cuentas": len(accounts)
        }
    
    def get_by_type(self, account_type: str) -> List[Account]:
        """
        Obtiene cuentas por tipo.
        
        Args:
            account_type: Tipo de cuenta (efectivo, tarjeta, broker, ahorro, otro)
        
        Returns:
            Lista de cuentas del tipo especificado
        """
        return self.db.query(Account).filter(
            Account.tipo == account_type
        ).all()
    
    def get_accounts_by_currency(self, currency: str) -> List[Account]:
        """
        Obtiene cuentas por moneda.
        
        Args:
            currency: Moneda (USD, EUR, MXN, etc.)
        
        Returns:
            Lista de cuentas con esa moneda
        """
        return self.db.query(Account).filter(
            Account.moneda == currency
        ).all()
