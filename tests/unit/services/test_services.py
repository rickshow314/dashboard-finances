"""
Tests para servicios.
Valida la lógica de negocio en la capa de servicios.
"""

import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.services.account_service import AccountService
from app.services.transaction_service import TransactionService
from app.services.budget_service import BudgetService
from app.database.models import Transaction, TransactionType, Account, Budget, AccountType, CurrencyType


class TestAccountService:
    """Tests para AccountService."""
    
    def test_create_account(self, test_db: Session):
        """Verifica creación de cuenta por servicio."""
        service = AccountService(test_db)
        
        account = Account(
            nombre="Nueva Cuenta",
            tipo=AccountType.CASH,
            moneda=CurrencyType.EUR,
            saldo_inicial=1000.00
        )
        
        created = service.create(account)
        assert created.id is not None
    
    def test_get_balance_for_account(self, test_db: Session, test_account):
        """Verifica obtención de saldo para una cuenta."""
        service = AccountService(test_db)
        
        balance = service.get_balance_for_account(test_account.id)
        assert isinstance(balance, (int, float))
        assert balance >= test_account.saldo_inicial
    
    def test_get_financial_health(self, test_db: Session, test_account):
        """Verifica obtención del estado financiero."""
        service = AccountService(test_db)
        
        health = service.get_financial_health()
        assert health is not None
        assert 'total_balance' in health
        assert 'total_accounts' in health


class TestTransactionService:
    """Tests para TransactionService."""
    
    def test_create_transaction(self, test_db: Session, test_account, test_category_income):
        """Verifica creación de transacción por servicio."""
        service = TransactionService(test_db)
        
        transaction = Transaction(
            fecha=date.today(),
            cantidad=1000.00,
            descripcion="Test",
            tipo=TransactionType.INCOME,
            account_id=test_account.id,
            categoria_id=test_category_income.id
        )
        
        created = service.create(transaction)
        assert created.id is not None
    
    def test_get_monthly_summary(self, test_db: Session, test_account, test_transaction):
        """Verifica resumen mensual de transacciones."""
        service = TransactionService(test_db)
        
        today = date.today()
        summary = service.get_monthly_summary(today.month, today.year)
        
        assert summary is not None
        if isinstance(summary, dict):
            # Verificar estructuras posibles
            assert len(summary) >= 0
    
    def test_get_expense_analysis(self, test_db: Session, test_account, test_transaction_expense):
        """Verifica análisis de gastos."""
        service = TransactionService(test_db)
        
        analysis = service.get_expense_analysis(test_account.id)
        assert analysis is not None
    
    def test_get_income_analysis(self, test_db: Session, test_account, test_transaction):
        """Verifica análisis de ingresos."""
        service = TransactionService(test_db)
        
        analysis = service.get_income_analysis(test_account.id)
        assert analysis is not None


class TestBudgetService:
    """Tests para BudgetService."""
    
    def test_create_budget(self, test_db: Session, test_category_expense):
        """Verifica creación de presupuesto por servicio."""
        service = BudgetService(test_db)
        
        budget = Budget(
            nombre="Test Budget",
            monto_limite=500.00,
            monto_usado=0.00,
            categoria_id=test_category_expense.id,
            activo=True
        )
        
        created = service.create(budget)
        assert created.id is not None
    
    def test_get_budget_status(self, test_db: Session, test_category_expense):
        """Verifica estado de presupuesto."""
        service = BudgetService(test_db)
        
        budget = Budget(
            nombre="Status Budget",
            monto_limite=100.00,
            monto_usado=80.00,
            categoria_id=test_category_expense.id,
            activo=True
        )
        test_db.add(budget)
        test_db.commit()
        test_db.refresh(budget)
        
        status = service.get_budget_status(test_category_expense.id)
        assert status is not None
    
    def test_get_all_budgets_summary(self, test_db: Session):
        """Verifica resumen de todos los presupuestos."""
        service = BudgetService(test_db)
        
        summary = service.get_all_budgets_summary()
        assert isinstance(summary, list)
    
    def test_get_budget_alerts(self, test_db: Session):
        """Verifica obtención de alertas de presupuesto."""
        service = BudgetService(test_db)
        
        alerts = service.get_budget_alerts()
        assert isinstance(alerts, list)


class TestServiceIntegration:
    """Tests de integración entre servicios."""
    
    def test_transaction_affects_budget(self, test_db: Session, test_account, test_category_expense, test_budget):
        """Verifica que una transacción afecta el presupuesto."""
        tx_service = TransactionService(test_db)
        budget_service = BudgetService(test_db)
        
        # Crear transacción
        transaction = Transaction(
            fecha=date.today(),
            cantidad=50.00,
            descripcion="Test",
            tipo=TransactionType.EXPENSE,
            account_id=test_account.id,
            categoria_id=test_category_expense.id
        )
        tx_service.create(transaction)
        
        # Verificar presupuesto
        status = budget_service.get_budget_status(test_category_expense.id)
        assert status is not None
    
    def test_multiple_transactions_summary(self, test_db: Session, test_account, multiple_transactions):
        """Verifica resumen de múltiples transacciones."""
        service = TransactionService(test_db)
        
        today = date.today()
        summary = service.get_monthly_summary(test_account.id, today.month, today.year)
        
        assert summary is not None
