"""
Guía de Integración - Dashboard Financiero API

Este archivo proporciona una guía completa de cómo está estructurada
la aplicación y cómo verificar que todo funciona correctamente.
"""

## ✅ VERIFICACIÓN DE INTEGRACIÓN

### 1. Instalación de Dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configuración del Archivo .env

```env
# app/.env
APP_NAME=Dashboard Financiero
DEBUG=true
ENVIRONMENT=development

API_PREFIX=/api/v1
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

DATABASE_URL=sqlite:///./dashboard.db
# O para PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/dashboard

SECRET_KEY=tu-clave-secreta-aqui
ACCESS_TOKEN_EXPIRE_MINUTES=30

DEFAULT_CURRENCY=USD
DEFAULT_LANGUAGE=es
```

### 3. Ejecutar la Aplicación

```bash
# Desde la carpeta backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Output esperado:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

### 4. Verificar que está funcionando

```bash
# Health check
curl http://localhost:8000/health

# Ver documentación Swagger
curl http://localhost:8000/api/docs
```

---

## 📁 ESTRUCTURA DE CARPETAS

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    ← ARCHIVO PRINCIPAL (INTEGRADO)
│   │
│   ├── api/                       ← ROUTERS (ENDPOINTS)
│   │   ├── __init__.py
│   │   ├── routers_analytics.py           (12 endpoints)
│   │   ├── routers_accounts_transactions  (10 endpoints)
│   │   ├── routers_budgets.py             (6 endpoints)
│   │   ├── routers_crud.py                (21 endpoints)
│   │   └── routers_users.py               (legacy)
│   │
│   ├── core/                      ← CONFIGURACIÓN
│   │   ├── config.py              (Settings de la app)
│   │   └── security.py            (JWT, hash passwords)
│   │
│   ├── database/                  ← CAPA DE BD
│   │   ├── __init__.py
│   │   ├── models.py              (6 modelos SQLAlchemy)
│   │   └── database.py            (Conexión, sesiones)
│   │
│   ├── repositories/              ← ACCESO A DATOS
│   │   ├── __init__.py
│   │   ├── base_repository.py     (CRUD genérico)
│   │   ├── account_repository.py  (5 métodos)
│   │   ├── transaction_repository (7 métodos)
│   │   ├── budget_repository.py   (5 métodos)
│   │   ├── category_repository.py (5 métodos)
│   │   ├── recurring_repository.py (7 métodos)
│   │   └── goal_repository.py     (7 métodos)
│   │
│   ├── services/                  ← LÓGICA DE NEGOCIO
│   │   ├── __init__.py
│   │   ├── account_service.py     (4 métodos)
│   │   ├── transaction_service.py (4 métodos)
│   │   ├── budget_service.py      (4 métodos)
│   │   ├── category_service.py    (4 métodos)
│   │   ├── recurring_service.py   (5 métodos)
│   │   └── goal_service.py        (5 métodos)
│   │
│   ├── schemas/                   ← VALIDACIÓN
│   │   └── schemas.py             (18 schemas Pydantic)
│   │
│   └── utils/
│       └── (para funciones auxiliares)
│
├── tests/                         ← TESTS (FALTA IMPLEMENTAR)
│   ├── unit/
│   └── integration/
│
├── requirements.txt               ← DEPENDENCIAS
├── .env                          ← VARIABLES DE ENTORNO
└── README.md
```

---

## 🔄 FLUJO DE DATOS

### Ejemplo: Crear una Transacción

```
1. Cliente HTTP
   POST /api/v1/transactions
   {
     "cantidad": 50.0,
     "tipo": "gasto",
     "account_id": 1,
     "category_id": 2
   }

2. Endpoint (routers_accounts_transactions.py)
   create_transaction()
   ↓
   
3. Service (transaction_service.py)
   TransactionService.create_transaction()
   ↓
   
4. Repository (transaction_repository.py)
   TransactionRepository.create()
   ↓
   
5. Database (models.py)
   INSERT INTO transactions (...)
   ↓
   
6. Response
   {"id": 1, "cantidad": 50.0, ...}
```

---

## 📊 RESUMEN DE IMPLEMENTACIÓN

### Entidades Implementadas: 6
- Account (Cuentas)
- Category (Categorías)
- Transaction (Transacciones)
- Budget (Presupuestos)
- Recurring (Recurrentes)
- FinancialGoal (Objetivos)

### Total de Endpoints: 49
- 12 Analytics (análisis)
- 10 Accounts & Transactions (CRUD)
- 6 Budgets (CRUD)
- 21 Categories/Recurring/Goals (CRUD + Analytics)

### Métodos por Capa:
- Repositories: 37 métodos (consultas a BD)
- Services: 26 métodos (lógica de negocio)
- Endpoints: 49 (interfaz HTTP)

---

## 🚀 PRÓXIMOS PASOS

### Corto Plazo (Este Sprint):
- [ ] Tests unitarios para repositories
- [ ] Tests de integración para endpoints
- [ ] Validaciones de negocio en services

### Mediano Plazo:
- [ ] Autenticación JWT
- [ ] Roles y permisos (admin, user)
- [ ] Auditoria (quien cambió qué y cuándo)

### Largo Plazo:
- [ ] Caché con Redis
- [ ] Reportes PDF/Excel
- [ ] Notificaciones email
- [ ] Mobile app
- [ ] Machine Learning para análisis

---

## 🔧 TROUBLESHOOTING

### Error: "ModuleNotFoundError: No module named 'app'"

Solución:
```bash
# Asegúrate de estar en la carpeta backend
cd backend

# E instala en modo desarrollo
pip install -e .
```

### Error: "Database locked"

Solución (si usas SQLite):
```python
# En app/database/database.py, SQLite requiere:
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True  # Añade esto
)
```

### Error: "CORS error"

Solución: Verifica que BACKEND_CORS_ORIGINS esté configurado en .env

```env
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

---

## 📚 REFERENCIAS

- FastAPI Docs: https://fastapi.tiangolo.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Pydantic: https://docs.pydantic.dev/
- Clean Architecture: https://blog.cleancoder.com/
