"""
Script para actualizar las rutas de los tests de /api/ a /api/v1/
"""

import os
import re

test_dir = "tests/integration"

# Patrones a reemplazar
replacements = [
    ('"/api/accounts', '"/api/v1/accounts'),
    ('"/api/transactions', '"/api/v1/transactions'),
    ('"/api/budgets', '"/api/v1/budgets'),
    ('"/api/categories', '"/api/v1/categories'),
    ('"/api/recurring', '"/api/v1/recurring'),
    ('"/api/goals', '"/api/v1/goals'),
    ('"/api/analytics', '"/api/v1/analytics'),
]

def fix_file(filepath):
    """Reemplaza todas las rutas en un archivo."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Actualizado: {filepath}")
        return True
    return False

# Procesar todos los archivos de test
updated = 0
for filename in os.listdir(test_dir):
    if filename.startswith('test_') and filename.endswith('.py'):
        filepath = os.path.join(test_dir, filename)
        if fix_file(filepath):
            updated += 1

print(f"\n📊 {updated} archivos actualizados")
