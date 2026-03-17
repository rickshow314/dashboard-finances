"""
GUÍA RÁPIDA - Ejecutar Tests

Comienza en 5 minutos.
"""

# 🚀 INICIO RÁPIDO

## Paso 1: Instalar dependencias (si aún no lo hizo)

```bash
cd backend
pip install -r requirements.txt
```

**Nota**: pytest ya está incluido en requirements.txt

## Paso 2: Navegar a la raíz del proyecto

```bash
cd ..  # Volver a Dashboard/
```

## Paso 3: Ejecutar tests

### Opción A: Script automático (MÁS FÁCIL)

```bash
python run_tests.py
```

Se abrirá un menú interactivo:

```
============================================================
  EJECUTOR DE TESTS - Dashboard Financiero
============================================================

Opciones disponibles:

   1. todos
   2. repos
   3. servicios
   4. cobertura
   5. verbose
   6. rapidos
   7. accounts
   8. transactions
   9. budgets
  10. categories
  11. recurring
  12. goals

Selecciona una opción (nombre o número):
```

### Opción B: Comando directo (Pytest)

```bash
# Todos los tests
pytest -v

# Solo repositorios
pytest tests/unit/repositories/ -v

# Con cobertura
pytest --cov=app --cov-report=html
```

---

## 📊 RESULTADOS ESPERADOS

Cuando ejecutes los tests, deberías ver algo como:

```
============================== test session starts ==============================
platform win32 -- Python 3.11.x, pytest-7.4.3
cachedir: .pytest_cache
rootdir: C:\Users\ricar\Desktop\Propio\Proyectos\Dashboard
configfile: pytest.ini
collected 98 items

tests/unit/repositories/test_account_repository.py::TestAccountRepositoryCRUD::test_create_account PASSED [  1%]
tests/unit/repositories/test_account_repository.py::TestAccountRepositoryCRUD::test_get_account_by_id PASSED [  2%]
...
tests/unit/services/test_services.py::TestServiceIntegration::test_multiple_transactions_summary PASSED [99%]

============================== 98 passed in 2.34s ==============================
✅ Tests completados exitosamente
```

---

## 🎯 COMANDOS COMUNES

```bash
# Ver todos los tests y qué hacen
pytest --collect-only

# Ejecutar con más detalles
pytest -vv

# Ejecutar un test específico
pytest tests/unit/repositories/test_account_repository.py::TestAccountRepositoryCRUD::test_create_account

# Ejecutar una clase de tests
pytest tests/unit/repositories/test_account_repository.py::TestAccountRepositoryCRUD

# Ver cobertura
pytest --cov=app --cov-report=html

# Abrir reporte de cobertura
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
```

---

## 📁 ESTRUCTURA

```
Dashboard/
├── tests/
│   ├── conftest.py                    ← Fixtures
│   └── unit/
│       ├── repositories/              ← 88 tests
│       └── services/                  ← 10 tests
├── pytest.ini                          ← Config
├── run_tests.py                        ← Script ejecutor
├── TESTING_GUIDE.md                    ← Documentación
└── TEST_COVERAGE.md                    ← Cobertura
```

---

## ✅ CHECKLIST

Antes de correr tests:

- [ ] Instalaste las dependencias con `pip install -r backend/requirements.txt`
- [ ] Estás en la carpeta raíz del proyecto (`Dashboard/`)
- [ ] Tienes Python 3.9+
- [ ] La carpeta `tests/` existe con todos los archivos

---

## 🐛 TROUBLESHOOTING

### Error: "No module named 'pytest'"
```bash
pip install pytest pytest-cov
```

### Error: "No module named 'app'"
- Asegúrate de estar en la raíz del proyecto
- Ejecuta: `python run_tests.py`

### Error: "No such file or directory: 'tests'"
- Verifica que la carpeta `tests/` existe
- Ejecuta desde la raíz: `ls tests/` (o `dir tests` en Windows)

### Tests lentos
- Usa: `pytest tests/unit/repositories/test_account_repository.py` (más rápido)
- Los 98 tests deberían tomar <5 segundos

---

## 📈 PROGRESIÓN

1️⃣ **Instalar** - pip install
2️⃣ **Ejecutar** - python run_tests.py
3️⃣ **Ver resultados** - 98 tests ✅
4️⃣ **Explorar cobertura** - pytest --cov
5️⃣ **Leer documentación** - TESTING_GUIDE.md

---

## 🎓 EJEMPLOS DE USO

### Ejecutar y generar reporte HTML de cobertura

```bash
pytest --cov=app --cov-report=html
start htmlcov/index.html
```

### Ejecutar solo tests rápidos (excluyendo lentos)

```bash
pytest -m "not slow"
```

### Ejecutar con salida detallada

```bash
pytest -vv --tb=long
```

### Ejecutar un archivo de tests específico

```bash
pytest tests/unit/repositories/test_account_repository.py -v
```

---

## 💡 TIPS

- **Usa el script**: `python run_tests.py` es lo más fácil
- **Lee la output**: Te dice exactamente qué pasó
- **Revisa pytest.ini**: Configuración de los tests
- **Fixtures reutilizables**: No necesitas crear datos cada test
- **Edge cases incluidos**: Ya probamos límites y errores

---

## 📚 DOCUMENTACIÓN DISPONIBLE

1. **TESTS_SUMMARY.md** - Resumen ejecutivo (este archivo ampliado)
2. **TESTING_GUIDE.md** - Guía completa y detallada
3. **TEST_COVERAGE.md** - Matriz de cobertura por entidad
4. **run_tests.py** - Script interactivo para ejecutar tests
5. **pytest.ini** - Configuración de pytest

---

## 🎉 ¡LISTO!

Ya tienes todo configurado. Ahora simplemente:

```bash
python run_tests.py
```

Y selecciona la opción que quieras. ¡A testear! 🚀

---

**Generado**: 18 de noviembre de 2025
**Versión**: 1.0
