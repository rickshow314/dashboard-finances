# 🏗️ Backend Architecture

Design overview and guidelines for the backend service layer.

## Layered Architecture

```
┌─────────────────────────────────┐
│     HTTP Routers (FastAPI)      │  api/routers_*.py
│     - Request validation        │
│     - Response formatting       │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│     Services (Business Logic)   │  services/
│     - Validations              │
│     - Calculations             │
│     - Coordination             │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  Repositories (Data Access)     │  repositories/
│     - Database queries         │
│     - ORM operations           │
│     - Filtering & sorting      │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  SQLAlchemy Models & Database   │  database/
│     - ORM definitions          │
│     - Schema validation        │
│     - Relationships            │
└─────────────────────────────────┘
```

---

## Directory Structure

```
backend/app/
├── api/
│   ├── routers_auth.py          # Authentication endpoints
│   ├── routers_accounts_transactions.py
│   ├── routers_crud.py          # CRUD for budgets, goals, etc
│   ├── routers_analytics.py     # Analytics endpoints
│   └── routers_budgets.py       # Budget-specific endpoints
│
├── core/
│   ├── config.py                # Environment & settings
│   └── security.py              # JWT & password hashing
│
├── database/
│   ├── database.py              # Session management
│   ├── models.py                # SQLAlchemy ORM models
│   └── enums.py (in models)     # Account types, etc
│
├── repositories/
│   ├── base_repository.py       # Common CRUD operations
│   ├── account_repository.py
│   ├── transaction_repository.py
│   ├── budget_repository.py
│   ├── category_repository.py
│   ├── recurring_repository.py
│   ├── goal_repository.py
│   └── user_repository.py
│
├── services/
│   ├── account_service.py
│   ├── transaction_service.py
│   ├── budget_service.py
│   ├── category_service.py
│   ├── recurring_service.py
│   ├── goal_service.py
│   └── user_service.py
│
├── schemas/
│   ├── auth.py                  # Auth request/response schemas
│   └── schemas.py               # CRUD schemas
│
└── main.py                       # FastAPI app setup
```

---

## Key Design Decisions

### 1. Repository Pattern
- Each model has a dedicated repository class
- Repositories inherit from `BaseRepository` for common CRUD
- Methods accept dicts for create/update (flexible)
- Return ORM instances or dicts as appropriate

**Example:**
```python
# In repository
def create(self, data: dict) -> Account:
    account = Account(**data)
    self.db.add(account)
    self.db.commit()
    self.db.refresh(account)
    return account
```

### 2. Service Layer
- Services delegate data access to repositories
- Services handle business logic (validations, calculations)
- Services coordinate between multiple repositories
- Public methods only (repositories are private detail)

**Example:**
```python
# In service
def get_financial_health(self) -> dict:
    total_balance = self.account_repo.get_total_balance()
    total_accounts = len(self.account_repo.get_all())
    return {
        'total_balance': total_balance['saldo_total'],
        'total_accounts': total_accounts,
        ...
    }
```

### 3. Router/Endpoint Pattern
- Routers call services (not repositories directly)
- Routers handle HTTP concerns (status codes, errors)
- Routers validate request data via schemas
- Routers transform responses for clients

**Example:**
```python
# In router
@router.get("/accounts/{account_id}")
async def get_account(account_id: int, db: Session = Depends(get_db)):
    service = AccountService(db)
    account = service.get_by_id(account_id)
    if not account:
        raise HTTPException(status_code=404)
    return account
```

---

## Database Models

### Core Enums
- `AccountType`: CASH, SAVINGS, CHECKING
- `CurrencyType`: EUR, USD, GBP
- `TransactionType`: INCOME, EXPENSE
- `CategoryType`: INCOME, EXPENSE
- `RecurrenceFrequency`: DAILY, WEEKLY, MONTHLY, YEARLY
- `GoalStatus`: ACTIVE, COMPLETED, CANCELLED

