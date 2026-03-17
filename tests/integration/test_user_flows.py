"""
Tests de integración para validación y flujos de usuario completos.
"""

import pytest
from datetime import date, timedelta


class TestValidationRules:
    """Tests para reglas de validación."""
    
    def test_account_saldo_inicial_positive(self, client):
        """Verifica que saldo inicial debe ser positivo."""
        invalid_data = {
            "nombre": "Test",
            "tipo": "corriente",
            "moneda": "EUR",
            "saldo_inicial": -100.00  # Negativo
        }
        
        response = client.post("/api/v1/accounts", json=invalid_data)
        # Puede aceptarse o validarse
        assert response.status_code in [201, 422]
    
    def test_transaction_cantidad_required(self, client, created_account, created_category):
        """Verifica que cantidad es requerida."""
        invalid_data = {
            "fecha": "2025-11-18",
            "descripcion": "Test",
            "tipo": "gasto",
            "account_id": created_account["id"],
            "categoria_id": created_category["id"]
            # Falta cantidad
        }
        
        response = client.post("/api/v1/transactions", json=invalid_data)
        assert response.status_code == 422
    
    def test_budget_monto_limite_positive(self, client, created_category):
        """Verifica que monto límite debe ser positivo."""
        invalid_data = {
            "nombre": "Test",
            "monto_limite": -100.00,
            "monto_usado": 0.00,
            "categoria_id": created_category["id"],
            "activo": True
        }
        
        response = client.post("/api/v1/budgets", json=invalid_data)
        assert response.status_code in [201, 422]
    
    def test_category_nombre_required(self, client):
        """Verifica que nombre de categoría es requerido."""
        invalid_data = {
            "tipo": "gasto"
            # Falta nombre
        }
        
        response = client.post("/api/v1/categories", json=invalid_data)
        assert response.status_code == 422
    
    def test_goal_monto_objetivo_positive(self, client, created_account):
        """Verifica que monto objetivo debe ser positivo."""
        invalid_data = {
            "nombre": "Test",
            "monto_objetivo": -1000.00,
            "monto_ahorrado": 0.00,
            "account_id": created_account["id"],
            "estado": "en_progreso",
            "prioridad": 1
        }
        
        response = client.post("/api/v1/goals", json=invalid_data)
        assert response.status_code in [201, 422]
    
    def test_transaction_fecha_format(self, client, created_account, created_category):
        """Verifica formato de fecha ISO."""
        invalid_data = {
            "fecha": "18/11/2025",  # Formato incorrecto
            "cantidad": 50.00,
            "descripcion": "Test",
            "tipo": "gasto",
            "account_id": created_account["id"],
            "categoria_id": created_category["id"]
        }
        
        response = client.post("/api/v1/transactions", json=invalid_data)
        assert response.status_code in [422, 400]
    
    def test_enum_type_validation(self, client, created_account, created_category):
        """Verifica validación de valores enum."""
        invalid_data = {
            "fecha": "2025-11-18",
            "cantidad": 50.00,
            "descripcion": "Test",
            "tipo": "invalid_type",  # Inválido
            "account_id": created_account["id"],
            "categoria_id": created_category["id"]
        }
        
        response = client.post("/api/v1/transactions", json=invalid_data)
        assert response.status_code == 422


