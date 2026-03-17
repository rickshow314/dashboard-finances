Refactor: normalize fields and fix repositories/services (tests green)

Summary
- Normalize field names (`categoria_id`) and fix inconsistencies across repositories, services and tests.
- Replace incorrect SQLAlchemy usage (`func.case` → `case`) and fix joins to use `categoria_id`.
- Refactor to enforce layered design: routers → services → repositories.
- Add backward-compatible wrappers in services to preserve compatibility with current tests.
- Update fixtures and unit/integration tests accordingly. Add helper scripts for normalization and running tests.

Test Results
- Local test run: 205 passed.

Key files changed
- backend/app/repositories/* (account, transaction, budget, category, recurring, goal)
- backend/app/services/* (account, transaction, budget)
- backend/app/api/routers_budgets.py
- tests/ (integration and unit fixtures and tests)
- pytest.ini, run_tests.py and normalization scripts

Notes
- Critical fix: replaced `func.case(...)` with SQLAlchemy `case(...)` to avoid TypeError in aggregated queries.
- I prioritized keeping backward compatibility with the existing test suite via service wrappers; recommend a follow-up task to remove temporary wrappers and unify naming (Spanish vs English fields).

How to reproduce locally
```bash
# from repo root
backend\venv\Scripts\activate
python -m pytest -q
```

If you want me to squash or split commits, or change the PR base/branch name, tell me and I will update the PR.
