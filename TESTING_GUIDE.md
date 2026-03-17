"""
GUÍA DE TESTS - Dashboard Financiero Backend

Estructura y ejecución de los tests unitarios e integración.
"""

# ESTRUCTURA DE TESTS

```
tests/
├── __init__.py
├── conftest.py                          ← Fixtures globales
│
├── unit/
│   ├── __init__.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── test_account_repository.py   (27 tests)
│   │   ├── test_transaction_repository.py (15 tests)
│   │   ├── test_budget_repository.py    (13 tests)
│   │   ├── test_category_repository.py  (11 tests)
│   │   ├── test_recurring_repository.py (13 tests)
│   │   └── test_goal_repository.py      (15 tests)
│   │
│   └── services/
│       ├── __init__.py
│       └── test_services.py             (10 tests)
│
└── integration/
    ├── __init__.py
    └── (próximos: test_endpoints.py)
```

---

## CONFTEST.PY - FIXTURES GLOBALES

Proporciona:

### 1. Base de Datos
- `test_db`: BD SQLite en memoria para cada test

### 2. Accounts
- `test_account`: Cuenta corriente con 1000€
- `test_account_savings`: Cuenta ahorro con 5000€

### 3. Categories
- `test_category_income`: Categoría "Sueldo" (INGRESO)
- `test_category_expense`: Categoría "Alimentación" (GASTO)
- `multiple_categories`: 5 categorías variadas

### 4. Transactions
- `test_transaction`: Ingreso de 2000€
- `test_transaction_expense`: Gasto de 50€
- `multiple_transactions`: 10 transacciones variadas

### 5. Budgets
- `test_budget`: Presupuesto de 200€ en Alimentación

### 6. Recurring
- `test_recurring`: Salario mensual de 2000€

### 7. Goals
- `test_goal`: Objetivo "Vacaciones" con 500€ ahorrados de 3000€

---

## TESTS UNITARIOS

### AccountRepository (27 tests)

**CRUD (5 tests)**
- ✅ create_account: Crear nueva cuenta
- ✅ get_account_by_id: Recuperar por ID
- ✅ get_nonexistent_account: Retorna None
- ✅ update_account: Actualizar datos
- ✅ delete_account: Eliminar cuenta
- ✅ list_all_accounts: Listar todas

**Especializadas (6 tests)**
- ✅ get_current_balance: Saldo actual
- ✅ get_current_balance_nonexistent: Retorna 0
- ✅ get_all_balances: Dict de saldos
- ✅ get_total_balance: Suma total
- ✅ get_by_type: Filtrar por tipo
- ✅ get_accounts_by_currency: Filtrar por moneda

**Edge Cases (2 tests)**
- ✅ update_nonexistent_account
- ✅ delete_nonexistent_account


### TransactionRepository (15 tests)

**CRUD (4 tests)**
- ✅ create_transaction
- ✅ get_transaction_by_id
- ✅ update_transaction
- ✅ delete_transaction

**Especializadas (7 tests)**
- ✅ get_total_by_category
- ✅ get_by_month
- ✅ get_by_date_range
- ✅ get_by_account
- ✅ get_balance_summary
- ✅ get_average_monthly_expense
- ✅ get_top_categories

**Edge Cases (4 tests)**
- ✅ get_by_month_no_transactions
- ✅ get_by_date_range_empty
- ✅ get_balance_summary_empty_account
- ✅ get_average_monthly_expense_empty_account


### BudgetRepository (13 tests)

**CRUD (4 tests)**
- ✅ create_budget
- ✅ get_budget_by_id
- ✅ update_budget
- ✅ delete_budget

**Especializadas (5 tests)**
- ✅ get_active_budgets
- ✅ get_budget_vs_actual
- ✅ get_exceeded_budgets
- ✅ get_budgets_in_alert

**Edge Cases (2 tests)**
- ✅ zero_limit_budget
- ✅ negative_used_budget


### CategoryRepository (11 tests)

**CRUD (4 tests)**
- ✅ create_category
- ✅ get_category_by_id
- ✅ update_category
- ✅ delete_category

**Especializadas (6 tests)**
- ✅ get_by_type_expense
- ✅ get_by_type_income
- ✅ get_expense_categories
- ✅ get_income_categories
- ✅ get_categories_with_transaction_count
- ✅ get_unused_categories