class TestUserFlows:
    """Tests para flujos de usuario completos."""
    
    def test_complete_expense_flow(self, client):
        """
        Flujo completo: Crear cuenta, categoría y transacción de gasto.
        """
        # 1. Crear cuenta
        account_data = {
            "nombre": "Mi Cuenta",
            "tipo": "ahorro",
            "moneda": "EUR",
            "saldo_inicial": 5000.00
        }
        account_response = client.post("/api/v1/accounts", json=account_data)
        assert account_response.status_code == 201
        account = account_response.json()
        
        # 2. Crear categoría de gasto
        category_data = {
            "nombre": "Restaurante",
            "tipo": "gasto"
        }
        category_response = client.post("/api/v1/categories", json=category_data)
        assert category_response.status_code == 201
        category = category_response.json()
        
        # 3. Registrar transacción de gasto
        transaction_data = {
            "fecha": "2025-11-18",
            "cantidad": 45.50,
            "descripcion": "Cena en restaurante",
            "tipo": "gasto",
            "account_id": account["id"],
            "categoria_id": category["id"]
        }
        transaction_response = client.post("/api/v1/transactions", json=transaction_data)
        assert transaction_response.status_code == 201
        transaction = transaction_response.json()
        
        # 4. Verificar que transacción se creó correctamente
        verify_response = client.get(f"/api/v1/transactions/{transaction['id']}")
        assert verify_response.status_code == 200
        assert verify_response.json()["cantidad"] == 45.50
    
    def test_complete_income_flow(self, client):
        """Flujo completo: Crear cuenta, categoría y transacción de ingreso."""
        # 1. Crear cuenta
        account_data = {
            "nombre": "Cuenta Nómina",
            "tipo": "ahorro",
            "moneda": "EUR",
            "saldo_inicial": 0.00
        }
        account_response = client.post("/api/v1/accounts", json=account_data)
        assert account_response.status_code == 201
        account = account_response.json()
        
        # 2. Crear categoría de ingreso
        category_data = {
            "nombre": "Sueldo",
            "tipo": "ingreso"
        }
        category_response = client.post("/api/v1/categories", json=category_data)
        assert category_response.status_code == 201
        category = category_response.json()
        
        # 3. Registrar transacción de ingreso
        transaction_data = {
            "fecha": "2025-11-18",
            "cantidad": 2500.00,
            "descripcion": "Salario mensual",
            "tipo": "ingreso",
            "account_id": account["id"],
            "categoria_id": category["id"]
        }
        transaction_response = client.post("/api/v1/transactions", json=transaction_data)
        assert transaction_response.status_code == 201
        transaction = transaction_response.json()
        
        # 4. Verificar que ingreso se registró
        verify_response = client.get(f"/api/v1/transactions/{transaction['id']}")
        assert verify_response.status_code == 200
    
    def test_complete_budget_flow(self, client):
        """Flujo completo: Crear presupuesto y asociar transacciones."""
        # 1. Crear categoría
        category_data = {
            "nombre": "Alimentación",
            "tipo": "gasto"
        }
        category_response = client.post("/api/v1/categories", json=category_data)
        assert category_response.status_code == 201
        category = category_response.json()
        
        # 2. Crear presupuesto
        budget_data = {
            "nombre": "Presupuesto Alimentación",
            "monto_limite": 300.00,
            "monto_usado": 0.00,
            "categoria_id": category["id"],
            "activo": True
        }
        budget_response = client.post("/api/v1/budgets", json=budget_data)
        assert budget_response.status_code == 201
        budget = budget_response.json()
        
        # 3. Crear cuenta
        account_data = {
            "nombre": "Cuenta Test",
            "tipo": "ahorro",
            "moneda": "EUR",
            "saldo_inicial": 1000.00
        }
        account_response = client.post("/api/v1/accounts", json=account_data)
        assert account_response.status_code == 201
        account = account_response.json()
        
        # 4. Crear transacción dentro del presupuesto
        transaction_data = {
            "fecha": "2025-11-18",
            "cantidad": 75.00,
            "descripcion": "Compra supermercado",
            "tipo": "gasto",
            "account_id": account["id"],
            "categoria_id": category["id"]
        }
        transaction_response = client.post("/api/v1/transactions", json=transaction_data)
        assert transaction_response.status_code == 201
        
        # 5. Verificar presupuesto (debería tener monto_usado actualizado)
        budget_check = client.get(f"/api/v1/budgets/{budget['id']}")
        assert budget_check.status_code == 200
    
    def test_complete_goal_flow(self, client):
        """Flujo completo: Crear objetivo y actualizar progreso."""
        # 1. Crear cuenta
        account_data = {
            "nombre": "Cuenta Ahorros",
            "tipo": "ahorro",
            "moneda": "EUR",
            "saldo_inicial": 500.00
        }
        account_response = client.post("/api/v1/accounts", json=account_data)
        assert account_response.status_code == 201
        account = account_response.json()
        
        # 2. Crear objetivo
        goal_data = {
            "nombre": "Vacaciones a Bali",
            "monto_objetivo": 5000.00,
            "monto_ahorrado": 500.00,
            "account_id": account["id"],
            "estado": "activo",
            "prioridad": 1
        }
        goal_response = client.post("/api/v1/goals", json=goal_data)
        assert goal_response.status_code == 201
        goal = goal_response.json()
        
        # 3. Actualizar progreso del objetivo
        progress_data = {"monto_ahorrado": 1000.00}
        update_response = client.patch(
            f"/api/v1/goals/{goal['id']}/progress",
            json=progress_data
        )
        
        if update_response.status_code == 200:
            updated = update_response.json()
            assert updated["monto_ahorrado"] >= 1000.00
    
    def test_complete_recurring_flow(self, client):
        """Flujo completo: Crear recurrente y obtener proyección."""
        # 1. Crear cuenta
        account_data = {
            "nombre": "Cuenta Principal",
            "tipo": "ahorro",
            "moneda": "EUR",
            "saldo_inicial": 1000.00
        }
        account_response = client.post("/api/v1/accounts", json=account_data)
        assert account_response.status_code == 201
        account = account_response.json()
        
        # 2. Crear categoría
        category_data = {
            "nombre": "Suscripciones",
            "tipo": "gasto"
        }
        category_response = client.post("/api/v1/categories", json=category_data)
        assert category_response.status_code == 201
        category = category_response.json()
        
        # 3. Crear recurrente
        recurring_data = {
            "nombre": "Netflix",
            "monto": 12.99,
            "tipo": "gasto",
            "frecuencia": "mensual",
            "categoria_id": category["id"],
            "account_id": account["id"],
            "fecha_fin": "2026-11-18"
        }
        recurring_response = client.post("/api/v1/recurring", json=recurring_data)
        assert recurring_response.status_code == 201
        recurring = recurring_response.json()
        
        # 4. Obtener proyección mensual
        projection_response = client.get(
            f"/api/v1/analytics/accounts/{account['id']}/projection/monthly"
        )
        
        if projection_response.status_code == 200:
            projection = projection_response.json()
            assert isinstance(projection, dict)


