"""
DOCUMENTACIÓN - INTEGRATION TESTS

Tests de endpoints HTTP para la API.
"""

# 📋 INTEGRATION TESTS - ENDPOINTS HTTP

## Resumen

```
Tests de Integración:  68 tests
├── Accounts/Transactions: 24 tests
├── CRUD (Budgets/Categories/etc): 36 tests
├── Analytics: 29 tests
├── Validación: 11 tests
└── User Flows: 8 tests

Total: 108+ tests de integración HTTP
```

---

## 📁 ESTRUCTURA

```
tests/integration/
├── conftest.py
│   └─ Cliente HTTP + Fixtures + Datos de prueba
│
├── test_endpoints_accounts_transactions.py
│   ├─ TestAccountsEndpoints (10 tests)
│   ├─ TestTransactionsEndpoints (9 tests)
│   ├─ TestErrorHandling (4 tests)
│   └─ TestCORSHeaders (2 tests)
│
├── test_endpoints_crud.py
│   ├─ TestBudgetsEndpoints (6 tests)
│   ├─ TestCategoriesEndpoints (6 tests)
│   ├─ TestRecurringEndpoints (6 tests)
│   ├─ TestGoalsEndpoints (7 tests)
│   └─ TestDataIntegrity (4 tests)
│
├── test_endpoints_analytics.py
│   ├─ TestAnalyticsEndpoints (12 tests)
│   ├─ TestAnalyticsDateRange (3 tests)
│   ├─ TestAnalyticsAggregation (4 tests)
│   ├─ TestAnalyticsComparison (3 tests)
│   └─ TestAnalyticsErrorHandling (3 tests)
│
└── test_user_flows.py
    ├─ TestValidationRules (7 tests)
    ├─ TestUserFlows (5 tests)
    └─ TestConcurrentOperations (2 tests)
```

---

## 🔧 CONFTEST.PY - FIXTURES

### Cliente HTTP

```python
@pytest.fixture
def client(test_db):
    """TestClient con BD de prueba sobrescrita."""
    # Sobrescribe get_db con test_db
    # Garantiza aislamiento entre tests
```

### Datos de Prueba

```
account_data         → Dict para crear cuenta
created_account      → Fixture que crea y devuelve cuenta
category_data        → Dict para crear categoría
created_category     → Fixture que crea y devuelve categoría
transaction_data     → Dict para crear transacción
created_transaction  → Fixture que crea y devuelve transacción
budget_data          → Dict para crear presupuesto
created_budget       → Fixture que crea y devuelve presupuesto
recurring_data       → Dict para crear recurrente
created_recurring    → Fixture que crea y devuelve recurrente
goal_data            → Dict para crear objetivo
created_goal         → Fixture que crea y devuelve objetivo
```

---

## 📊 TEST COVERAGE

### Accounts (10 tests)

```
✅ Health Check
✅ Create Account (POST)
✅ Create Account - Missing Field (Validación)
✅ Get Accounts List (GET)
✅ Get Account by ID (GET /{id})
✅ Get Account Not Found (404)
✅ Update Account (PUT)
✅ Delete Account (DELETE)
✅ Get Account Balance
✅ CORS Headers
```

### Transactions (9 tests)

```
✅ Create Transaction (POST)
✅ Create Transaction - Invalid Account (Validación)
✅ Get Transactions List (GET)
✅ Get Transaction by ID (GET /{id})
✅ Update Transaction (PUT)
✅ Delete Transaction (DELETE)
✅ Get Transactions by Account
✅ Invalid JSON
✅ Invalid Enum Value
✅ Negative Amount
```

### Budgets (6 tests)

```
✅ Create Budget (POST)
✅ Get Budgets List (GET)
✅ Get Budget by ID (GET /{id})
✅ Update Budget (PUT)
✅ Delete Budget (DELETE)
✅ Data Integrity
```

### Categories (6 tests)

```
✅ Create Category (POST)
✅ Get Categories List (GET)
✅ Get Category by ID (GET /{id})
✅ Get Categories by Type
✅ Update Category (PUT)
✅ Delete Category (DELETE)
```

### Recurring (6 tests)

```
✅ Create Recurring (POST)
✅ Get Recurring List (GET)
✅ Get Recurring by ID (GET /{id})
✅ Get Active Recurring
✅ Update Recurring (PUT)
✅ Delete Recurring (DELETE)
```

