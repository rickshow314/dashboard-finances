"""
Tests para CategoryRepository.
Valida filtrado y agrupación de categorías.
"""

import pytest
from sqlalchemy.orm import Session
from app.repositories.category_repository import CategoryRepository
from app.database.models import Category, CategoryType


class TestCategoryRepositoryCRUD:
    """Tests para operaciones CRUD básicas."""
    
    def test_create_category(self, test_db: Session):
        """Verifica que se puede crear una categoría."""
        repo = CategoryRepository(test_db)
        
        created = repo.create({
            "nombre": "Nueva Categoría",
            "tipo": CategoryType.EXPENSE
        })
        assert created.id is not None
        assert created.nombre == "Nueva Categoría"
    
    def test_get_category_by_id(self, test_db: Session, test_category_expense):
        """Verifica que se puede recuperar una categoría por ID."""
        repo = CategoryRepository(test_db)
        
        retrieved = repo.get_by_id(test_category_expense.id)
        assert retrieved is not None
        assert retrieved.id == test_category_expense.id
    
    def test_update_category(self, test_db: Session, test_category_expense):
        """Verifica que se puede actualizar una categoría."""
        repo = CategoryRepository(test_db)
        
        updated = repo.update(test_category_expense.id, {"nombre": "Categoría Actualizada"})
        assert updated.nombre == "Categoría Actualizada"
    
    def test_delete_category(self, test_db: Session, test_category_expense):
        """Verifica que se puede eliminar una categoría."""
        repo = CategoryRepository(test_db)
        
        result = repo.delete(test_category_expense.id)
        assert result is True


class TestCategoryRepositorySpecialized:
    """Tests para consultas especializadas."""
    
    def test_get_by_type_expense(self, test_db: Session, test_category_expense):
        """Verifica filtrado por tipo de gasto."""
        repo = CategoryRepository(test_db)
        
        expenses = repo.get_by_type(CategoryType.EXPENSE)
        assert len(expenses) >= 1
        assert test_category_expense in expenses
    
    def test_get_by_type_income(self, test_db: Session, test_category_income):
        """Verifica filtrado por tipo de ingreso."""
        repo = CategoryRepository(test_db)
        
        incomes = repo.get_by_type(CategoryType.INCOME)
        assert len(incomes) >= 1
        assert test_category_income in incomes
    
    def test_get_expense_categories(self, test_db: Session, test_category_expense):
        """Verifica obtención de categorías de gasto."""
        repo = CategoryRepository(test_db)
        
        expenses = repo.get_expense_categories()
        assert len(expenses) >= 1
        assert test_category_expense in expenses
    
    def test_get_income_categories(self, test_db: Session, test_category_income):
        """Verifica obtención de categorías de ingreso."""
        repo = CategoryRepository(test_db)
        
        incomes = repo.get_income_categories()
        assert len(incomes) >= 1
        assert test_category_income in incomes
    
    def test_get_categories_with_transaction_count(self, test_db: Session):
        """Verifica conteo de transacciones por categoría."""
        repo = CategoryRepository(test_db)
        
        with_counts = repo.get_categories_with_transaction_count()
        assert isinstance(with_counts, list)
        # Puede estar vacío si no hay transacciones
    
    def test_get_unused_categories(self, test_db: Session, test_category_expense):
        """Verifica obtención de categorías sin transacciones."""
        repo = CategoryRepository(test_db)
        
        unused = repo.get_unused_categories()
        assert isinstance(unused, list)
        # En la fixture, test_category_expense no tiene transacciones
        assert test_category_expense in unused


class TestCategoryRepositoryEdgeCases:
    """Tests para casos límite."""
    
    def test_duplicate_category_names(self, test_db: Session):
        """Verifica creación de categorías con mismo nombre."""
        repo = CategoryRepository(test_db)
        
        created1 = repo.create({"nombre": "Duplicada", "tipo": CategoryType.EXPENSE})
        created2 = repo.create({"nombre": "Duplicada", "tipo": CategoryType.EXPENSE})
        
        # Ambas deberían crearse sin error
        assert created1.id != created2.id
    
    def test_empty_category_name(self, test_db: Session):
        """Verifica creación de categoría con nombre vacío."""
        repo = CategoryRepository(test_db)
        
        created = repo.create({"nombre": "", "tipo": CategoryType.EXPENSE})
        
        # Debería crearse (validación en API)
        assert created.id is not None
