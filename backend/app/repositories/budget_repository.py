"""
Budget Repository - Consultas específicas de presupuestos.

Métodos:
- Presupuesto vs gasto real
- Presupuestos activos
- Alertas de presupuesto (si se acerca al límite)
"""

from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import Budget, Transaction, Category


class BudgetRepository:
    """Repositorio para operaciones con presupuestos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, budget_id: int) -> Optional[Budget]:
        """Obtiene un presupuesto por ID"""
        return self.db.query(Budget).filter(Budget.id == budget_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Budget]:
        """Obtiene todos los presupuestos"""
        return self.db.query(Budget).offset(skip).limit(limit).all()
    
    def create(self, data: dict) -> Budget:
        """Crea un nuevo presupuesto"""
        budget = Budget(**data)
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget
    
    def update(self, budget_id: int, data: dict) -> Optional[Budget]:
        """Actualiza un presupuesto"""
        budget = self.get_by_id(budget_id)
        if budget:
            for key, value in data.items():
                if value is not None:
                    setattr(budget, key, value)
            self.db.commit()
            self.db.refresh(budget)
        return budget
    
    def delete(self, budget_id: int) -> bool:
        """Elimina un presupuesto"""
        budget = self.get_by_id(budget_id)
        if budget:
            self.db.delete(budget)
            self.db.commit()
            return True
        return False
    
    # ==================== CONSULTAS ANALÍTICAS ====================
    
    def get_active_budgets(self) -> List[Budget]:
        """
        Obtiene todos los presupuestos activos.
        
        Returns:
            Lista de presupuestos activos
        """
        return self.db.query(Budget).filter(Budget.activo == True).all()
    
    def get_budget_vs_actual(self, budget_id: int) -> Dict:
        """
        Compara presupuesto vs gasto real de una categoría.
        
        Args:
            budget_id: ID del presupuesto
        
        Returns:
            {
                "budget_id": 1,
                "categoria": "Comida",
                "monto_limite": 500.0,
                "gasto_actual": 350.75,
                "restante": 149.25,
                "porcentaje_usado": 70.15,
                "estado": "OK" | "ALERTA" | "EXCEDIDO"
            }
        """
        budget = self.get_by_id(budget_id)
        if not budget:
            return None
        
        # Calcular gasto actual en la categoría desde inicio de mes
        result = self.db.query(
            func.sum(Transaction.cantidad).label("total_gastado")
        ).filter(
            Transaction.categoria_id == budget.categoria_id
        ).first()
        
        # Prefer the stored `monto_usado` on the budget if present, otherwise compute from transactions
        gasto_actual = float(budget.monto_usado) if getattr(budget, 'monto_usado', None) else (float(result.total_gastado) if result.total_gastado else 0.0)
        monto_limite = float(budget.monto_limite)
        restante = monto_limite - gasto_actual
        porcentaje_usado = (gasto_actual / monto_limite * 100) if monto_limite > 0 else 0
        
        # Determinar estado
        if gasto_actual > monto_limite:
            estado = "EXCEDIDO"
        elif porcentaje_usado >= 80:
            estado = "ALERTA"
        else:
            estado = "OK"
        
        category = self.db.query(Category).filter(
            Category.id == budget.categoria_id
        ).first()
        
        return {
            "budget_id": budget.id,
            "nombre": budget.nombre,
            "categoria": category.nombre if category else "Desconocida",
            "categoria_id": budget.categoria_id,
            "monto_limite": monto_limite,
            "gasto_actual": gasto_actual,
            "restante": max(0, restante),
            "porcentaje_usado": round(porcentaje_usado, 2),
            "estado": estado
        }
    
    def get_all_budgets_status(self) -> List[Dict]:
        """
        Obtiene el estado de todos los presupuestos activos.
        
        Returns:
            [
                {"categoria": "Comida", "estado": "OK", "porcentaje_usado": 60.5},
                ...
            ]
        """
        active_budgets = self.get_active_budgets()
        statuses = []
        
        for budget in active_budgets:
            status = self.get_budget_vs_actual(budget.id)
            if status:
                statuses.append(status)
        
        return statuses
    
    def get_budgets_in_alert(self, threshold: float = 80.0) -> List[Dict]:
        """
        Obtiene presupuestos que están en alerta (por encima del threshold).
        
        Args:
            threshold: Porcentaje de límite alcanzado para alerta (default: 80%)
        
        Returns:
            Lista de presupuestos en alerta
        """
        all_budgets = self.get_all_budgets_status()
        
        return [
            b for b in all_budgets 
            if b["porcentaje_usado"] >= threshold
        ]
    
    def get_exceeded_budgets(self) -> List[Dict]:
        """
        Obtiene presupuestos que han sido excedidos.
        
        Returns:
            Lista de presupuestos excedidos
        """
        all_budgets = self.get_all_budgets_status()
        return [b for b in all_budgets if b["estado"] == "EXCEDIDO"]
