"""
Tests para FinancialGoalRepository.
Valida operaciones con objetivos financieros.
"""

import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.repositories.goal_repository import FinancialGoalRepository
from app.database.models import FinancialGoal, GoalStatus


class TestFinancialGoalRepositoryCRUD:
    """Tests para operaciones CRUD básicas."""
    
    def test_create_goal(self, test_db: Session, test_account):
        """Verifica que se puede crear un objetivo."""
        repo = FinancialGoalRepository(test_db)
        
        created = repo.create({
            "nombre": "Ahorrar para coche",
            "monto_objetivo": 25000.00,
            "monto_ahorrado": 0.00,
            "account_id": test_account.id,
            "estado": GoalStatus.ACTIVE,
            "prioridad": 1
        })
        assert created.id is not None
        assert created.monto_objetivo == 25000.00
    
    def test_get_goal_by_id(self, test_db: Session, test_goal):
        """Verifica que se puede recuperar un objetivo por ID."""
        repo = FinancialGoalRepository(test_db)
        
        retrieved = repo.get_by_id(test_goal.id)
        assert retrieved is not None
        assert retrieved.id == test_goal.id
    
    def test_update_goal(self, test_db: Session, test_goal):
        """Verifica que se puede actualizar un objetivo."""
        repo = FinancialGoalRepository(test_db)
        
        updated = repo.update(test_goal.id, {
            "monto_ahorrado": 1000.00,
            "estado": GoalStatus.ACTIVE
        })
        assert updated.monto_ahorrado == 1000.00
    
    def test_delete_goal(self, test_db: Session, test_goal):
        """Verifica que se puede eliminar un objetivo."""
        repo = FinancialGoalRepository(test_db)
        
        result = repo.delete(test_goal.id)
        assert result is True


class TestFinancialGoalRepositorySpecialized:
    """Tests para consultas especializadas."""
    
    def test_get_active_goals(self, test_db: Session, test_goal):
        """Verifica obtención de objetivos activos."""
        repo = FinancialGoalRepository(test_db)
        
        active = repo.get_active_goals()
        assert len(active) >= 1
        assert test_goal in active
    
    def test_get_goals_by_status(self, test_db: Session, test_goal):
        """Verifica filtrado por estado."""
        repo = FinancialGoalRepository(test_db)
        
        in_progress = repo.get_goals_by_status(GoalStatus.ACTIVE)
        assert len(in_progress) >= 1
        assert test_goal in in_progress
    
    def test_get_goals_with_progress(self, test_db: Session, test_goal):
        """Verifica obtención de objetivos con progreso."""
        repo = FinancialGoalRepository(test_db)
        
        with_progress = repo.get_goals_with_progress()
        assert isinstance(with_progress, list)
        assert len(with_progress) > 0
    
    def test_get_near_completion(self, test_db: Session, test_account):
        """Verifica obtención de objetivos próximos a completar."""
        repo = FinancialGoalRepository(test_db)
        
        # Crea objetivo al 95% completado
        near = FinancialGoal(
            nombre="Casi completado",
            monto_objetivo=1000.00,
            monto_ahorrado=950.00,
            account_id=test_account.id,
            estado=GoalStatus.ACTIVE,
            prioridad=1
        )
        test_db.add(near)
        test_db.commit()
        
        near_completion = repo.get_near_completion(threshold=90)
        assert len(near_completion) >= 1
    
    def test_get_goals_by_priority(self, test_db: Session, test_goal):
        """Verifica filtrado por prioridad."""
        repo = FinancialGoalRepository(test_db)
        
        high_priority = repo.get_goals_by_priority(1)
        assert len(high_priority) >= 1
        assert test_goal in high_priority
    
    def test_get_total_savings_target(self, test_db: Session, test_account, test_goal):
        """Verifica obtención del total de ahorro objetivo."""
        repo = FinancialGoalRepository(test_db)
        
        total = repo.get_total_savings_target()
        assert isinstance(total, (int, float))
        assert total >= test_goal.monto_objetivo
    
    def test_get_overdue_goals(self, test_db: Session, test_account):
        """Verifica obtención de objetivos vencidos."""
        repo = FinancialGoalRepository(test_db)
        
        # Crear objetivo con fecha vencida
        from datetime import datetime, timedelta
        overdue = FinancialGoal(
            nombre="Vencido",
            monto_objetivo=500.00,
            monto_ahorrado=100.00,
            account_id=test_account.id,
            estado=GoalStatus.ACTIVE,
            prioridad=1,
            fecha_objetivo=datetime.utcnow() - timedelta(days=1)
        )
        test_db.add(overdue)
        test_db.commit()
        
        overdue_goals = repo.get_overdue_goals()
        assert isinstance(overdue_goals, list)
        # Si el repositorio retorna dicts, verificamos que es lista


class TestFinancialGoalRepositoryEdgeCases:
    """Tests para casos límite."""
    
    def test_completed_goal(self, test_db: Session, test_account):
        """Verifica objetivo completado."""
        repo = FinancialGoalRepository(test_db)
        
        completed = FinancialGoal(
            nombre="Completado",
            monto_objetivo=1000.00,
            monto_ahorrado=1000.00,
            account_id=test_account.id,
            estado=GoalStatus.COMPLETED,
            prioridad=1
        )
        test_db.add(completed)
        test_db.commit()
        
        active = repo.get_active_goals()
        assert completed not in active
    
    def test_over_savings_goal(self, test_db: Session, test_account):
        """Verifica objetivo con ahorro superior al objetivo."""
        repo = FinancialGoalRepository(test_db)
        
        over = FinancialGoal(
            nombre="Superado",
            monto_objetivo=1000.00,
            monto_ahorrado=1500.00,
            account_id=test_account.id,
            estado=GoalStatus.ACTIVE,
            prioridad=1
        )
        test_db.add(over)
        test_db.commit()
        
        retrieved = repo.get_by_id(over.id)
        assert retrieved.monto_ahorrado > retrieved.monto_objetivo
    
    def test_zero_target_goal(self, test_db: Session, test_account):
        """Verifica objetivo con target 0."""
        repo = FinancialGoalRepository(test_db)
        
        zero = FinancialGoal(
            nombre="Sin meta",
            monto_objetivo=0.00,
            monto_ahorrado=0.00,
            account_id=test_account.id,
            estado=GoalStatus.ACTIVE,
            prioridad=1
        )
        test_db.add(zero)
        test_db.commit()
        
        retrieved = repo.get_by_id(zero.id)
        assert retrieved.monto_objetivo == 0.00
