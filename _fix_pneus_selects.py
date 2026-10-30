import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PNEUS_SELECTS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/routers/pneus.py",
        "frontend/src/pages/Pneus.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "pneus.py")
    if not os.path.exists(caminho): return

    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Adiciona a rota de modelos se não existir (simula um cadastro usando distinct)
    if "def listar_modelos" not in c:
        rota_modelos = '''

@router.get("/modelos")
async def listar_modelos(_u: dict = Depends(require("read"))):
    # Busca todos os modelos distintos já cadastrados nos pneus para montar o dropdown
    modelos = await db.pneus.distinct("modelo")
    return [{"nome": m} for m in modelos if m]
'''
        c += rota_modelos
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota GET /pneus/modelos criada.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar as queries para buscar Marcas, Medidas e Modelos
    if 'const { data: marcasDb = [] }' not in c:
        c = c.replace(
            'const { data: veiculosApi = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });',
            '''const { data: veiculosApi = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: marcasDb = [] } = useQuery({ queryKey: ["marcas-pneus"], queryFn: () => apiGet<any[]>("/marcas-pneus") });
  const { data: medidasDb = [] } = useQuery({ queryKey: ["medidas-pneus"], queryFn: () => apiGet<any[]>("/medidas-pneus") });
  const { data: modelosDb = [] } = useQuery({ queryKey: ["modelos-pneus"], queryFn: () => apiGet<any[]>("/pneus/modelos") });'''
        )

    # 2. Substituir os Inputs de Marca, Modelo e Medida por FieldSelects
    c = c.replace(
        '<div className="grid gap-1.5"><Label className="text-xs text-slate-400">Marca *</Label><Input value={form.marca} onChange={(e) => setForm(s => ({ ...s, marca: e.target.value }))} placeholder="Ex: Michelin" /></div>',
        '''<div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Marca *</Label>
                <FieldSelect 
                  value={form.marca} 
                  onChange={(v) => setForm(s => ({ ...s, marca: v }))} 
                  options={marcasDb.map((m: any) => ({ value: m.nome, label: m.nome }))} 
                  placeholder="Selecione a Marca..." 
                />
              </div>'''
    )

    c = c.replace(
        '<div className="grid gap-1.5"><Label className="text-xs text-slate-400">Modelo</Label><Input value={form.modelo} onChange={(e) => setForm(s => ({ ...s, modelo: e.target.value }))} placeholder="Ex: X Multi Z" /></div>',
        '''<div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Modelo</Label>
                <FieldSelect 
                  value={form.modelo} 
                  onChange={(v) => setForm(s => ({ ...s, modelo: v }))} 
                  options={modelosDb.map((m: any) => ({ value: m.nome, label: m.nome }))} 
                  placeholder="Selecione o Modelo..." 
                />
              </div>'''
    )

    c = c.replace(
        '<div className="grid gap-1.5"><Label className="text-xs text-slate-400">Medida *</Label><Input value={form.medida} onChange={(e) => setForm(s => ({ ...s, medida: e.target.value }))} placeholder="Ex: 295/80 R22.5" /></div>',
        '''<div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Medida *</Label>
                <FieldSelect 
                  value={form.medida} 
                  onChange={(v) => setForm(s => ({ ...s, medida: v }))} 
                  options={medidasDb.map((m: any) => ({ value: m.medida, label: m.medida }))} 
                  placeholder="Selecione a Medida..." 
                />
              </div>'''
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Selects de Marca, Modelo e Medida integrados ao banco.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso!")