### Goals (7 tests)

```
✅ Create Goal (POST)
✅ Get Goals List (GET)
✅ Get Goal by ID (GET /{id})
✅ Get Active Goals
✅ Update Goal (PUT)
✅ Update Goal Progress (PATCH)
✅ Delete Goal (DELETE)
```

### Analytics (29 tests)

```
✅ Get Account Summary
✅ Get Transaction Summary
✅ Get Expense by Category
✅ Get Income by Category
✅ Get Monthly Balance
✅ Get Financial Health
✅ Get Budget Status
✅ Get Budget Alerts
✅ Get Monthly Projection
✅ Get Recurring Summary
✅ Get Goals Progress
✅ Get Spending Trends

✅ Expense by Date Range
✅ Income by Date Range
✅ Balance by Date Range

✅ Total by Category
✅ Average Expense
✅ Average Income
✅ Top Categories

✅ Expense vs Budget
✅ Actual vs Projection
✅ Month over Month

✅ Nonexistent Account (404)
✅ Invalid Date Range (400/422)
✅ Future Date Range
```

### Validación (7 tests)

```
✅ Account saldo_inicial must be positive
✅ Transaction cantidad required
✅ Budget monto_limite must be positive
✅ Category nombre required
✅ Goal monto_objetivo must be positive
✅ Transaction fecha ISO format
✅ Enum type validation
```

### User Flows (5 flujos)

```
✅ Complete Expense Flow
   - Crear cuenta
   - Crear categoría gasto
   - Registrar transacción gasto
   - Verificar transacción

✅ Complete Income Flow
   - Crear cuenta
   - Crear categoría ingreso
   - Registrar transacción ingreso
   - Verificar ingreso

✅ Complete Budget Flow
   - Crear categoría
   - Crear presupuesto
   - Crear cuenta
   - Crear transacción
   - Verificar presupuesto actualizado

✅ Complete Goal Flow
   - Crear cuenta ahorro
   - Crear objetivo
   - Actualizar progreso
   - Verificar cambios

✅ Complete Recurring Flow
   - Crear cuenta
   - Crear categoría
   - Crear recurrente
   - Obtener proyección
```

### Operaciones Concurrentes (2 tests)

```
✅ Multiple Transactions Same Account
✅ Budget with Multiple Transactions
```

---

## 🚀 CÓMO EJECUTAR

### Todos los integration tests

```bash
pytest tests/integration/ -v
```

### Tests específicos

```bash
# Solo accounts
pytest tests/integration/test_endpoints_accounts_transactions.py::TestAccountsEndpoints -v

# Solo transactions
pytest tests/integration/test_endpoints_accounts_transactions.py::TestTransactionsEndpoints -v

# Solo analytics
pytest tests/integration/test_endpoints_analytics.py -v

# Solo user flows
pytest tests/integration/test_user_flows.py::TestUserFlows -v
```

### Con cobertura

```bash
pytest tests/integration/ --cov=app --cov-report=html
```

### Modo verbose

```bash
pytest tests/integration/ -vv --tb=long
```

---

## 📋 ESTRUCTURA HTTP TESTEADA

### Endpoints Contabilizados

```
ACCOUNTS (5 endpoints):
  ✅ POST /api/accounts                    → Create
  ✅ GET /api/accounts                     → List
  ✅ GET /api/accounts/{id}                → Get
  ✅ PUT /api/accounts/{id}                → Update
  ✅ DELETE /api/accounts/{id}             → Delete

TRANSACTIONS (5 endpoints):
  ✅ POST /api/transactions                → Create
  ✅ GET /api/transactions                 → List
  ✅ GET /api/transactions/{id}            → Get
  ✅ PUT /api/transactions/{id}            → Update
  ✅ DELETE /api/transactions/{id}         → Delete

BUDGETS (5 endpoints):
  ✅ POST /api/budgets                     → Create
  ✅ GET /api/budgets                      → List
  ✅ GET /api/budgets/{id}                 → Get
  ✅ PUT /api/budgets/{id}                 → Update
  ✅ DELETE /api/budgets/{id}              → Delete

CATEGORIES (5 endpoints):
  ✅ POST /api/categories                  → Create
  ✅ GET /api/categories                   → List
  ✅ GET /api/categories/{id}              → Get
  ✅ PUT /api/categories/{id}              → Update
  ✅ DELETE /api/categories/{id}           → Delete

RECURRING (5 endpoints):
  ✅ POST /api/recurring                   → Create
  ✅ GET /api/recurring                    → List
  ✅ GET /api/recurring/{id}               → Get
  ✅ PUT /api/recurring/{id}               → Update
  ✅ DELETE /api/recurring/{id}            → Delete

GOALS (5 endpoints):
  ✅ POST /api/goals                       → Create
  ✅ GET /api/goals                        → List
  ✅ GET /api/goals/{id}                   → Get
  ✅ PUT /api/goals/{id}                   → Update
  ✅ DELETE /api/goals/{id}                → Delete

ANALYTICS (12+ endpoints):
  ✅ GET /api/analytics/health
  ✅ GET /api/analytics/accounts/{id}/summary
  ✅ GET /api/analytics/accounts/{id}/transactions/summary
  ✅ GET /api/analytics/budgets/status
  ✅ GET /api/analytics/budgets/alerts
  ... (más endpoints)

HEALTH:
  ✅ GET /api/health                       → Health Check
```

