"""
Script para normalizar nombres de campos en tests a categoria_id
"""

import os
import re

test_files = [
    "tests/integration/conftest.py",
    "tests/integration/test_endpoints_accounts_transactions.py",
    "tests/integration/test_endpoints_analytics.py",
    "tests/integration/test_endpoints_crud.py",
    "tests/integration/test_user_flows.py"
]

# Patrones a reemplazar
replacements = [
    # En JSON/dicts
    ('"category_id"', '"categoria_id"'),
    ("'category_id'", "'categoria_id'"),
    # En diccionarios con espacios
    ('category_id"', 'categoria_id"'),
    ("category_id'", "categoria_id'"),
    # En argumentos de función
    ('category_id=', 'categoria_id='),
    # En aserciones
    ('["category_id"]', '["categoria_id"]'),
    ("['category_id']", "['categoria_id']"),
]

for filepath in test_files:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Actualizado: {filepath}")
        else:
            print(f"ℹ️ Sin cambios: {filepath}")
    else:
        print(f"❌ No encontrado: {filepath}")

print("\n✅ Normalización completada")
