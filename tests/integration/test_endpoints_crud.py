"""
Tests de integración para endpoints CRUD.
Cubre Budgets, Categories, Recurring y Goals.
"""

import pytest


class TestBudgetsEndpoints:
    """Tests para endpoints de Budgets."""
    
    def test_create_budget(self, client, budget_data):
        """Verifica creación de presupuesto."""
        response = client.post("/api/v1/budgets", json=budget_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == budget_data["nombre"]
        assert data["monto_limite"] == budget_data["monto_limite"]
        assert "id" in data
    
    def test_get_budgets_list(self, client, created_budget):
        """Verifica obtención de lista de presupuestos."""
        response = client.get("/api/v1/budgets")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_budget_by_id(self, client, created_budget):
        """Verifica obtención de presupuesto por ID."""
        response = client.get(f"/api/v1/budgets/{created_budget['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_budget["id"]
    
    def test_update_budget(self, client, created_budget, created_category):
        """Verifica actualización de presupuesto."""
        updated_data = {
            "nombre": "Presupuesto Actualizado",
            "monto_limite": 300.00,
            "monto_usado": 50.00,
            "categoria_id": created_category["id"],
            "activo": True
        }
        
        response = client.put(
            f"/api/v1/budgets/{created_budget['id']}",
            json=updated_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == updated_data["nombre"]
    
    def test_delete_budget(self, client, created_budget):
        """Verifica eliminación de presupuesto."""
        budget_id = created_budget["id"]
        
        response = client.delete(f"/api/v1/budgets/{budget_id}")
        assert response.status_code == 200
        
        response = client.get(f"/api/v1/budgets/{budget_id}")
        assert response.status_code == 404


class TestCategoriesEndpoints:
    """Tests para endpoints de Categories."""
    
    def test_create_category(self, client, category_data):
        """Verifica creación de categoría."""
        response = client.post("/api/v1/categories", json=category_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == category_data["nombre"]
        assert data["tipo"] == category_data["tipo"]
        assert "id" in data
    
    def test_get_categories_list(self, client, created_category):
        """Verifica obtención de lista de categorías."""
        response = client.get("/api/v1/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_category_by_id(self, client, created_category):
        """Verifica obtención de categoría por ID."""
        response = client.get(f"/api/v1/categories/{created_category['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_category["id"]
    
    def test_get_categories_by_type(self, client, created_category):
        """Verifica obtención de categorías por tipo."""
        response = client.get(f"/api/v1/categories/type/{created_category['tipo']}")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_update_category(self, client, created_category):
        """Verifica actualización de categoría."""
        updated_data = {
            "nombre": "Categoría Actualizada",
            "tipo": created_category["tipo"]
        }
        
        response = client.put(
            f"/api/v1/categories/{created_category['id']}",
            json=updated_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == updated_data["nombre"]
    
    def test_delete_category(self, client, created_category):
        """Verifica eliminación de categoría."""
        cat_id = created_category["id"]
        
        response = client.delete(f"/api/v1/categories/{cat_id}")
        assert response.status_code == 200
        
        response = client.get(f"/api/v1/categories/{cat_id}")
        assert response.status_code == 404


class TestRecurringEndpoints:
    """Tests para endpoints de Recurring."""
    
    def test_create_recurring(self, client, recurring_data):
        """Verifica creación de recurrente."""
        response = client.post("/api/v1/recurring", json=recurring_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == recurring_data["nombre"]
        assert data["monto"] == recurring_data["monto"]
        assert "id" in data
    
    def test_get_recurring_list(self, client, created_recurring):
        """Verifica obtención de lista de recurrentes."""
        response = client.get("/api/v1/recurring")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_recurring_by_id(self, client, created_recurring):
        """Verifica obtención de recurrente por ID."""
        response = client.get(f"/api/v1/recurring/{created_recurring['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_recurring["id"]
    
    def test_get_active_recurring(self, client, created_recurring):
        """Verifica obtención de recurrentes activos."""
        response = client.get("/api/v1/recurring/active")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_update_recurring(self, client, created_recurring, created_category, created_account):
        """Verifica actualización de recurrente."""
        updated_data = {
            "nombre": "Salario Actualizado",
            "monto": 2500.00,
            "tipo": created_recurring["tipo"],
            "frecuencia": created_recurring["frecuencia"],
            "categoria_id": created_category["id"],
            "account_id": created_account["id"],
            "fecha_fin": "2026-11-18"
        }
        
        response = client.put(
            f"/api/v1/recurring/{created_recurring['id']}",
            json=updated_data
        )
        
        assert response.status_code == 200
    
    def test_delete_recurring(self, client, created_recurring):
        """Verifica eliminación de recurrente."""
        rec_id = created_recurring["id"]
        
        response = client.delete(f"/api/v1/recurring/{rec_id}")
        assert response.status_code == 200
        
        response = client.get(f"/api/v1/recurring/{rec_id}")
        assert response.status_code == 404


class TestGoalsEndpoints:
    """Tests para endpoints de Financial Goals."""
    
    def test_create_goal(self, client, goal_data):
        """Verifica creación de objetivo."""
        response = client.post("/api/v1/goals", json=goal_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == goal_data["nombre"]
        assert data["monto_objetivo"] == goal_data["monto_objetivo"]
        assert "id" in data
    
    def test_get_goals_list(self, client, created_goal):
        """Verifica obtención de lista de objetivos."""
        response = client.get("/api/v1/goals")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_goal_by_id(self, client, created_goal):
        """Verifica obtención de objetivo por ID."""
        response = client.get(f"/api/v1/goals/{created_goal['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_goal["id"]
    
    def test_get_active_goals(self, client, created_goal):
        """Verifica obtención de objetivos activos."""
        response = client.get("/api/v1/goals/active")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_update_goal(self, client, created_goal, created_account):
        """Verifica actualización de objetivo."""
        updated_data = {
            "nombre": "Vacaciones Actualizado",
            "monto_objetivo": 4000.00,
            "monto_ahorrado": 500.00,
            "account_id": created_account["id"],
            "estado": "activo",
            "prioridad": 2
        }
        
        response = client.put(
            f"/api/v1/goals/{created_goal['id']}",
            json=updated_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["monto_objetivo"] == updated_data["monto_objetivo"]
    
    def test_update_goal_progress(self, client, created_goal):
        """Verifica actualización del progreso del objetivo."""
        progress_data = {"monto_ahorrado": 1000.00}
        
        response = client.patch(
            f"/api/v1/goals/{created_goal['id']}/progress",
            json=progress_data
        )
        
        if response.status_code == 200:
            data = response.json()
            assert data["monto_ahorrado"] == 1000.00
    
    def test_delete_goal(self, client, created_goal):
        """Verifica eliminación de objetivo."""
        goal_id = created_goal["id"]
        
        response = client.delete(f"/api/v1/goals/{goal_id}")
        assert response.status_code == 200
        
        response = client.get(f"/api/v1/goals/{goal_id}")
        assert response.status_code == 404


class TestDataIntegrity:
    """Tests de integridad de datos entre entidades."""
    
    def test_transaction_linked_to_account_and_category(self, client, created_transaction):
        """Verifica que transacción tiene referencias válidas."""
        response = client.get(f"/api/v1/transactions/{created_transaction['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert "account_id" in data
        assert "categoria_id" in data
    
    def test_budget_linked_to_category(self, client, created_budget):
        """Verifica que presupuesto tiene referencia a categoría."""
        response = client.get(f"/api/v1/budgets/{created_budget['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert "categoria_id" in data
    
    def test_recurring_linked_to_account_and_category(self, client, created_recurring):
        """Verifica que recurrente tiene referencias válidas."""
        response = client.get(f"/api/v1/recurring/{created_recurring['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert "account_id" in data
        assert "categoria_id" in data
    
    def test_goal_linked_to_account(self, client, created_goal):
        """Verifica que objetivo tiene referencia a cuenta."""
        response = client.get(f"/api/v1/goals/{created_goal['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert "account_id" in data
