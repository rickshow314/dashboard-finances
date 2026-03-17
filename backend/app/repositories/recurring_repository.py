"""
Recurring Repository - Consultas específicas de gastos/ingresos recurrentes.

Métodos:
- Recurrentes activos
- Proyección de dinero mensual
- Cambios en recurrentes
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import Recurring, Category


class RecurringRepository:
    """Repositorio para operaciones con recurrentes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, recurring_id: int) -> Optional[Recurring]:
        """Obtiene un recurrente por ID"""
        return self.db.query(Recurring).filter(Recurring.id == recurring_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Recurring]:
        """Obtiene todos los recurrentes"""
        return self.db.query(Recurring).offset(skip).limit(limit).all()
    
    def create(self, data: dict) -> Recurring:
        """Crea un nuevo recurrente"""
        recurring = Recurring(**data)
        self.db.add(recurring)
        self.db.commit()
        self.db.refresh(recurring)
        return recurring
    
    def update(self, recurring_id: int, data: dict) -> Optional[Recurring]:
        """Actualiza un recurrente"""
        recurring = self.get_by_id(recurring_id)
        if recurring:
            for key, value in data.items():
                if value is not None:
                    setattr(recurring, key, value)
            self.db.commit()
            self.db.refresh(recurring)
        return recurring
    
    def delete(self, recurring_id: int) -> bool:
        """Elimina un recurrente"""
        recurring = self.get_by_id(recurring_id)
        if recurring:
            self.db.delete(recurring)
            self.db.commit()
            return True
        return False
    
    # ==================== CONSULTAS ANALÍTICAS ====================
    
    def get_active_recurring(self) -> List[Recurring]:
        """
        Obtiene todos los recurrentes activos.
        
        Returns:
            Lista de recurrentes activos
        """
        # Exclude those with fecha_fin in the past
        now = datetime.utcnow()
        return self.db.query(Recurring).filter(
            Recurring.activo == True,
            (Recurring.fecha_fin.is_(None)) | (Recurring.fecha_fin > now)
        ).order_by(Recurring.nombre).all()
    
    def get_by_type(self, recurring_type: str) -> List[Recurring]:
        """
        Obtiene recurrentes por tipo (ingreso/gasto).
        
        Args:
            recurring_type: "ingreso" o "gasto"
        
        Returns:
            Lista de recurrentes del tipo especificado
        """
        return self.db.query(Recurring).filter(
            Recurring.tipo == recurring_type,
            Recurring.activo == True
        ).all()
    
    def calculate_monthly_projection(self) -> Dict:
        """
        Calcula la proyección mensual basada en recurrentes activos.
        
        Returns:
            {
                "ingresos_proyectados": 5000.0,
                "gastos_proyectados": 2500.0,
                "balance_proyectado": 2500.0,
                "detalles_ingresos": [...],
                "detalles_gastos": [...]
            }
        """
        ingresos = self.db.query(
            func.sum(Recurring.monto).label("total")
        ).filter(
            Recurring.tipo == "ingreso",
            Recurring.activo == True
        ).scalar()
        
        gastos = self.db.query(
            func.sum(Recurring.monto).label("total")
        ).filter(
            Recurring.tipo == "gasto",
            Recurring.activo == True
        ).scalar()
        
        ingresos_total = float(ingresos) if ingresos else 0.0
        gastos_total = float(gastos) if gastos else 0.0
        
        # Detalles de ingresos
        detail_ingresos = self.db.query(
            Recurring.id,
            Recurring.nombre,
            Recurring.monto,
            Recurring.frecuencia
        ).filter(
            Recurring.tipo == "ingreso",
            Recurring.activo == True
        ).order_by(Recurring.monto.desc()).all()
        
        # Detalles de gastos
        detail_gastos = self.db.query(
            Recurring.id,
            Recurring.nombre,
            Recurring.monto,
            Recurring.frecuencia
        ).filter(
            Recurring.tipo == "gasto",
            Recurring.activo == True
        ).order_by(Recurring.monto.desc()).all()
        
        return {
            "ingresos_proyectados": ingresos_total,
            "gastos_proyectados": gastos_total,
            "balance_proyectado": ingresos_total - gastos_total,
            "detalles_ingresos": [
                {
                    "id": r.id,
                    "nombre": r.nombre,
                    "monto": float(r.monto),
                    "frecuencia": r.frecuencia.value
                }
                for r in detail_ingresos
            ],
            "detalles_gastos": [
                {
                    "id": r.id,
                    "nombre": r.nombre,
                    "monto": float(r.monto),
                    "frecuencia": r.frecuencia.value
                }
                for r in detail_gastos
            ]
        }
    
    def get_recurring_by_frequency(self, frequency: str) -> List[Recurring]:
        """
        Obtiene recurrentes por frecuencia.
        
        Args:
            frequency: "diaria", "semanal", "mensual", etc.
        
        Returns:
            Lista de recurrentes con esa frecuencia
        """
        return self.db.query(Recurring).filter(
            Recurring.frecuencia == frequency,
            Recurring.activo == True
        ).all()
    
    def get_recurring_by_category(self, category_id: int) -> List[Recurring]:
        """
        Obtiene recurrentes de una categoría específica.
        
        Args:
            category_id: ID de la categoría
        
        Returns:
            Lista de recurrentes de esa categoría
        """
        return self.db.query(Recurring).filter(
            Recurring.categoria_id == category_id,
            Recurring.activo == True
        ).all()
    
    def get_soon_to_expire(self, days: int = 30) -> List[Dict]:
        """
        Obtiene recurrentes que vencerán pronto.
        
        Args:
            days: Número de días a considerar (default: 30)
        
        Returns:
            Lista de recurrentes próximos a vencer
        """
        cutoff_date = datetime.utcnow() + timedelta(days=days)
        
        results = self.db.query(Recurring).filter(
            Recurring.fecha_fin.isnot(None),
            Recurring.fecha_fin <= cutoff_date,
            Recurring.fecha_fin > datetime.utcnow(),
            Recurring.activo == True
        ).order_by(Recurring.fecha_fin).all()
        
        return [
            {
                "id": r.id,
                "nombre": r.nombre,
                "monto": float(r.monto),
                "fecha_fin": r.fecha_fin,
                "dias_restantes": (r.fecha_fin - datetime.utcnow()).days
            }
            for r in results
        ]
