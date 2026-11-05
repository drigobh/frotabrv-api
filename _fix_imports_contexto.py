import os
import re

# 1. Pega o conteúdo de um arquivo que JÁ FUNCIONA (ex: abastecimentos.py)
arquivo_referencia = os.path.join(os.getcwd(), "app", "backend", "routers", "abastecimentos.py")

imports_referencia = {
    "db": None,
    "require": None,
    "HTTPException": None
}

if os.path.exists(arquivo_referencia):
    with open(arquivo_referencia, "r", encoding="utf-8") as f:
        ref_c = f.read()
    
    # Procura como o 'db' é importado no arquivo de referência
    match_db = re.search(r'from\s+[\w\.]+\s+import\s+.*?db', ref_c)
    if match_db:
        imports_referencia["db"] = match_db.group(0).strip()
    
    # Procura como o 'require' é importado
    match_req = re.search(r'from\s+[\w\.]+\s+import\s+.*?require', ref_c)
    if match_req:
        imports_referencia["require"] = match_req.group(0).strip()
    
    # Verifica se HTTPException está importado
    if "HTTPException" in ref_c:
        imports_referencia["HTTPException"] = "from fastapi import HTTPException"

# 2. Aplica no arquivo veiculos.py
path = os.path.join(os.getcwd(), "app", "backend", "routers", "veiculos.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Remove imports antigos de db e require (se houver)
c = re.sub(r'from\s+[\w\.]+\s+import\s+.*?db\n', '', c)
c = re.sub(r'from\s+[\w\.]+\s+import\s+.*?require\n', '', c)

# Constrói o bloco de imports que falta
novos_imports = []
if imports_referencia["require"]:
    novos_imports.append(imports_referencia["require"])
if imports_referencia["db"]:
    novos_imports.append(imports_referencia["db"])
if "HTTPException" not in c:
    novos_imports.append("from fastapi import HTTPException")

if novos_imports:
    # Coloca os imports após a linha do APIRouter
    match_apirouter = re.search(r'(from fastapi import .*?\n)', c)
    if match_apirouter:
        bloco = "\n".join(novos_imports) + "\n"
        c = c.replace(match_apirouter.group(1), match_apirouter.group(1) + bloco)
    else:
        c = "\n".join(novos_imports) + "\n" + c
    
    print("✅ Imports injetados com base na referência:")
    for imp in novos_imports:
        print(f"   {imp}")
else:
    print("⚠️ Não foi possível encontrar referências.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("\n✅ veiculos.py atualizado!")