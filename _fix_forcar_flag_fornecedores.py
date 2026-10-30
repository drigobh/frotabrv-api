import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_FORCAR_FLAG_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/routers/parametrizacao.py",
        "frontend/src/pages/Parametrizacao.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    # Adicionar um endpoint para forçar a flag = true
    router_path = os.path.join(raiz, "app", "backend", "routers", "parametrizacao.py")
    with open(router_path, 'r', encoding='utf-8') as f:
        c = f.read()

    if '/forcar-seed' not in c:
        rota = '''
@router.post("/forcar-seed")
async def forcar_seed(_u: dict = Depends(require("write"))):
    await db.parametrizacoes.update_one(
        {"id": "meta_abastecimento"},
        {"$set": {
            "mostrar_seed_fornecedores": True,
            "mostrar_seed_medidas": True,
            "mostrar_seed_marcas": True,
            "updated_at": now_iso()
        }},
        upsert=True
    )
    return {"ok": True, "mensagem": "Flags de seed ativadas com sucesso."}
'''
        c += rota
        with open(router_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota /forcar-seed criada.")

def fix_frontend(raiz):
    # Adicionar um botão na Parametrização para forçar a flag
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Parametrizacao.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    if 'Forçar Flags' not in c:
        # Adicionar o botão de forçar ao lado do "Salvar Parametrizações"
        alvo = '<Button onClick={() => salvar.mutate()} disabled={salvar.isPending} className="bg-sky-600 hover:bg-sky-500">'
        novo = '''<div className="flex gap-2">
          <Button 
            variant="outline" 
            onClick={async () => {
              await apiPost("/parametrizacao/forcar-seed", {});
              toast.success("Flags ativadas! Recarregue a página.");
              qc.invalidateQueries({ queryKey: ["parametrizacao-meta"] });
            }}
            className="border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10"
          >
            Forçar Flags de Seed
          </Button>
          ''' + alvo
        c = c.replace(alvo, novo)
        # Fechar a div extra após o botão de salvar
        c = c.replace('</Button>', '</Button>\n          </div>', 1)
        print("✅ Botão 'Forçar Flags de Seed' adicionado à Parametrização.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso!")