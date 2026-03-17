"""
FinancialGoal Service - Lógica de negocio para objetivos financieros.

Orquesta operaciones entre repositorios y aplica reglas de negocio.
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.repositories.goal_repository import FinancialGoalRepository
from app.schemas.schemas import FinancialGoalCreate, FinancialGoalUpdate, FinancialGoalResponse


class FinancialGoalService:
    """Servicio para operaciones con objetivos financieros"""
    
    def __init__(self, db: Session):
        self.db = db
        self._goal_repo = FinancialGoalRepository(db)
    
    def create_goal(self, data: FinancialGoalCreate) -> Dict:
        """
        Crea un nuevo objetivo.
        
        Args:
            data: Schema con datos del objetivo
        
        Returns:
            Objetivo creado
        """
        goal_dict = data.dict()
        goal = self._goal_repo.create(goal_dict)
        
        return {
            "id": goal.id,
            "nombre": goal.nombre,
            "monto_objetivo": float(goal.monto_objetivo),
            "created_at": goal.created_at
        }
    
    def get_goal(self, goal_id: int) -> Optional[Dict]:
        """Obtiene un objetivo por ID"""
        goal = self._goal_repo.get_by_id(goal_id)
        if goal:
            return FinancialGoalResponse.from_orm(goal).dict()
        return None
    
    def get_all_goals(self, limit: int = 1000) -> List[Dict]:
        """Obtiene todos los objetivos formateados"""
        goals_list = self._goal_repo.get_all(limit=limit)
        return [
            {
                "id": g.id,
                "nombre": g.nombre,
                "monto_objetivo": float(g.monto_objetivo),
                "monto_ahorrado": float(g.monto_ahorrado or 0),
                "prioridad": g.prioridad,
                "fecha_objetivo": str(g.fecha_objetivo) if g.fecha_objetivo else None,
                "estado": g.estado.value if hasattr(g.estado, 'value') else str(g.estado)
            }
            for g in goals_list
        ]
    
    def update_goal(self, goal_id: int, data: FinancialGoalUpdate) -> Optional[Dict]:
        """Actualiza un objetivo"""
        goal_dict = data.dict(exclude_unset=True)
        goal = self._goal_repo.update(goal_id, goal_dict)
        
        if goal:
            return FinancialGoalResponse.from_orm(goal).dict()
        return None
    
    def delete_goal(self, goal_id: int) -> bool:
        """Elimina un objetivo"""
        return self._goal_repo.delete(goal_id)
    
    # ==================== SERVICIOS ANALÍTICOS ====================
    
    def get_all_goals_with_progress(self) -> List[Dict]:
        """
        Obtiene todos los objetivos con su progreso.
        
        Returns:
            [
                {
                    "id": 1,
                    "nombre": "Vacaciones",
                    "porcentaje": 60.0,
                    "monto_objetivo": 5000.0,
                    "monto_ahorrado": 3000.0,
                    ...
                },
                ...
            ]
        """
        return self._goal_repo.get_goals_with_progress()
    
    def get_active_goals(self) -> List[Dict]:
        """
        Obtiene solo los objetivos activos con progreso.
        
        Returns:
            Lista de objetivos activos ordenados por prioridad
        """
        goals = self._goal_repo.get_goals_with_progress()
        return [g for g in goals if g["estado"] == "activo"]
    
    def get_goals_dashboard(self) -> Dict:
        """
        Dashboard completo de objetivos.
        
        Returns:
            {
                "total_objetivos": 5,
                "objetivos_activos": 4,
                "objetivos_completados": 1,
                "progreso_general": 50.0,
                "total_ahorrado": 25000.0,
                "total_objetivo": 50000.0,
                "objetivos_por_hacer": [...],
                "casi_completados": [...],
                "vencidos": [...]
            }
        """
        all_goals = self._goal_repo.get_goals_with_progress()
        total_summary = self._goal_repo.get_total_savings_target()
        near_completion = self._goal_repo.get_near_completion(threshold=80)
        overdue = self._goal_repo.get_overdue_goals()
        
        active_goals = [g for g in all_goals if g["estado"] == "activo"]
        completed_goals = [g for g in all_goals if g["estado"] == "completado"]
        
        return {
            "total_objetivos": len(all_goals),
            "objetivos_activos": len(active_goals),
            "objetivos_completados": len(completed_goals),
            "progreso_general": total_summary["porcentaje_general"],
            "total_ahorrado": total_summary["total_ahorrado"],
            "total_objetivo": total_summary["total_objetivo"],
            "resumen": total_summary,
            "listado_activos": active_goals,
            "casi_completados": near_completion,
            "vencidos": overdue
        }
    
    def get_goals_by_priority(self) -> Dict:
        """
        Agrupa objetivos activos por prioridad.
        
        Returns:
            {
                "prioridad_5": [...],
                "prioridad_4": [...],
                ...
            }
        """
        all_goals = self._goal_repo.get_goals_with_progress()
        active_goals = [g for g in all_goals if g["estado"] == "activo"]
        
        by_priority = {}
        for priority in range(5, 0, -1):
            by_priority[f"prioridad_{priority}"] = [
                g for g in active_goals if g["prioridad"] == priority
            ]
        
        return by_priority
    
    def update_goal_progress(self, goal_id: int, amount_saved: float) -> Optional[Dict]:
        """
        Actualiza el progreso de un objetivo.
        
        Args:
            goal_id: ID del objetivo
            amount_saved: Cantidad adicional ahorrada
        
        Returns:
            Objetivo actualizado con nuevo progreso
        """
        goal = self.goal_repo.get_by_id(goal_id)
        
        if goal:
            new_amount = goal.monto_ahorrado + amount_saved
            
            # Verificar si se completó
            if new_amount >= goal.monto_objetivo:
                update_data = {
                    "monto_ahorrado": goal.monto_objetivo,
                    "estado": "completado"
                }
            else:
                update_data = {"monto_ahorrado": new_amount}
            
            goal = self.goal_repo.update(goal_id, update_data)
            return FinancialGoalResponse.from_orm(goal).dict()
        
        return None
