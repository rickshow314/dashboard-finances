"""
Account Service - Lógica de negocio para cuentas.

Orquesta operaciones entre repositorios y aplica reglas de negocio.
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.repositories.account_repository import AccountRepository
from app.schemas.schemas import AccountCreate, AccountUpdate, AccountResponse


class AccountService:
    """Servicio para operaciones con cuentas"""
    
    def __init__(self, db: Session):
        self.db = db
        self._account_repo = AccountRepository(db)
    
    def create_account(self, data: AccountCreate) -> Dict:
        """
        Crea una nueva cuenta.
        
        Args:
            data: Schema con datos de la cuenta
        
        Returns:
            Cuenta creada
        """
        account_dict = data.dict()
        account = self._account_repo.create(account_dict)
        
        return {
            "id": account.id,
            "nombre": account.nombre,
            "tipo": account.tipo.value,
            "moneda": account.moneda.value,
            "saldo_inicial": account.saldo_inicial,
            "created_at": account.created_at
        }

    # Backwards-compatible wrapper expected by tests
    def create(self, account_obj) -> Dict:
        if hasattr(account_obj, 'dict'):
            data = account_obj.dict()
        elif isinstance(account_obj, dict):
            data = account_obj
        else:
            # assume ORM instance
            data = {
                "nombre": getattr(account_obj, 'nombre', None),
                "tipo": getattr(account_obj, 'tipo', None),
                "moneda": getattr(account_obj, 'moneda', None),
                "saldo_inicial": getattr(account_obj, 'saldo_inicial', 0.0)
            }

        account = self._account_repo.create(data)
        return account
    
    def get_account(self, account_id: int) -> Optional[Dict]:
        """Obtiene una cuenta por ID"""
        account = self._account_repo.get_by_id(account_id)
        if account:
            return AccountResponse.from_orm(account).dict()
        return None
    
    def get_all_accounts(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Obtiene todas las cuentas formateadas"""
        accounts = self._account_repo.get_all(skip, limit)
        return [
            {
                "id": acc.id,
                "nombre": acc.nombre,
                "tipo": acc.tipo.value if hasattr(acc.tipo, 'value') else str(acc.tipo),
                "moneda": acc.moneda.value if hasattr(acc.moneda, 'value') else str(acc.moneda),
                "saldo_inicial": acc.saldo_inicial or 0.0,
                "created_at": acc.created_at,
                "updated_at": acc.updated_at
            }
            for acc in accounts
        ]
    
    def update_account(self, account_id: int, data: AccountUpdate) -> Optional[Dict]:
        """Actualiza una cuenta"""
        account_dict = data.dict(exclude_unset=True)
        account = self._account_repo.update(account_id, account_dict)
        
        if account:
            return AccountResponse.from_orm(account).dict()
        return None
    
    def delete_account(self, account_id: int) -> bool:
        """Elimina una cuenta"""
        return self._account_repo.delete(account_id)
    
    # ==================== SERVICIOS ANALÍTICOS ====================
    
    def get_balance_for_account(self, account_id: int) -> Optional[Dict]:
        """
        Obtiene el saldo completo de una cuenta.
        
        Args:
            account_id: ID de la cuenta
        
        Returns:
            Información de saldo detallada
        """
        balance = self._account_repo.get_current_balance(account_id)
        if balance and isinstance(balance, dict):
            return balance.get("saldo_actual")
        return balance
    
    def get_all_balances(self) -> List[Dict]:
        """
        Obtiene los saldos de todas las cuentas.
        
        Returns:
            [
                {
                    "account_id": 1,
                    "nombre": "Efectivo",
                    "saldo_actual": 500.0,
                    ...
                },
                ...
            ]
        """
        return self._account_repo.get_all_balances()
    
    def get_total_balance(self) -> Dict:
        """
        Obtiene el balance total consolidado.
        
        Returns:
            {
                "total_saldo_inicial": 2000.0,
                "total_ingresos": 10000.0,
                "total_gastos": 5000.0,
                "saldo_total": 7000.0,
                "cantidad_cuentas": 3
            }
        """
        return self._account_repo.get_total_balance()
    
    def get_financial_health(self) -> Dict:
        """
        Calcula un índice de salud financiera.
        
        Returns:
            {
                "saldo_total": 7000.0,
                "cuentas_activas": 3,
                "salud": "Saludable" | "Neutral" | "Crítica"
            }
        """
        total_balance = self._account_repo.get_total_balance()
        
        saldo_total = total_balance["saldo_total"]
        
        if saldo_total > total_balance["total_gastos"] * 2:
            salud = "Saludable"
        elif saldo_total > 0:
            salud = "Neutral"
        else:
            salud = "Crítica"
        
        return {
            "saldo_total": saldo_total,
            "cuentas_activas": total_balance["cantidad_cuentas"],
            "salud": salud,
            "detalles": total_balance,
            "total_balance": saldo_total,
            "total_accounts": total_balance["cantidad_cuentas"]
        }
