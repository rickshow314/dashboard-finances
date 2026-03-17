"""
Tests para AccountRepository.
Valida todas las operaciones CRUD y consultas especializadas.
"""

import pytest
from sqlalchemy.orm import Session
from app.repositories.account_repository import AccountRepository
from app.database.models import Account, AccountType, CurrencyType


class TestAccountRepositoryCRUD:
    """Tests para operaciones CRUD básicas."""
    
    def test_create_account(self, test_db: Session):
        """Verifica que se puede crear una cuenta."""
        repo = AccountRepository(test_db)
        
        created = repo.create({
            "nombre": "Nueva Cuenta",
            "tipo": AccountType.CASH,
            "moneda": CurrencyType.EUR,
            "saldo_inicial": 500.00
        })
        assert created.id is not None
        assert created.nombre == "Nueva Cuenta"
        assert created.saldo_inicial == 500.00
    
    def test_get_account_by_id(self, test_db: Session, test_account: Account):
        """Verifica que se puede recuperar una cuenta por ID."""
        repo = AccountRepository(test_db)
        
        retrieved = repo.get_by_id(test_account.id)
        assert retrieved is not None
        assert retrieved.id == test_account.id
        assert retrieved.nombre == "Cuenta Test"
    
    def test_get_nonexistent_account(self, test_db: Session):
        """Verifica que devuelve None para cuenta inexistente."""
        repo = AccountRepository(test_db)
        
        retrieved = repo.get_by_id(999)
        assert retrieved is None
    
    def test_update_account(self, test_db: Session, test_account: Account):
        """Verifica que se puede actualizar una cuenta."""
        repo = AccountRepository(test_db)
        
        updated = repo.update(test_account.id, {
            "nombre": "Cuenta Actualizada",
            "saldo_inicial": 2000.00
        })
        assert updated.nombre == "Cuenta Actualizada"
        assert updated.saldo_inicial == 2000.00
    
    def test_delete_account(self, test_db: Session, test_account: Account):
        """Verifica que se puede eliminar una cuenta."""
        repo = AccountRepository(test_db)
        
        result = repo.delete(test_account.id)
        assert result is True
        
        retrieved = repo.get_by_id(test_account.id)
        assert retrieved is None
    
    def test_list_all_accounts(self, test_db: Session, test_account: Account, test_account_savings: Account):
        """Verifica que se listan todas las cuentas."""
        repo = AccountRepository(test_db)
        
        all_accounts = repo.get_all()
        assert len(all_accounts) >= 2
        assert any(a.id == test_account.id for a in all_accounts)
        assert any(a.id == test_account_savings.id for a in all_accounts)


class TestAccountRepositorySpecialized:
    """Tests para consultas especializadas."""
    
    def test_get_current_balance(self, test_db: Session, test_account: Account):
        """Verifica el saldo actual correcto."""
        repo = AccountRepository(test_db)
        
        balance = repo.get_current_balance(test_account.id)
        assert isinstance(balance, dict)
        assert balance["saldo_actual"] == 1000.00
    
    def test_get_current_balance_nonexistent(self, test_db: Session):
        """Verifica que devuelve None para cuenta inexistente."""
        repo = AccountRepository(test_db)
        
        balance = repo.get_current_balance(999)
        assert balance is None
    
    def test_get_all_balances(self, test_db: Session, test_account: Account, test_account_savings: Account):
        """Verifica que se obtienen todos los saldos."""
        repo = AccountRepository(test_db)
        
        balances = repo.get_all_balances()
        assert len(balances) >= 2
        assert isinstance(balances, list)
        assert all(isinstance(b, dict) for b in balances)
        # Verificar que nuestras cuentas están en la lista
        account_ids = [b["account_id"] for b in balances]
        assert test_account.id in account_ids
        assert test_account_savings.id in account_ids
    
    def test_get_total_balance(self, test_db: Session, test_account: Account, test_account_savings: Account):
        repo = AccountRepository(test_db)
        total = repo.get_total_balance()
        assert isinstance(total, dict)
        assert "saldo_total" in total
        assert total["saldo_total"] >= 6000.00  # Al menos nuestros saldos iniciales (test_db)
        expected = 1000.00 + 5000.00
        assert total["saldo_total"] == expected
    
    def test_get_by_type(self, test_db: Session, test_account: Account, test_account_savings: Account):
        """Verifica filtrado por tipo de cuenta."""
        repo = AccountRepository(test_db)
        
        savings = repo.get_by_type(AccountType.SAVINGS)
        assert len(savings) >= 1
        assert test_account_savings in savings
    
    def test_get_accounts_by_currency(self, test_db: Session, test_account: Account):
        """Verifica filtrado por moneda."""
        repo = AccountRepository(test_db)
        
        eur_accounts = repo.get_accounts_by_currency(CurrencyType.EUR)
        assert len(eur_accounts) >= 1
        assert test_account in eur_accounts


class TestAccountRepositoryEdgeCases:
    """Tests para casos límite."""
    
    def test_update_nonexistent_account(self, test_db: Session):
        """Verifica actualizar cuenta inexistente."""
        repo = AccountRepository(test_db)
        
        # No debe fallar, pero no actualiza nada
        result = repo.update(999, {"nombre": "Fake"})
        assert result is None
    
    def test_delete_nonexistent_account(self, test_db: Session):
        """Verifica eliminar cuenta inexistente."""
        repo = AccountRepository(test_db)
        
        result = repo.delete(999)
        assert result is False
