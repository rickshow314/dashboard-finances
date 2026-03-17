"""
Recurring Service - Lógica de negocio para gastos/ingresos recurrentes.

Orquesta operaciones entre repositorios y aplica reglas de negocio.
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.repositories.recurring_repository import RecurringRepository
from app.schemas.schemas import RecurringCreate, RecurringUpdate, RecurringResponse


class RecurringService:
    """Servicio para operaciones con recurrentes"""
    
    def __init__(self, db: Session):
        self.db = db
        self._recurring_repo = RecurringRepository(db)
    
    def create_recurring(self, data: RecurringCreate) -> Dict:
        """
        Crea un nuevo recurrente.
        
        Args:
            data: Schema con datos del recurrente
        
        Returns:
            Recurrente creado
        """
        recurring_dict = data.dict()
        recurring = self._recurring_repo.create(recurring_dict)
        
        return {
            "id": recurring.id,
            "nombre": recurring.nombre,
            "monto": float(recurring.monto),
            "tipo": recurring.tipo.value,
            "frecuencia": recurring.frecuencia.value,
            "created_at": recurring.created_at
        }
    
    def get_recurring(self, recurring_id: int) -> Optional[Dict]:
        """Obtiene un recurrente por ID"""
        recurring = self._recurring_repo.get_by_id(recurring_id)
        if recurring:
            return RecurringResponse.from_orm(recurring).dict()
        return None
    
    def get_all_recurring(self, limit: int = 1000) -> List[Dict]:
        """Obtiene todos los recurrentes activos formateados"""
        recurring_list = self._recurring_repo.get_all(limit=limit)
        return [
            {
                "id": r.id,
                "descripcion": r.descripcion,
                "monto": float(r.monto),
                "frecuencia": r.frecuencia,
                "tipo": r.tipo.value if hasattr(r.tipo, 'value') else str(r.tipo),
                "activo": bool(r.activo)
            }
            for r in recurring_list if r.activo
        ]
    
    def update_recurring(self, recurring_id: int, data: RecurringUpdate) -> Optional[Dict]:
        """Actualiza un recurrente"""
        recurring_dict = data.dict(exclude_unset=True)
        recurring = self._recurring_repo.update(recurring_id, recurring_dict)
        
        if recurring:
            return RecurringResponse.from_orm(recurring).dict()
        return None
    
    def delete_recurring(self, recurring_id: int) -> bool:
        """Elimina un recurrente"""
        return self._recurring_repo.delete(recurring_id)
    
    # ==================== SERVICIOS ANALÍTICOS ====================
    
    def get_monthly_projection(self) -> Dict:
        """
        Obtiene la proyección mensual de dinero basada en recurrentes.
        
        Returns:
            {
                "ingresos_proyectados": 5000.0,
                "gastos_proyectados": 2500.0,
                "balance_proyectado": 2500.0,
                "detalles_ingresos": [...],
                "detalles_gastos": [...]
            }
        """
        return self._recurring_repo.calculate_monthly_projection()
    
    def get_active_recurring_summary(self) -> Dict:
        """
        Obtiene resumen de recurrentes activos.
        
        Returns:
            {
                "total_ingresos": 10000.0,
                "total_gastos": 4000.0,
                "balance": 6000.0,
                "cantidad_activos": 15,
                "por_tipo": {
                    "ingresos": 3,
                    "gastos": 12
                }
            }
        """
        projection = self.monthly_projection = self._recurring_repo.calculate_monthly_projection()
        
        ingresos = self._recurring_repo.get_by_type("ingreso")
        gastos = self._recurring_repo.get_by_type("gasto")
        
        return {
            "total_ingresos": projection["ingresos_proyectados"],
            "total_gastos": projection["gastos_proyectados"],
            "balance": projection["balance_proyectado"],
            "cantidad_activos": len(ingresos) + len(gastos),
            "por_tipo": {
                "ingresos": len(ingresos),
                "gastos": len(gastos)
            },
            "proyeccion": projection
        }
    
    def get_soon_to_expire_alert(self) -> Dict:
        """
        Obtiene alerta de recurrentes próximos a vencer.
        
        Returns:
            {
                "pronto_a_vencer": [...],
                "cantidad": 3
            }
        """
        soon_to_expire = self._recurring_repo.get_soon_to_expire(days=30)
        
        return {
            "pronto_a_vencer": soon_to_expire,
            "cantidad": len(soon_to_expire)
        }
    
    def get_spending_breakdown(self) -> Dict:
        """
        Desglose de gastos recurrentes por categoría.
        
        Returns:
            {
                "total_gastos_recurrentes": 2500.0,
                "por_categoria": [
                    {"categoria": "Suscripciones", "monto": 50.0, "porcentaje": 2.0},
                    ...
                ]
            }
        """
        gastos = self._recurring_repo.get_by_type("gasto")
        
        # Agrupar por categoría
        por_categoria = {}
        for gasto in gastos:
            cat_name = gasto.category.nombre if gasto.category else "Sin categoría"
            
            if cat_name not in por_categoria:
                por_categoria[cat_name] = 0.0
            
            por_categoria[cat_name] += float(gasto.monto)
        
        total_gastos = sum(por_categoria.values())
        
        desglose = [
            {
                "categoria": cat,
                "monto": float(monto),
                "porcentaje": round((monto / total_gastos * 100) if total_gastos > 0 else 0, 2)
            }
            for cat, monto in por_categoria.items()
        ]
        
        # Ordenar por monto descendente
        desglose.sort(key=lambda x: x["monto"], reverse=True)
        
        return {
            "total_gastos_recurrentes": float(total_gastos),
            "cantidad_recurrentes": len(gastos),
            "por_categoria": desglose
        }
