"""
Script para normalizar categoria_id en el backend
"""

import os
import re

# Archivos a actualizar
files_to_update = [
    "backend/app/repositories/transaction_repository.py",
    "backend/app/services/transaction_service.py",
    "backend/app/api/routers_accounts_transactions.py",
    "tests/conftest.py",
    "tests/unit/repositories/test_transaction_repository.py",
    "tests/unit/services/test_services.py",
]

# Patrones a reemplazar
replacements = [
    ('category_id', 'categoria_id'),
]

for filepath in files_to_update:
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            
            for old, new in replacements:
                # Reemplazar pero no en comentarios que digan "category"
                # Reemplazar solamente cuando sea category_id (con underscore)
                content = re.sub(r'\b' + re.escape(old) + r'\b', new, content)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Actualizado: {filepath}")
            else:
                print(f"ℹ️ Sin cambios: {filepath}")
        except Exception as e:
            print(f"⚠️ Error en {filepath}: {e}")
    else:
        print(f"❌ No encontrado: {filepath}")

print("\n✅ Normalización completada")