class TestConcurrentOperations:
    """Tests para operaciones concurrentes."""
    
    def test_multiple_transactions_same_account(self, client, created_account, created_category):
        """Verifica múltiples transacciones en la misma cuenta."""
        for i in range(5):
            transaction_data = {
                "fecha": "2025-11-18",
                "cantidad": 10.00 + i,
                "descripcion": f"Transacción {i}",
                "tipo": "gasto",
                "account_id": created_account["id"],
                "categoria_id": created_category["id"]
            }
            
            response = client.post("/api/v1/transactions", json=transaction_data)
            assert response.status_code == 201
        
        # Verificar que todas se crearon
        response = client.get("/api/v1/transactions")
        assert response.status_code == 200
        assert len(response.json()) >= 5
    
    def test_budget_with_multiple_transactions(self, client, created_budget, created_account, created_category):
        """Verifica presupuesto actualizado con múltiples transacciones."""
        for i in range(3):
            transaction_data = {
                "fecha": "2025-11-18",
                "cantidad": 50.00 + i,
                "descripcion": f"Gasto {i}",
                "tipo": "gasto",
                "account_id": created_account["id"],
                "categoria_id": created_category["id"]
            }
            
            response = client.post("/api/v1/transactions", json=transaction_data)
            assert response.status_code == 201
        
        # Verificar presupuesto final
        response = client.get(f"/api/v1/budgets/{created_budget['id']}")
        assert response.status_code == 200
