import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ACOPL_MANUT_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    for arquivo in ["models/acoplamentos.py", "routers/acoplamentos.py"]:
        caminho_abs = os.path.join(raiz, "app", "backend", arquivo.replace("/", os.sep))
        if os.path.exists(caminho_abs):
            with zipfile.ZipFile(caminho_zip, 'a', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(caminho_abs, f"app/backend/{arquivo}")

    caminho_front = os.path.join(raiz, "frontend", "src", "pages", "Acoplamentos.tsx")
    if os.path.exists(caminho_front):
        with zipfile.ZipFile(caminho_zip, 'a', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_front, "frontend/src/pages/Acoplamentos.tsx")
            
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    # 1. Atualizar Model para aceitar o campo de manutenção
    path_model = os.path.join(raiz, "app", "backend", "models", "acoplamentos.py")
    if os.path.exists(path_model):
        with open(path_model, 'r', encoding='utf-8') as f:
            c = f.read()
        
        if 'manutencao:' not in c:
            # Adiciona o campo opcional na classe Acoplamento
            c = re.sub(r'(class Acoplamento\(.*?\):\n)', r'\1    manutencao: dict | None = None\n', c)
            with open(path_model, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Model atualizado com campo 'manutencao'.")

    # 2. Atualizar Router para buscar manutenções ativas e cruzar com os acoplamentos
    path_router = os.path.join(raiz, "app", "backend", "routers", "acoplamentos.py")
    with open(path_router, 'r', encoding='utf-8') as f:
        c = f.read()

    if 'db.manutencoes.find' not in c:
        novo_get = '''@router.get("", response_model=list[Acoplamento])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.acoplamentos.find({"status": "ativo"}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    # Busca manutenções ativas (qualquer status que não seja finalizado/fechado/cancelado)
    manutencoes = await db.manutencoes.find({"status": {"$nin": ["concluida", "fechada", "cancelada", "finalizada"]}}, {"_id": 0}).to_list(1000)
    manut_map = {m["veiculo_id"]: m for m in manutencoes if "veiculo_id" in m}

    for d in docs:
        if not d.get("data_inicio"):
            d["data_inicio"] = d.get("created_at", "").split("T")[0]
            
        if d["veiculo_id"] in manut_map:
            m = manut_map[d["veiculo_id"]]
            d["manutencao"] = {
                "id": m.get("id"),
                "usuario": m.get("created_by") or m.get("usuario") or "Sistema",
                "data": m.get("data_abertura") or m.get("created_at") or ""
            }
            
    return [Acoplamento(**d) for d in docs]'''
        
        # Substitui a função listar antiga pela nova
        c = re.sub(r'@router\.get\("", response_model=list\[Acoplamento\]\)\nasync def listar[\s\S]*?return \[Acoplamento\(\*\*d\) for d in docs\]', novo_get, c)
        
        with open(path_router, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Router atualizado para cruzar dados de manutenção.")

def fix_frontend(raiz):
    path_front = os.path.join(raiz, "frontend", "src", "pages", "Acoplamentos.tsx")
    with open(path_front, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Importar o ícone Truck
    if 'Truck' not in c.split('lucide-react')[0]:
        c = c.replace(
            'import { Link2, Plus, Pencil, Trash2, History, Clock, User }',
            'import { Link2, Plus, Pencil, Trash2, History, Clock, User, Truck }'
        )

    # 2. Adicionar o caminhãozinho piscando antes do nome do veículo
    if 'r.manutencao &&' not in c:
        c = c.replace(
            '<TableCell>{r.veiculo_label}</TableCell>',
            '''<TableCell>
                  <div className="flex items-center gap-2">
                    {r.manutencao && (
                      <div title={`Em manutenção desde ${new Date(r.manutencao.data).toLocaleDateString("pt-BR")} por ${r.manutencao.usuario}`}>
                        <Truck className="size-4 text-red-500 animate-pulse drop-shadow-[0_0_5px_rgba(239,68,68,0.8)]" />
                      </div>
                    )}
                    <span>{r.veiculo_label}</span>
                  </div>
                </TableCell>'''
        )
        print("✅ Caminhão de manutenção adicionado ao Frontend.")

    with open(path_front, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso!")