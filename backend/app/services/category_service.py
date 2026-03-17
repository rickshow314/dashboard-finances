"""
Category Service - Lógica de negocio para categorías.

Orquesta operaciones entre repositorios y aplica reglas de negocio.
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.repositories.category_repository import CategoryRepository
from app.schemas.schemas import CategoryCreate, CategoryUpdate, CategoryResponse


class CategoryService:
    """Servicio para operaciones con categorías"""
    
    def __init__(self, db: Session):
        self.db = db
        self._category_repo = CategoryRepository(db)
    
    def create_category(self, data: CategoryCreate) -> Dict:
        """
        Crea una nueva categoría.
        
        Args:
            data: Schema con datos de la categoría
        
        Returns:
            Categoría creada
        """
        category_dict = data.dict()
        category = self._category_repo.create(category_dict)
        
        return {
            "id": category.id,
            "nombre": category.nombre,
            "tipo": category.tipo.value,
            "created_at": category.created_at
        }
    
    def get_category(self, category_id: int) -> Optional[Dict]:
        """Obtiene una categoría por ID"""
        category = self._category_repo.get_by_id(category_id)
        if category:
            return CategoryResponse.from_orm(category).dict()
        return None
    
    def get_all_categories(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Obtiene todas las categorías formateadas"""
        categories = self._category_repo.get_all(skip, limit)
        return [
            {
                "id": c.id,
                "nombre": c.nombre,
                "tipo": c.tipo.value if hasattr(c.tipo, 'value') else str(c.tipo)
            }
            for c in categories
        ]
    
    def update_category(self, category_id: int, data: CategoryUpdate) -> Optional[Dict]:
        """Actualiza una categoría"""
        category_dict = data.dict(exclude_unset=True)
        category = self._category_repo.update(category_id, category_dict)
        
        if category:
            return CategoryResponse.from_orm(category).dict()
        return None
    
    def delete_category(self, category_id: int) -> bool:
        """Elimina una categoría"""
        return self._category_repo.delete(category_id)
    
    # ==================== SERVICIOS ANALÍTICOS ====================
    
    def list_categories_by_type(self, category_type: str) -> List[Dict]:
        """
        Obtiene categorías listadas por tipo.
        
        Args:
            category_type: "ingreso" o "gasto"
        
        Returns:
            Lista de categorías del tipo
        """
        categories = self._category_repo.get_by_type(category_type)
        
        return [
            {
                "id": c.id,
                "nombre": c.nombre,
                "tipo": c.tipo.value,
                "created_at": c.created_at
            }
            for c in categories
        ]
    
    def get_expense_categories(self) -> List[Dict]:
        """Obtiene todas las categorías de gastos"""
        return self.list_categories_by_type("gasto")
    
    def get_income_categories(self) -> List[Dict]:
        """Obtiene todas las categorías de ingresos"""
        return self.list_categories_by_type("ingreso")
    
    def get_categories_dashboard(self) -> Dict:
        """
        Dashboard con información de categorías.
        
        Returns:
            {
                "total_categorias": 15,
                "categorias_gasto": 8,
                "categorias_ingreso": 7,
                "categorias_mas_usadas": [...],
                "categorias_sin_usar": [...]
            }
        """
        all_categories = self.category_repo.get_all(limit=1000)
        categories_with_count = self.category_repo.get_categories_with_transaction_count()
        unused = self.category_repo.get_unused_categories()
        
        expense_count = len(self.category_repo.get_expense_categories())
        income_count = len(self.category_repo.get_income_categories())
        
        top_5 = sorted(
            categories_with_count,
            key=lambda x: x["cantidad_transacciones"],
            reverse=True
        )[:5]
        
        return {
            "total_categorias": len(all_categories),
            "categorias_gasto": expense_count,
            "categorias_ingreso": income_count,
            "mas_usadas": top_5,
            "sin_usar": [
                {
                    "id": c.id,
                    "nombre": c.nombre,
                    "tipo": c.tipo.value
                }
                for c in unused
            ]
        }
