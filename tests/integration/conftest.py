"""
Configuración para Integration Tests.
Proporciona cliente HTTP y base de datos para testing.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

import sys
import os

# Cargar variables de entorno antes de importar la aplicación
from dotenv import load_dotenv
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
sys.path.insert(0, backend_path)
env_file = os.path.join(backend_path, '.env')
load_dotenv(env_file, override=True)

from app.main import app
from app.database.models import Base
from app.database.database import get_db


@pytest.fixture(scope="function")
def test_db():
    """Crea BD SQLite en memoria para cada test."""
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
def client(test_db: Session):
    """
    Crea cliente HTTP TestClient con BD de prueba.
    Sobrescribe la dependencia get_db.
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def account_data():
    """Datos para crear una cuenta."""
    return {
        "nombre": "Cuenta Test",
        "tipo": "ahorro",
        "moneda": "EUR",
        "saldo_inicial": 1000.00
    }


@pytest.fixture(scope="function")
def created_account(client, account_data):
    """Crea una cuenta y la devuelve."""
    response = client.post("/api/v1/accounts", json=account_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture(scope="function")
def category_data():
    """Datos para crear una categoría."""
    return {
        "nombre": "Alimentación",
        "tipo": "gasto"
    }


@pytest.fixture(scope="function")
def created_category(client, category_data):
    """Crea una categoría y la devuelve."""
    response = client.post("/api/v1/categories", json=category_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture(scope="function")
def transaction_data(created_account, created_category):
    """Datos para crear una transacción."""
    return {
        "fecha": "2025-11-18",
        "cantidad": 50.00,
        "descripcion": "Gasto test",
        "tipo": "gasto",
        "account_id": created_account["id"],
        "categoria_id": created_category["id"]
    }


@pytest.fixture(scope="function")
def created_transaction(client, transaction_data):
    """Crea una transacción y la devuelve."""
    response = client.post("/api/v1/transactions", json=transaction_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture(scope="function")
def budget_data(created_category):
    """Datos para crear un presupuesto."""
    return {
        "nombre": "Presupuesto Test",
        "monto_limite": 200.00,
        "categoria_id": created_category["id"],
        "activo": True
    }


@pytest.fixture(scope="function")
def created_budget(client, budget_data):
    """Crea un presupuesto y lo devuelve."""
    response = client.post("/api/v1/budgets", json=budget_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture(scope="function")
def recurring_data(created_account, created_category):
    """Datos para crear un recurrente."""
    return {
        "nombre": "Salario Mensual",
        "monto": 2000.00,
        "tipo": "ingreso",
        "frecuencia": "mensual",
        "categoria_id": created_category["id"],
        "account_id": created_account["id"],
        "fecha_fin": "2026-11-18"
    }


@pytest.fixture(scope="function")
def created_recurring(client, recurring_data):
    """Crea un recurrente y lo devuelve."""
    response = client.post("/api/v1/recurring", json=recurring_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture(scope="function")
def goal_data(created_account):
    """Datos para crear un objetivo."""
    return {
        "nombre": "Vacaciones",
        "descripcion": "Objetivo de viaje",
        "monto_objetivo": 3000.00,
        "account_id": created_account["id"],
        "estado": "activo",
        "prioridad": 1
    }


@pytest.fixture(scope="function")
def created_goal(client, goal_data):
    """Crea un objetivo y lo devuelve."""
    response = client.post("/api/v1/goals", json=goal_data)
    assert response.status_code == 201
    return response.json()


# ==================== AUTENTICACIÓN ====================

@pytest.fixture(scope="function")
def registered_user(client):
    """Registra un usuario y lo devuelve con contraseña en plaintext para login."""
    user_data = {
        "email": "testuser@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    user_response = response.json()
    # Añadir password para uso en tests de login
    user_response["password"] = user_data["password"]
    return user_response


@pytest.fixture(scope="function")
def auth_token(client, registered_user):
    """Obtiene un token JWT válido para un usuario registrado."""
    login_data = {
        "email": registered_user["email"],
        "password": registered_user["password"]
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    # Validar que el token tiene la estructura esperada
    assert "access_token" in token_data
    assert "token_type" in token_data
    assert "expires_in" in token_data
    assert "user_id" in token_data
    
    return token_data


@pytest.fixture(scope="function")
def expired_token():
    """Crea un token JWT expirado para testing."""
    from datetime import datetime, timedelta
    from app.core.security import create_access_token
    
    # Crear un token con 0 segundos de expiración (ya está expirado)
    expired_time = timedelta(seconds=-1)
    token = create_access_token({"sub": "test_user"}, expired_time)
    return token