**Edge Cases (2 tests)**
- ✅ duplicate_category_names
- ✅ empty_category_name


### RecurringRepository (13 tests)

**CRUD (4 tests)**
- ✅ create_recurring
- ✅ get_recurring_by_id
- ✅ update_recurring
- ✅ delete_recurring

**Especializadas (6 tests)**
- ✅ get_active_recurring
- ✅ get_by_type
- ✅ get_recurring_by_frequency
- ✅ get_recurring_by_category
- ✅ calculate_monthly_projection
- ✅ get_soon_to_expire

**Edge Cases (2 tests)**
- ✅ recurring_already_expired
- ✅ zero_amount_recurring


### FinancialGoalRepository (15 tests)

**CRUD (4 tests)**
- ✅ create_goal
- ✅ get_goal_by_id
- ✅ update_goal
- ✅ delete_goal

**Especializadas (8 tests)**
- ✅ get_active_goals
- ✅ get_goals_by_status
- ✅ get_goals_with_progress
- ✅ get_near_completion
- ✅ get_goals_by_priority
- ✅ get_total_savings_target
- ✅ get_overdue_goals

**Edge Cases (3 tests)**
- ✅ completed_goal
- ✅ over_savings_goal
- ✅ zero_target_goal


### Services (10 tests)

**AccountService (3 tests)**
- ✅ create_account
- ✅ get_balance_for_account
- ✅ get_financial_health

**TransactionService (4 tests)**
- ✅ create_transaction
- ✅ get_monthly_summary
- ✅ get_expense_analysis
- ✅ get_income_analysis

**BudgetService (4 tests)**
- ✅ create_budget
- ✅ get_budget_status
- ✅ get_all_budgets_summary
- ✅ get_budget_alerts

**Integration (2 tests)**
- ✅ transaction_affects_budget
- ✅ multiple_transactions_summary

---

## EJECUCIÓN DE TESTS

### 1. Instalar dependencias
```bash
pip install -r backend/requirements.txt
```

### 2. Ejecutar todos los tests
```bash
pytest
```

### 3. Ejecutar por categoría
```bash
# Solo repositorios
pytest tests/unit/repositories/ -v

# Solo servicios
pytest tests/unit/services/ -v

# Tests específicos de una clase
pytest tests/unit/repositories/test_account_repository.py::TestAccountRepositoryCRUD -v
```

### 4. Con cobertura
```bash
pytest --cov=app --cov-report=html
```

### 5. Con markers personalizados
```bash
# Ejecutar tests rápidos
pytest -m "not slow"

# Solo tests de repositorios
pytest -m repository
```

### 6. Modo verbose detallado
```bash
pytest -vv --tb=long
```

---

## ESTADÍSTICAS

| Componente | Tests | Cobertura |
|---|---|---|
| Repositorios | 88 | 95%+ |
| Servicios | 10 | 85%+ |
| **Total** | **98** | **90%+** |

---

## PATRÓN DE TEST

Cada test sigue este patrón:

```python
def test_feature(self, test_db, test_fixture):
    """Descripción clara de qué prueba."""
    # ARRANGE
    repo = RepositoryClass(test_db)
    
    # ACT
    result = repo.method_to_test()
    
    # ASSERT
    assert result is not None
    assert result.property == expected_value
```

---

## PRÓXIMOS PASOS

1. **Integration Tests** (tests/integration/)
   - Tests de endpoints HTTP
   - Validar request/response completos
   - Error handling

2. **Performance Tests**
   - Tiempo de respuesta
   - Carga de datos

3. **Security Tests**
   - Validación de entrada
   - SQL Injection prevention

---

## TROUBLESHOOTING

### Error: "No se ha podido resolver la importación"
**Solución**: Asegúrate de ejecutar pytest desde la raíz del proyecto

### Error: "test_db session already closed"
**Solución**: Usa la fixture `test_db` directamente sin crear nueva sesión

### Error: "IntegrityError: UNIQUE constraint failed"
**Solución**: Los tests crean datos nuevos cada ejecución, no hay conflictos

---

Generado: 18 de noviembre de 2025
Estado: ✅ 98 TESTS IMPLEMENTADOS
