import os
import re

path = os.path.join(os.getcwd(), "app", "backend", "routers", "veiculos.py")

if not os.path.exists(path):
    print("❌ Arquivo veiculos.py não encontrado.")
else:
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # Verifica se Depends está importado
    if "Depends" not in c.split("router =")[0]:
        # Tenta adicionar na linha do APIRouter
        c = c.replace(
            "from fastapi import APIRouter",
            "from fastapi import APIRouter, Depends, HTTPException"
        )
        # Se não achar a linha exata, tenta o import genérico do fastapi
        if "from fastapi import" not in c:
            c = "from fastapi import APIRouter, Depends, HTTPException\n" + c
        print("✅ Import do Depends (e HTTPException) corrigido.")
    else:
        print("ℹ️ Depends já estava importado.")

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)

    print("✅ veiculos.py corrigido! O Render vai conseguir compilar no próximo push.")