"""
Tests para TransactionRepository.
Valida consultas de transacciones y análisis financieros.
"""

import pytest
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
from app.repositories.transaction_repository import TransactionRepository
from app.database.models import Transaction, TransactionType


class TestTransactionRepositoryCRUD:
    """Tests para operaciones CRUD básicas."""
    
    def test_create_transaction(self, test_db: Session, test_account, test_category_income):
        """Verifica que se puede crear una transacción."""
        repo = TransactionRepository(test_db)
        
        created = repo.create({
            "fecha": date.today(),
            "cantidad": 1500.00,
            "descripcion": "Ingreso freelance",
            "tipo": TransactionType.INCOME,
            "account_id": test_account.id,
            "categoria_id": test_category_income.id
        })
        assert created.id is not None
        assert created.cantidad == 1500.00
    
    def test_get_transaction_by_id(self, test_db: Session, test_transaction):
        """Verifica que se puede recuperar una transacción por ID."""
        repo = TransactionRepository(test_db)
        
        retrieved = repo.get_by_id(test_transaction.id)
        assert retrieved is not None
        assert retrieved.id == test_transaction.id
        assert retrieved.cantidad == 2000.00
    
    def test_update_transaction(self, test_db: Session, test_transaction):
        """Verifica que se puede actualizar una transacción."""
        repo = TransactionRepository(test_db)
        
        updated = repo.update(test_transaction.id, {
            "descripcion": "Salario actualizado",
            "cantidad": 2200.00
        })
        assert updated.descripcion == "Salario actualizado"
        assert updated.cantidad == 2200.00
    
    def test_delete_transaction(self, test_db: Session, test_transaction):
        """Verifica que se puede eliminar una transacción."""
        repo = TransactionRepository(test_db)
        
        result = repo.delete(test_transaction.id)
        assert result is True
        
        retrieved = repo.get_by_id(test_transaction.id)
        assert retrieved is None


class TestTransactionRepositorySpecialized:
    """Tests para consultas especializadas."""
    
    def test_get_total_by_category(self, test_db: Session, test_account, test_category_expense, multiple_transactions):
        """Verifica que calcula correctamente el total por categoría."""
        repo = TransactionRepository(test_db)
        
        total = repo.get_total_by_category()
        assert isinstance(total, list)
        # Debería retornar una lista de dicts con categoria info
        if total:
            assert all("categoria_id" in t and "total" in t for t in total)
    
    def test_get_by_month(self, test_db: Session, test_account, test_category_income, test_transaction):
        """Verifica filtrado por mes."""
        repo = TransactionRepository(test_db)
        
        today = date.today()
        transactions = repo.get_by_month(today.year, today.month)
        
        assert isinstance(transactions, list)
        assert len(transactions) >= 1
        assert test_transaction in transactions
    
    def test_get_by_date_range(self, test_db: Session, test_account, multiple_transactions):
        """Verifica filtrado por rango de fechas."""
        repo = TransactionRepository(test_db)
        
        today = date.today()
        start = datetime.combine(today - timedelta(days=5), datetime.min.time())
        end = datetime.combine(today, datetime.max.time())
        
        transactions = repo.get_by_date_range(start, end)
        assert len(transactions) > 0
        assert isinstance(transactions, list)
    
    def test_get_by_account(self, test_db: Session, test_account, test_transaction):
        """Verifica que se obtienen transacciones de una cuenta."""
        repo = TransactionRepository(test_db)
        
        transactions = repo.get_by_account(test_account.id)
        assert len(transactions) >= 1
        assert test_transaction in transactions
    
    def test_get_balance_summary(self, test_db: Session, test_account, test_transaction, test_transaction_expense):
        """Verifica el resumen de balance."""
        repo = TransactionRepository(test_db)
        
        summary = repo.get_balance_summary(test_account.id)
        assert summary is not None
        assert 'total_ingresos' in summary
        assert 'total_gastos' in summary
        assert 'balance_neto' in summary
    
    def test_get_average_monthly_expense(self, test_db: Session, test_account, test_category_expense, multiple_transactions):
        """Verifica el promedio de gasto mensual."""
        repo = TransactionRepository(test_db)
        
        avg = repo.get_average_monthly_expense(test_account.id)
        assert isinstance(avg, float)
        assert avg > 0
    
    def test_get_top_categories(self, test_db: Session, test_account, test_category_expense, multiple_transactions):
        """Verifica las categorías principales."""
        repo = TransactionRepository(test_db)
        
        top = repo.get_top_categories(test_account.id, limit=5)
        assert isinstance(top, list)
        assert len(top) > 0


class TestTransactionRepositoryEdgeCases:
    """Tests para casos límite."""
    
    def test_get_by_month_no_transactions(self, test_db: Session, test_account):
        """Verifica mes sin transacciones."""
        repo = TransactionRepository(test_db)
        
        transactions = repo.get_by_month(test_account.id, 1, 2020)
        assert len(transactions) == 0
    
    def test_get_by_date_range_empty(self, test_db: Session, test_account):
        """Verifica rango vacío."""
        repo = TransactionRepository(test_db)
        
        past = date(2020, 1, 1)
        future = date(2020, 1, 31)
        
        transactions = repo.get_by_date_range(test_account.id, past, future)
        assert len(transactions) == 0
    
    def test_get_balance_summary_empty_account(self, test_db: Session, test_account):
        """Verifica resumen de cuenta vacía (sin transacciones)."""
        repo = TransactionRepository(test_db)
        
        summary = repo.get_balance_summary(test_account.id)
        assert summary['total_ingresos'] == 0.0
        assert summary['total_gastos'] == 0.0
        assert summary['balance_neto'] == 0.0
    
    def test_get_average_monthly_expense_empty_account(self, test_db: Session, test_account):
        """Verifica promedio de cuenta sin gastos."""
        repo = TransactionRepository(test_db)
        
        avg = repo.get_average_monthly_expense(test_account.id)
        assert avg == 0.0
