"""
Category Repository - Consultas específicas de categorías.

Métodos:
- Listar categorías por tipo
- Categorías con más transacciones
- Categorías sin usar
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import Category, Transaction


class CategoryRepository:
    """Repositorio para operaciones con categorías"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, category_id: int) -> Optional[Category]:
        """Obtiene una categoría por ID"""
        return self.db.query(Category).filter(Category.id == category_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """Obtiene todas las categorías"""
        return self.db.query(Category).offset(skip).limit(limit).all()
    
    def create(self, data: dict) -> Category:
        """Crea una nueva categoría"""
        category = Category(**data)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def update(self, category_id: int, data: dict) -> Optional[Category]:
        """Actualiza una categoría"""
        category = self.get_by_id(category_id)
        if category:
            for key, value in data.items():
                if value is not None:
                    setattr(category, key, value)
            self.db.commit()
            self.db.refresh(category)
        return category
    
    def delete(self, category_id: int) -> bool:
        """Elimina una categoría"""
        category = self.get_by_id(category_id)
        if category:
            self.db.delete(category)
            self.db.commit()
            return True
        return False
    
    # ==================== CONSULTAS ANALÍTICAS ====================
    
    def get_by_type(self, category_type: str) -> List[Category]:
        """
        Obtiene categorías por tipo (ingreso/gasto).
        
        Args:
            category_type: Tipo de categoría ("ingreso" o "gasto")
        
        Returns:
            Lista de categorías del tipo especificado
        """
        return self.db.query(Category).filter(
            Category.tipo == category_type
        ).order_by(Category.nombre).all()
    
    def get_categories_with_transaction_count(self) -> List[Dict]:
        """
        Obtiene categorías con el número de transacciones asociadas.
        
        Returns:
            [
                {"categoria_id": 1, "nombre": "Comida", "tipo": "gasto", "cantidad_transacciones": 45},
                ...
            ]
        """
        results = self.db.query(
            Category.id,
            Category.nombre,
            Category.tipo,
            func.count(Transaction.id).label("cantidad_transacciones")
        ).outerjoin(
            Transaction, Category.id == Transaction.categoria_id
        ).group_by(
            Category.id, Category.nombre, Category.tipo
        ).order_by(
            func.count(Transaction.id).desc()
        ).all()
        
        return [
            {
                "categoria_id": r.id,
                "nombre": r.nombre,
                "tipo": r.tipo.value,
                "cantidad_transacciones": r.cantidad_transacciones
            }
            for r in results
        ]
    
    def get_unused_categories(self) -> List[Category]:
        """
        Obtiene categorías que no tienen transacciones asociadas.
        
        Útil para limpiar categorías obsoletas.
        
        Returns:
            Lista de categorías sin transacciones
        """
        return self.db.query(Category).outerjoin(
            Transaction, Category.id == Transaction.categoria_id
        ).filter(
            Transaction.id.is_(None)
        ).all()
    
    def get_expense_categories(self) -> List[Category]:
        """Obtiene todas las categorías de gastos"""
        return self.get_by_type("gasto")
    
    def get_income_categories(self) -> List[Category]:
        """Obtiene todas las categorías de ingresos"""
        return self.get_by_type("ingreso")
