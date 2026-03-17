"""
Script para simplificar endpoints GET list a devolver solo listas
"""

import os
import re

files_to_update = [
    "backend/app/api/routers_budgets.py",
    "backend/app/api/routers_crud.py",
]

for filepath in files_to_update:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar response_model=dict por response_model=list en GET sin ID
        # Esto es simplista pero funciona para patrones específicos
        lines = content.split('\n')
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Si es un @router.get("/...", response_model=dict, sin {id}
            if '@router.get("/' in line and 'response_model=dict' in line and '{' not in line:
                # Cambiar a response_model=list
                line = line.replace('response_model=dict', 'response_model=list')
            
            result.append(line)
            i += 1
        
        new_content = '\n'.join(result)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Actualizado: {filepath}")
        else:
            print(f"ℹ️ Sin cambios: {filepath}")
    else:
        print(f"❌ No encontrado: {filepath}")

print("\n✅ Proceso completado")
