"""
Tests para BudgetRepository.
Valida operaciones de presupuestos y alertas.
"""

import pytest
from sqlalchemy.orm import Session
from app.repositories.budget_repository import BudgetRepository
from app.database.models import Budget


class TestBudgetRepositoryCRUD:
    """Tests para operaciones CRUD básicas."""
    
    def test_create_budget(self, test_db: Session, test_category_expense):
        """Verifica que se puede crear un presupuesto."""
        repo = BudgetRepository(test_db)
        
        created = repo.create({
            "nombre": "Presupuesto Test",
            "monto_limite": 300.00,
            "monto_usado": 0.00,
            "categoria_id": test_category_expense.id,
            "activo": True
        })
        assert created.id is not None
        assert created.nombre == "Presupuesto Test"
    
    def test_get_budget_by_id(self, test_db: Session, test_budget):
        """Verifica que se puede recuperar un presupuesto por ID."""
        repo = BudgetRepository(test_db)
        
        retrieved = repo.get_by_id(test_budget.id)
        assert retrieved is not None
        assert retrieved.id == test_budget.id
    
    def test_update_budget(self, test_db: Session, test_budget):
        """Verifica que se puede actualizar un presupuesto."""
        repo = BudgetRepository(test_db)
        
        updated = repo.update(test_budget.id, {
            "monto_limite": 300.00,
            "monto_usado": 150.00
        })
        assert updated.monto_limite == 300.00
        assert updated.monto_usado == 150.00
    
    def test_delete_budget(self, test_db: Session, test_budget):
        """Verifica que se puede eliminar un presupuesto."""
        repo = BudgetRepository(test_db)
        
        result = repo.delete(test_budget.id)
        assert result is True


class TestBudgetRepositorySpecialized:
    """Tests para consultas especializadas."""
    
    def test_get_active_budgets(self, test_db: Session, test_budget):
        """Verifica filtrado de presupuestos activos."""
        repo = BudgetRepository(test_db)
        
        active = repo.get_active_budgets()
        assert len(active) >= 1
        assert test_budget in active
    
    def test_get_budget_vs_actual(self, test_db: Session, test_budget):
        """Verifica comparativa presupuesto vs actual."""
        repo = BudgetRepository(test_db)
        
        comparison = repo.get_budget_vs_actual(test_budget.id)
        assert isinstance(comparison, dict)
        assert "budget_id" in comparison
        assert "estado" in comparison
    
    def test_get_exceeded_budgets(self, test_db: Session):
        """Verifica presupuestos excedidos."""
        repo = BudgetRepository(test_db)
        
        exceeded = repo.get_exceeded_budgets()
        assert isinstance(exceeded, list)
    
    def test_get_budgets_in_alert(self, test_db: Session, test_category_expense):
        """Verifica presupuestos en alerta (>80%)."""
        repo = BudgetRepository(test_db)
        
        # Crea presupuesto al 85%
        alert = Budget(
            nombre="Alerta",
            monto_limite=100.00,
            monto_usado=85.00,
            categoria_id=test_category_expense.id,
            activo=True
        )
        test_db.add(alert)
        test_db.commit()
        
        alerts = repo.get_budgets_in_alert()
        assert len(alerts) >= 1


class TestBudgetRepositoryEdgeCases:
    """Tests para casos límite."""
    
    def test_zero_limit_budget(self, test_db: Session, test_category_expense):
        """Verifica presupuesto con límite 0."""
        repo = BudgetRepository(test_db)
        
        created = repo.create({
            "nombre": "Sin límite",
            "monto_limite": 0.00,
            "monto_usado": 0.00,
            "categoria_id": test_category_expense.id,
            "activo": True
        })
        
        assert created.id is not None
        assert created.monto_limite == 0.00
    
    def test_negative_used_budget(self, test_db: Session, test_category_expense):
        """Verifica presupuesto con monto usado negativo."""
        repo = BudgetRepository(test_db)
        
        created = repo.create({
            "nombre": "Negativo",
            "monto_limite": 100.00,
            "monto_usado": -50.00,
            "categoria_id": test_category_expense.id,
            "activo": True
        })
        
        assert created.id is not None
        assert created.monto_usado == -50.00
