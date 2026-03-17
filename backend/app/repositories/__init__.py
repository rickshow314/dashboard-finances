"""
Repositorios para acceso a datos.

Los repositorios encapsulan la lógica de consultas a la base de datos,
permitiendo reutilización y facilidad de testing.
"""

from app.repositories.transaction_repository import TransactionRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.budget_repository import BudgetRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.recurring_repository import RecurringRepository
from app.repositories.goal_repository import FinancialGoalRepository

__all__ = [
    "TransactionRepository",
    "AccountRepository",
    "BudgetRepository",
    "CategoryRepository",
    "RecurringRepository",
    "FinancialGoalRepository",
]