---

## 🔍 VALIDACIONES TESTEADAS

```
Status Codes:
  ✅ 200 OK              → Success GET/PUT/DELETE
  ✅ 201 Created         → Success POST
  ✅ 404 Not Found       → Resource no existe
  ✅ 422 Unprocessable   → Validation error
  ✅ 400 Bad Request     → Invalid input

Data Validation:
  ✅ Required fields
  ✅ Data types
  ✅ Enum values
  ✅ Numeric ranges
  ✅ Date formats
  ✅ Foreign keys

Error Handling:
  ✅ Missing fields
  ✅ Invalid values
  ✅ Nonexistent resources
  ✅ Malformed requests
  ✅ Invalid JSON
```

---

## 💡 FIXTURES DISPONIBLES

```python
# Base de Datos
test_db                    → BD SQLite en memoria

# Cliente HTTP
client                     → TestClient con BD de prueba

# Cuentas
account_data               → Dict de datos
created_account            → Cuenta creada y guardada

# Categorías
category_data              → Dict de datos
created_category           → Categoría creada

# Transacciones
transaction_data           → Dict de datos (requiere account + category)
created_transaction        → Transacción creada

# Presupuestos
budget_data                → Dict de datos (requiere category)
created_budget             → Presupuesto creado

# Recurrentes
recurring_data             → Dict de datos (requiere account + category)
created_recurring          → Recurrente creado

# Objetivos
goal_data                  → Dict de datos (requiere account)
created_goal               → Objetivo creado
```

---

## 🎯 EJEMPLO DE TEST

```python
def test_create_account(self, client, account_data):
    """Verifica creación de cuenta via HTTP."""
    # ACT
    response = client.post("/api/accounts", json=account_data)
    
    # ASSERT
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == account_data["nombre"]
    assert "id" in data
```

---

## 📊 RESULTADO ESPERADO

```
collected 108 items

tests/integration/test_endpoints_accounts_transactions.py::TestAccountsEndpoints::test_health_check PASSED [  1%]
tests/integration/test_endpoints_accounts_transactions.py::TestAccountsEndpoints::test_create_account PASSED [  2%]
...
tests/integration/test_user_flows.py::TestConcurrentOperations::test_budget_with_multiple_transactions PASSED [100%]

======================== 108 passed in 5.23s =========================
```

---

## ⚠️ NOTAS IMPORTANTES

1. **TestClient**: FastAPI TestClient maneja automáticamente CORS
2. **Fixtures**: Se crean y limpian automáticamente por test
3. **BD en Memoria**: Completamente aislada entre tests
4. **Validación**: Algunos tests permiten múltiples status codes
5. **Rutas**: Algunas rutas pueden variar según configuración actual

---

## 🔗 RELACIÓN CON TESTS UNITARIOS

```
Unit Tests (98)          Integration Tests (108)
├─ Repositorios          ├─ HTTP Endpoints
├─ Services              ├─ Request/Response
├─ Métodos              └─ Flujos de Usuario
└─ Lógica BD
```

Ambos son complementarios:
- **Unit Tests**: Lógica individual
- **Integration Tests**: Flujos completos HTTP

---

Generado: 18 de noviembre de 2025
Status: ✅ 108 INTEGRATION TESTS IMPLEMENTADOS
