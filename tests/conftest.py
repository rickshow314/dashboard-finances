"""
Configuration and fixtures para tests.
Proporciona base de datos en memoria y modelos de prueba.
"""

import pytest
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Cargar variables de entorno antes de importar la aplicación
import sys
import os
from pathlib import Path

# Añadir backend al path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

# Cargar .env desde el directorio backend
from dotenv import load_dotenv
env_file = os.path.join(backend_path, '.env')
load_dotenv(env_file, override=True)

# Ahora importar la aplicación
from app.database.models import Base, Account, Category, Transaction, Budget, Recurring, FinancialGoal
from app.database.models import AccountType, CurrencyType, TransactionType, CategoryType, RecurrenceFrequency, GoalStatus


@pytest.fixture(scope="function")
def test_db():
    """
    Crea una base de datos SQLite en memoria para cada test.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    yield db
    db.close()
    engine.dispose()


@pytest.fixture(scope="function")
def test_account(test_db: Session) -> Account:
    """Crea una cuenta de prueba."""
    account = Account(
        nombre="Cuenta Test",
        tipo=AccountType.CASH,
        moneda=CurrencyType.EUR,
        saldo_inicial=1000.00
    )
    test_db.add(account)
    test_db.commit()
    test_db.refresh(account)
    return account


@pytest.fixture(scope="function")
def test_account_savings(test_db: Session) -> Account:
    """Crea una cuenta de ahorro de prueba."""
    account = Account(
        nombre="Cuenta Ahorro",
        tipo=AccountType.SAVINGS,
        moneda=CurrencyType.EUR,
        saldo_inicial=5000.00
    )
    test_db.add(account)
    test_db.commit()
    test_db.refresh(account)
    return account


@pytest.fixture(scope="function")
def test_category_income(test_db: Session) -> Category:
    """Crea una categoría de ingresos."""
    category = Category(
        nombre="Sueldo",
        tipo=CategoryType.INCOME
    )
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)
    return category


@pytest.fixture(scope="function")
def test_category_expense(test_db: Session) -> Category:
    """Crea una categoría de gasto."""
    category = Category(
        nombre="Alimentación",
        tipo=CategoryType.EXPENSE
    )
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)
    return category


@pytest.fixture(scope="function")
def test_transaction(test_db: Session, test_account: Account, test_category_income: Category) -> Transaction:
    """Crea una transacción de prueba."""
    transaction = Transaction(
        fecha=date.today(),
        cantidad=2000.00,
        descripcion="Salario mensual",
        tipo=TransactionType.INCOME,
        account_id=test_account.id,
        categoria_id=test_category_income.id
    )
    test_db.add(transaction)
    test_db.commit()
    test_db.refresh(transaction)
    return transaction


@pytest.fixture(scope="function")
def test_transaction_expense(test_db: Session, test_account: Account, test_category_expense: Category) -> Transaction:
    """Crea una transacción de gasto."""
    transaction = Transaction(
        fecha=date.today(),
        cantidad=50.00,
        descripcion="Compra supermercado",
        tipo=TransactionType.EXPENSE,
        account_id=test_account.id,
        categoria_id=test_category_expense.id
    )
    test_db.add(transaction)
    test_db.commit()
    test_db.refresh(transaction)
    return transaction


@pytest.fixture(scope="function")
def test_budget(test_db: Session, test_category_expense: Category) -> Budget:
    """Crea un presupuesto de prueba."""
    budget = Budget(
        nombre="Presupuesto Alimentación",
        monto_limite=200.00,
        monto_usado=0.00,
        categoria_id=test_category_expense.id,
        activo=True
    )
    test_db.add(budget)
    test_db.commit()
    test_db.refresh(budget)
    return budget


@pytest.fixture(scope="function")
def test_recurring(test_db: Session, test_account: Account, test_category_income: Category) -> Recurring:
    """Crea un ingreso recurrente de prueba."""
    recurring = Recurring(
        nombre="Salario Mensual",
        monto=2000.00,
        tipo=TransactionType.INCOME,
        frecuencia=RecurrenceFrequency.MONTHLY,
        categoria_id=test_category_income.id,
        account_id=test_account.id,
        fecha_fin=date.today() + timedelta(days=365)
    )
    test_db.add(recurring)
    test_db.commit()
    test_db.refresh(recurring)
    return recurring


@pytest.fixture(scope="function")
def test_goal(test_db: Session, test_account: Account) -> FinancialGoal:
    """Crea un objetivo financiero de prueba."""
    goal = FinancialGoal(
        nombre="Ahorrar para vacaciones",
        monto_objetivo=3000.00,
        monto_ahorrado=500.00,
        account_id=test_account.id,
        estado=GoalStatus.ACTIVE,
        prioridad=1
    )
    test_db.add(goal)
    test_db.commit()
    test_db.refresh(goal)
    return goal


@pytest.fixture(scope="function")
def multiple_transactions(test_db: Session, test_account: Account, test_category_expense: Category) -> list:
    """Crea múltiples transacciones para pruebas de agregación."""
    transactions = []
    base_date = date.today()
    
    for i in range(10):
        tx = Transaction(
            fecha=base_date - timedelta(days=i),
            cantidad=10.00 + i,
            descripcion=f"Gasto {i}",
            tipo=TransactionType.EXPENSE,
            account_id=test_account.id,
            categoria_id=test_category_expense.id
        )
        test_db.add(tx)
        transactions.append(tx)
    
    test_db.commit()
    for tx in transactions:
        test_db.refresh(tx)
    
    return transactions


@pytest.fixture(scope="function")
def multiple_categories(test_db: Session) -> list:
    """Crea múltiples categorías para pruebas."""
    categories = []
    
    names = [
        ("Sueldo", CategoryType.INCOME),
        ("Freelance", CategoryType.INCOME),
        ("Comida", CategoryType.EXPENSE),
        ("Transporte", CategoryType.EXPENSE),
        ("Ocio", CategoryType.EXPENSE),
    ]
    
    for name, cat_type in names:
        cat = Category(nombre=name, tipo=cat_type)
        test_db.add(cat)
        categories.append(cat)
    
    test_db.commit()
    for cat in categories:
        test_db.refresh(cat)
    
    return categories
