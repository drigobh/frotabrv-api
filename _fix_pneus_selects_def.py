import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PNEUS_SELECTS_DEF_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Pneus.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar as queries para buscar do banco (se não existirem)
    if 'const { data: marcasDb = [] }' not in c:
        c = c.replace(
            'const { data: veiculosApi = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });',
            '''const { data: veiculosApi = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: marcasDb = [] } = useQuery({ queryKey: ["marcas-pneus"], queryFn: () => apiGet<any[]>("/marcas-pneus") });
  const { data: medidasDb = [] } = useQuery({ queryKey: ["medidas-pneus"], queryFn: () => apiGet<any[]>("/medidas-pneus") });
  const { data: modelosDb = [] } = useQuery({ queryKey: ["modelos-pneus"], queryFn: () => apiGet<any[]>("/pneus/modelos") });'''
        )

    # 2. Substituir o Input de MARCA pelo FieldSelect
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

    # 3. Substituir o Input de MODELO pelo FieldSelect
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

    # 4. Substituir o Input de MEDIDA pelo FieldSelect
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
    print("✅ Pneus.tsx atualizado com FieldSelects.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")