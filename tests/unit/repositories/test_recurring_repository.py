"""
Tests para RecurringRepository.
Valida operaciones con ingresos/gastos recurrentes.
"""

import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.repositories.recurring_repository import RecurringRepository
from app.database.models import Recurring, RecurrenceFrequency, TransactionType


class TestRecurringRepositoryCRUD:
    """Tests para operaciones CRUD básicas."""
    
    def test_create_recurring(self, test_db: Session, test_account, test_category_income):
        """Verifica que se puede crear un recurrente."""
        repo = RecurringRepository(test_db)
        
        created = repo.create({
            "nombre": "Salario Mensual",
            "monto": 2000.00,
            "tipo": TransactionType.INCOME,
            "frecuencia": RecurrenceFrequency.MONTHLY,
            "categoria_id": test_category_income.id,
            "account_id": test_account.id,
            "fecha_fin": date.today() + timedelta(days=365)
        })
        assert created.id is not None
        assert created.monto == 2000.00
    
    def test_get_recurring_by_id(self, test_db: Session, test_recurring):
        """Verifica que se puede recuperar un recurrente por ID."""
        repo = RecurringRepository(test_db)
        
        retrieved = repo.get_by_id(test_recurring.id)
        assert retrieved is not None
        assert retrieved.id == test_recurring.id
    
    def test_update_recurring(self, test_db: Session, test_recurring):
        """Verifica que se puede actualizar un recurrente."""
        repo = RecurringRepository(test_db)
        
        updated = repo.update(test_recurring.id, {"monto": 2500.00})
        assert updated.monto == 2500.00
    
    def test_delete_recurring(self, test_db: Session, test_recurring):
        """Verifica que se puede eliminar un recurrente."""
        repo = RecurringRepository(test_db)
        
        result = repo.delete(test_recurring.id)
        assert result is True


class TestRecurringRepositorySpecialized:
    """Tests para consultas especializadas."""
    
    def test_get_active_recurring(self, test_db: Session, test_recurring):
        """Verifica obtención de recurrentes activos."""
        repo = RecurringRepository(test_db)
        
        active = repo.get_active_recurring()
        assert len(active) >= 1
        assert test_recurring in active
    
    def test_get_by_type(self, test_db: Session, test_recurring):
        """Verifica filtrado por tipo de transacción."""
        repo = RecurringRepository(test_db)
        
        incomes = repo.get_by_type(TransactionType.INCOME)
        assert isinstance(incomes, list)
        assert len(incomes) >= 1
        assert test_recurring in incomes
    
    def test_get_recurring_by_frequency(self, test_db: Session, test_recurring):
        """Verifica filtrado por frecuencia."""
        repo = RecurringRepository(test_db)
        
        monthly = repo.get_recurring_by_frequency(RecurrenceFrequency.MONTHLY)
        assert isinstance(monthly, list)
        assert len(monthly) >= 1
        assert test_recurring in monthly
    
    def test_get_recurring_by_category(self, test_db: Session, test_recurring, test_category_income):
        """Verifica filtrado por categoría."""
        repo = RecurringRepository(test_db)
        
        by_category = repo.get_recurring_by_category(test_category_income.id)
        assert len(by_category) >= 1
        assert test_recurring in by_category
    
    def test_calculate_monthly_projection(self, test_db: Session, test_account, test_recurring):
        """Verifica cálculo de proyección mensual."""
        repo = RecurringRepository(test_db)
        
        projection = repo.calculate_monthly_projection()
        assert projection is not None
        assert isinstance(projection, dict)
        # La proyección puede retornar diferentes keys según la implementación
        assert "balance_proyectado" in projection or "ingresos" in projection
    
    def test_get_soon_to_expire(self, test_db: Session, test_account, test_category_income):
        """Verifica obtención de recurrentes próximos a vencer."""
        repo = RecurringRepository(test_db)
        
        # Crea recurrente que vence en 5 días
        soon_expire = Recurring(
            nombre="Casi vence",
            monto=100.00,
            tipo=TransactionType.INCOME,
            frecuencia=RecurrenceFrequency.MONTHLY,
            categoria_id=test_category_income.id,
            account_id=test_account.id,
            fecha_fin=date.today() + timedelta(days=5)
        )
        test_db.add(soon_expire)
        test_db.commit()
        
        soon = repo.get_soon_to_expire(days=30)
        assert len(soon) >= 1


class TestRecurringRepositoryEdgeCases:
    """Tests para casos límite."""
    
    def test_recurring_already_expired(self, test_db: Session, test_account, test_category_income):
        """Verifica recurrente ya vencido."""
        repo = RecurringRepository(test_db)
        
        created = repo.create({
            "nombre": "Vencido",
            "monto": 100.00,
            "tipo": TransactionType.INCOME,
            "frecuencia": RecurrenceFrequency.MONTHLY,
            "categoria_id": test_category_income.id,
            "account_id": test_account.id,
            "fecha_fin": date.today() - timedelta(days=1)
        })
        
        active = repo.get_active_recurring()
        # El recurrente vencido no debería aparecer en los activos
        assert created not in active or len(active) == 0
    
    def test_zero_amount_recurring(self, test_db: Session, test_account, test_category_income):
        """Verifica recurrente con monto 0."""
        repo = RecurringRepository(test_db)
        
        zero = Recurring(
            nombre="Cero",
            monto=0.00,
            tipo=TransactionType.INCOME,
            frecuencia=RecurrenceFrequency.MONTHLY,
            categoria_id=test_category_income.id,
            account_id=test_account.id,
            fecha_fin=date.today() + timedelta(days=365)
        )
        test_db.add(zero)
        test_db.commit()
        
        retrieved = repo.get_by_id(zero.id)
        assert retrieved.monto == 0.00
