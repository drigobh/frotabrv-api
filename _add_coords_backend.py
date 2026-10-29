import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_COORDS_BACKEND_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/models/empresa.py",
        "app/backend/models/fornecedores.py",
        "app/backend/routers/fornecedores.py",
        "app/backend/routers/empresa.py"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    # 1. Adicionar campos de latitude e longitude no Model de Empresa
    caminho_emp = os.path.join(raiz, "app", "backend", "models", "empresa.py")
    with open(caminho_emp, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'latitude:' not in c:
        c = c.replace(
            'tipo_unidade: str = "Matriz"',
            'tipo_unidade: str = "Matriz"\n    latitude: float | None = None\n    longitude: float | None = None'
        )
        with open(caminho_emp, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Model Empresa: latitude e longitude adicionadas.")

    # 2. Adicionar campos de latitude e longitude no Model de Fornecedor
    caminho_forn = os.path.join(raiz, "app", "backend", "models", "fornecedores.py")
    with open(caminho_forn, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'latitude:' not in c:
        c = c.replace(
            'whatsapp: str | None = None',
            'whatsapp: str | None = None\n    latitude: float | None = None\n    longitude: float | None = None'
        )
        with open(caminho_forn, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Model Fornecedor: latitude e longitude adicionadas.")

    # 3. Forçar gravação no Router de Fornecedores (POST/PUT)
    router_forn = os.path.join(raiz, "app", "backend", "routers", "fornecedores.py")
    with open(router_forn, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if 'doc["latitude"] = getattr(body, "latitude", None)' not in c:
        c = c.replace(
            'doc["whatsapp"] = getattr(body, "whatsapp", None)',
            'doc["whatsapp"] = getattr(body, "whatsapp", None)\n    doc["latitude"] = getattr(body, "latitude", None)\n    doc["longitude"] = getattr(body, "longitude", None)'
        )
        with open(router_forn, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Router Fornecedor: gravação de latitude e longitude forçada.")

    # 4. Forçar gravação no Router de Empresa
    router_emp = os.path.join(raiz, "app", "backend", "routers", "empresa.py")
    with open(router_emp, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if 'doc["latitude"] = getattr(body, "latitude", None)' not in c:
        # No PUT
        c = c.replace(
            'doc["updated_at"] = now_iso()',
            'doc["updated_at"] = now_iso()\n    doc["latitude"] = getattr(body, "latitude", None)\n    doc["longitude"] = getattr(body, "longitude", None)'
        )
        # No POST
        c = c.replace(
            'doc["created_at"] = now_iso()',
            'doc["created_at"] = now_iso()\n    doc["latitude"] = getattr(body, "latitude", None)\n    doc["longitude"] = getattr(body, "longitude", None)'
        )
        with open(router_emp, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Router Empresa: gravação de latitude e longitude forçada.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Backend atualizado com coordenadas.")