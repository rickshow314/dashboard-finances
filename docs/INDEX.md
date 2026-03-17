# 📚 Project Documentation Index

Quick navigation to all project documentation.

## 🚀 Quick Start

**5 Minutes:** Run all tests
```bash
backend\venv\Scripts\activate
python -m pytest -q
```

**15 Minutes:** Read [TESTING.md](TESTING.md) and explore the test structure.

**1 Hour:** Review this index and explore the codebase.

---

## 📖 Documentation Files

| Document | Purpose | Time |
|----------|---------|------|
| [TESTING.md](TESTING.md) | Complete testing guide | 15 min |
| [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md) | Architecture & design patterns | 20 min |
| [BACKEND_STRUCTURE.md](BACKEND_STRUCTURE.md) | File structure and organization | 10 min |
| [BACKEND_GUIDE.md](BACKEND_GUIDE.md) | Integration & setup guide | 15 min |

---

## 🏗️ Project Structure

```
Dashboard/
├── backend/
│   ├── app/
│   │   ├── api/          # Endpoints (routers)
│   │   ├── core/         # Config & security
│   │   ├── database/     # Models & ORM
│   │   ├── repositories/ # Data access layer
│   │   ├── services/     # Business logic
│   │   └── schemas/      # Request/response schemas
│   ├── requirements.txt
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   └── services/     # API client
│   ├── package.json
│   └── vite.config.js
│
├── tests/
│   ├── unit/             # Unit tests (repositories, services)
│   └── integration/      # Integration tests (endpoints)
│
├── docs/                 # (This folder)
│   └── *.md files
│
└── pytest.ini            # Test configuration
```

---

## 🔧 Architecture Overview

```
HTTP Request
    ↓
[Router Endpoint]
    ↓
[Service Layer] ← Business logic
    ↓
[Repository Layer] ← Data access
    ↓
[Database]
```

---

## ✅ Test Coverage

- **Unit Tests:** 88 tests for repositories & services
- **Integration Tests:** Tests for all endpoints
- **Fixtures:** Database setup, test data
- **Configuration:** `pytest.ini` and `conftest.py`

Run tests with:
```bash
python -m pytest -q           # All tests
python -m pytest -v           # Verbose output
python -m pytest tests/unit/  # Unit tests only
```

---

## 📋 Key Technologies

- **Backend:** FastAPI, SQLAlchemy, Python
- **Frontend:** React, Vite, JavaScript
- **Testing:** pytest, TestClient
- **Database:** SQLite (dev), PostgreSQL (production)
- **Authentication:** JWT tokens

---

## 🔗 Related Files

- **Main README:** `../README.md`
- **Backend Requirements:** `../backend/requirements.txt`
- **Frontend Config:** `../frontend/package.json`
- **Test Config:** `../pytest.ini`

---

For questions or updates, refer to the specific documentation files listed above.
