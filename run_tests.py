"""
Script de ayuda para ejecutar tests.
Uso: python run_tests.py [opción]
"""

import subprocess
import sys


OPCIONES = {
    "todos": "pytest",
    "repos": "pytest tests/unit/repositories/ -v",
    "servicios": "pytest tests/unit/services/ -v",
    "cobertura": "pytest --cov=app --cov-report=html --cov-report=term",
    "verbose": "pytest -vv --tb=long",
    "rapidos": "pytest -m 'not slow'",
    "accounts": "pytest tests/unit/repositories/test_account_repository.py -v",
    "transactions": "pytest tests/unit/repositories/test_transaction_repository.py -v",
    "budgets": "pytest tests/unit/repositories/test_budget_repository.py -v",
    "categories": "pytest tests/unit/repositories/test_category_repository.py -v",
    "recurring": "pytest tests/unit/repositories/test_recurring_repository.py -v",
    "goals": "pytest tests/unit/repositories/test_goal_repository.py -v",
}


def mostrar_menu():
    print("\n" + "="*60)
    print("  EJECUTOR DE TESTS - Dashboard Financiero")
    print("="*60)
    print("\nOpciones disponibles:")
    print()
    for i, (opcion, _) in enumerate(OPCIONES.items(), 1):
        print(f"  {i:2d}. {opcion}")
    print()


def ejecutar_tests(opcion):
    if opcion.lower() not in OPCIONES:
        print(f"❌ Opción '{opcion}' no válida")
        return False
    
    comando = OPCIONES[opcion.lower()]
    print(f"\n▶️  Ejecutando: {comando}\n")
    
    try:
        resultado = subprocess.run(comando, shell=True, cwd=".")
        return resultado.returncode == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    if len(sys.argv) > 1:
        opcion = sys.argv[1]
    else:
        mostrar_menu()
        opcion = input("Selecciona una opción (nombre o número): ").strip()
        
        # Si es número, convertir a nombre
        if opcion.isdigit():
            opciones_list = list(OPCIONES.keys())
            try:
                opcion = opciones_list[int(opcion) - 1]
            except IndexError:
                print(f"❌ Opción {opcion} no válida")
                return
    
    exito = ejecutar_tests(opcion)
    
    if exito:
        print("\n✅ Tests completados exitosamente")
    else:
        print("\n❌ Algunos tests fallaron")
        sys.exit(1)


if __name__ == "__main__":
    main()
