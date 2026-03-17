"""
ARQUITECTURA DE SERVICIOS Y REPOSITORIOS
=========================================

Esta documentación explica cómo funciona la arquitectura implementada
y cómo añadir nuevas consultas en el futuro.

## Estructura

backend/app/
├── repositories/              # Capa de acceso a datos
│   ├── base_repository.py    # Clase base con CRUD común
│   ├── transaction_repository.py
│   ├── account_repository.py
│   ├── budget_repository.py
│   └── __init__.py
├── services/                 # Capa de lógica de negocio
│   ├── transaction_service.py
│   ├── account_service.py
│   ├── budget_service.py
│   └── __init__.py
└── api/
    └── routers_analytics.py  # Endpoints que usan los servicios


## Flujo de Datos

Cliente HTTP
    ↓
[Endpoint en router_analytics.py]
    ↓
[Service] - Lógica de negocio
    ↓
[Repository] - Consultas a BD
    ↓
[Database]
    ↓
Response JSON


## Ventajas de esta Arquitectura

1. **Separación de Responsabilidades**
   - Repositories: Acceso a datos (queries)
   - Services: Lógica de negocio (validaciones, transformaciones)
   - Routers/Endpoints: Interfaz HTTP (entrada/salida)

2. **Reutilización**
   - Misma lógica usable desde múltiples endpoints
   - Tests pueden probar Services sin necesidad de BD

3. **Mantenibilidad**
   - Cambios en queries solo se hacen en repositories
   - Cambios en lógica solo se hacen en services
   - Cambios en API solo se hacen en routers

4. **Escalabilidad**
   - Fácil añadir nuevas consultas
   - Fácil añadir nuevos servicios
   - Fácil añadir nuevos endpoints


## Cómo Añadir una Nueva Consulta

### Ejemplo: "Total gastado en la última semana"

### Paso 1: Añadir método en Repository

```python
# app/repositories/transaction_repository.py

def get_last_week_expenses(self) -> float:
    \"\"\"Calcula gastos de la última semana\"\"\"
    from datetime import datetime, timedelta
    
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    result = self.db.query(
        func.sum(Transaction.cantidad)
    ).filter(
        and_(
            Transaction.fecha >= seven_days_ago,
            Transaction.tipo == "gasto"
        )
    ).scalar()
    
    return float(result) if result else 0.0
```

### Paso 2: Crear método en Service

```python
# app/services/transaction_service.py

def get_weekly_expense_summary(self) -> Dict:
    \"\"\"Resumen de gastos de la última semana\"\"\"
    last_week_expenses = self.transaction_repo.get_last_week_expenses()
    
    # Aquí puedes añadir lógica adicional
    # Por ejemplo, comparar con la semana anterior
    
    return {
        "gastos_ultima_semana": last_week_expenses,
        "periodo": "Últimos 7 días"
    }
```

### Paso 3: Crear Endpoint

```python
# app/api/routers_analytics.py

@router.get("/transactions/weekly-expenses", summary="Gastos de la última semana")
def get_weekly_expenses(db: Session = Depends(get_db)):
    service = TransactionService(db)
    return service.get_weekly_expense_summary()
```

Ahora está disponible en: `GET /api/v1/analytics/transactions/weekly-expenses`


## Consultas Implementadas

### Transacciones
- get_total_by_category() - Total por categoría
- get_by_month() - Transacciones del mes
- get_by_date_range() - Transacciones en período
- get_by_account() - Transacciones de una cuenta
- get_balance_summary() - Ingresos vs Gastos
- get_average_monthly_expense() - Promedio mensual
- get_top_categories() - Top N categorías

### Cuentas
- get_current_balance() - Saldo de una cuenta
- get_all_balances() - Saldos de todas
- get_total_balance() - Balance consolidado
- get_by_type() - Cuentas por tipo
- get_accounts_by_currency() - Cuentas por moneda

### Presupuestos
- get_active_budgets() - Presupuestos activos
- get_budget_vs_actual() - Presupuesto vs gasto real
- get_all_budgets_status() - Estado de todos
- get_budgets_in_alert() - Presupuestos en alerta
- get_exceeded_budgets() - Presupuestos excedidos


## Testing

Para testear sin BD, mockea el repository:

```python
from unittest.mock import Mock

def test_monthly_summary():
    mock_repo = Mock()
    mock_repo.get_by_month.return_value = [...]
    
    service = TransactionService(None)
    service.transaction_repo = mock_repo  # Reemplazar con mock
    
    result = service.get_monthly_summary(2025, 11)
    
    assert result['cantidad_transacciones'] == 5
```


## Siguientes Pasos

1. Integrar con el archivo principal (main.py)
2. Crear routers CRUD básicos para crear/actualizar/eliminar
3. Añadir más consultas analíticas (Recurring, FinancialGoal)
4. Implementar caché para consultas costosas
5. Añadir tests unitarios e integración
"""
