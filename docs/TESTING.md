# 🧪 Testing Guide

Complete guide to running and understanding the test suite.

## Quick Start

```bash
# Activate Python environment
backend\venv\Scripts\activate

# Run all tests
python -m pytest -q

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/unit/repositories/test_account_repository.py

# Run tests matching a pattern
python -m pytest -k "account" -v
```

---

## Test Structure

```
tests/
├── conftest.py                    # Global fixtures
├── unit/
│   ├── repositories/              # Repository tests (7 test files)
│   │   ├── test_account_repository.py
│   │   ├── test_transaction_repository.py
│   │   ├── test_budget_repository.py
│   │   ├── test_category_repository.py
│   │   ├── test_recurring_repository.py
│   │   ├── test_goal_repository.py
│   │   └── test_user_repository.py
│   │
│   └── services/                  # Service tests
│       └── test_services.py
│
└── integration/                   # Integration tests
    ├── conftest.py               # HTTP client & fixtures
    └── test_endpoints_*.py       # API endpoint tests
```

---

## Fixtures (conftest.py)

### Database
- `test_db`: SQLite in-memory database for each test

### Models
- `test_account`: Cash account with €1,000
- `test_account_savings`: Savings account with €5,000
- `test_category_income`: "Salary" income category
- `test_category_expense`: "Food" expense category
- `test_transaction`: €2,000 income transaction
- `test_transaction_expense`: €50 expense transaction
- `test_budget`: €200 budget for Food category
- `test_recurring`: €2,000 monthly salary
- `test_goal`: €3,000 vacation goal with €500 saved
- `multiple_transactions`: 10 varied transactions
- `multiple_categories`: 5 varied categories

---

## Unit Tests

### AccountRepository (27 tests)

**CRUD Operations**
- ✅ Create account
- ✅ Get by ID
- ✅ Update account
- ✅ Delete account
- ✅ List all accounts

**Specialized Queries**
- ✅ Get current balance
- ✅ Get all balances
- ✅ Get total balance
- ✅ Filter by account type
- ✅ Filter by currency

**Edge Cases**
- ✅ Non-existent account handling

### TransactionRepository (15 tests)

**CRUD Operations**
- ✅ Create transaction
- ✅ Get by ID
- ✅ Update transaction
- ✅ Delete transaction

**Specialized Queries**
- ✅ Total by category
- ✅ Get by month
- ✅ Get by date range
- ✅ Get by account
- ✅ Balance summary
- ✅ Average monthly expense
- ✅ Top categories

**Edge Cases**
- ✅ Empty month handling
- ✅ Empty date range handling
- ✅ Empty account handling

### BudgetRepository (13 tests)

**CRUD Operations**
- ✅ Create budget
- ✅ Get by ID
- ✅ Update budget
- ✅ Delete budget

**Specialized Queries**
- ✅ Active budgets
- ✅ Budget vs actual
- ✅ Exceeded budgets
- ✅ Budgets in alert (>80%)

### CategoryRepository (11 tests)

**CRUD Operations**
- ✅ Create category
- ✅ Get by ID
- ✅ Update category
- ✅ Delete category

**Specialized Queries**
- ✅ Filter by type
- ✅ Expense categories
- ✅ Income categories
- ✅ Categories with counts
- ✅ Unused categories

### OtherRepositories

**RecurringRepository** (13 tests)
- Create, read, update, delete recurring transactions
- Active/inactive recurring
- Filter by frequency and category
- Soon-to-expire detection

**GoalRepository** (15 tests)
- Create, read, update, delete goals
- Filter by status and priority
- Near completion detection
- Overdue goals

**Services** (10 tests)
- Account service
- Transaction service
- Budget service integration

---

## Integration Tests

### Endpoints Tested

**Accounts**
- POST /api/v1/accounts (create)
- GET /api/v1/accounts (list)
- GET /api/v1/accounts/{id} (read)
- PUT /api/v1/accounts/{id} (update)
- DELETE /api/v1/accounts/{id} (delete)

**Transactions**
- Similar CRUD operations
- Filtering by account and date

**Budgets, Categories, Recurring, Goals**
- Full CRUD operations
- Status filtering
- Specialized queries

**Authentication**
- Register user
- Login (JWT token)
- Get current user
- Change password

**Analytics**
- Monthly summary
- Expense analysis
- Income analysis
- Budget comparisons

---

## Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

---

## Running Tests

### All Tests
```bash
python -m pytest -q
```
Output: `205 passed in ~11s`

### By Category
```bash
# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only  
python -m pytest tests/integration/ -v

# Repository tests
python -m pytest tests/unit/repositories/ -v

# Service tests
python -m pytest tests/unit/services/ -v
```

### With Markers
```bash
# Run only integration tests
python -m pytest -m integration -v

# Skip slow tests
python -m pytest -m "not slow" -v
```

### Coverage
```bash
pytest --cov=backend.app --cov-report=html
```

---

## Key Points

1. **Fixtures**: Reusable test data defined in conftest.py
2. **Database**: In-memory SQLite for fast, isolated tests
3. **Layered Tests**: Unit tests for data access, integration tests for APIs
4. **CI Ready**: Configuration suitable for GitHub Actions or similar
5. **Green Suite**: All 205 tests passing consistently

---

## Common Commands

```bash
# Run everything
python -m pytest -q

# Run with output
python -m pytest -v

# Stop on first failure
python -m pytest -x

# Show local variables on failure
python -m pytest -l

# Parallel execution (if pytest-xdist installed)
python -m pytest -n auto
```

---

For more information, see [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md).