### Relationships
```
User
  └─ Account (1:M)
      ├─ Transaction (1:M)
      ├─ Budget (1:M)
      ├─ Recurring (1:M)
      └─ FinancialGoal (1:M)

Category (1:M)
  └─ Transaction
  └─ Budget
  └─ Recurring
```

---

## Adding New Features

### Add a New Endpoint

1. **Create schema** (if needed)
   ```python
   # schemas/schemas.py
   class NewItemCreate(BaseModel):
       field1: str
       field2: int
   ```

2. **Add repository method**
   ```python
   # repositories/new_repository.py
   def custom_query(self) -> List[NewItem]:
       return self.db.query(NewItem).filter(...).all()
   ```

3. **Add service method**
   ```python
   # services/new_service.py
   def get_custom_data(self) -> dict:
       items = self.repo.custom_query()
       # Process/transform
       return result
   ```

4. **Add router endpoint**
   ```python
   # api/routers_new.py
   @router.get("/new")
   async def list_new(db: Session = Depends(get_db)):
       service = NewService(db)
       return service.get_custom_data()
   ```

### Add a New Repository Method

Follow these patterns:

```python
# Simple CRUD
def create(self, data: dict) -> Item:
    pass

def get_by_id(self, item_id: int) -> Optional[Item]:
    pass

def update(self, item_id: int, data: dict) -> Optional[Item]:
    pass

def delete(self, item_id: int) -> bool:
    pass

# Specialized queries
def get_by_status(self, status: str) -> List[Item]:
    pass

def get_total(self) -> dict:
    pass
```

---

## Data Flow Example

### Request: Create a Transaction

```
POST /api/v1/transactions
{
    "fecha": "2025-11-18",
    "cantidad": 50.00,
    "tipo": "gasto",
    "account_id": 1,
    "categoria_id": 2
}

    ↓ Validation via TransactionCreate schema

[Router: routers_accounts_transactions.py]
    - Validates input
    - Calls TransactionService

[Service: transaction_service.py]
    - Validates business rules
    - Calls TransactionRepository

[Repository: transaction_repository.py]
    - Creates ORM instance
    - Commits to database
    - Returns created instance

[Router Response: 201 Created]
{
    "id": 123,
    "fecha": "2025-11-18",
    "cantidad": 50.00,
    "tipo": "gasto",
    "account_id": 1,
    "categoria_id": 2,
    "created_at": "2025-11-18T10:00:00"
}
```

---

## Authentication & Security

### JWT Token Flow
1. User registers → password hashed with bcrypt
2. User logs in → JWT token issued (30 min expiry)
3. Protected endpoints check token header
4. Token decoded, user identified

### Protected Routes
```python
from app.core.security import verify_token

@router.get("/me")
async def get_current_user(
    token: str = Header(...),
    db: Session = Depends(get_db)
):
    user = verify_token(token)
    return user
```

---

## Testing Strategy

### Unit Tests (tests/unit/)
- Test repositories with in-memory SQLite
- Test services in isolation
- Mock external dependencies
- Focus on data access and business logic

### Integration Tests (tests/integration/)
- Test full request/response cycle
- Use TestClient with in-memory DB
- Verify endpoint behavior
- Test error handling

### Running Tests
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Coverage report
pytest --cov=app --cov-report=html
```

---

## Performance Considerations

1. **Database Queries**
   - Use eager loading when needed (`joinedload`)
   - Avoid N+1 queries
   - Index frequently queried columns

2. **API Response**
   - Paginate large result sets
   - Return only needed fields
   - Cache when appropriate

3. **Business Logic**
   - Move heavy calculations to background tasks
   - Use database aggregations where possible
   - Cache computed values

---

## Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Implement feature**
   - Add repository methods
   - Add service logic
   - Add router endpoint
   - Add tests

3. **Test locally**
   ```bash
   pytest tests/ -v
   ```

4. **Commit & push**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/new-feature
   ```

5. **Create PR & review**

---

For more details on testing, see [TESTING.md](TESTING.md).
