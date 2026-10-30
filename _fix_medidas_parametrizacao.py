import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MEDIDAS_PARAM_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/models/parametrizacao.py",
        "app/backend/routers/parametrizacao.py",
        "frontend/src/pages/Parametrizacao.tsx",
        "frontend/src/pages/PneuMedidas.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    # 1. Adicionar flag no Model de Parametrização
    model_path = os.path.join(raiz, "app", "backend", "models", "parametrizacao.py")
    with open(model_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'mostrar_seed_medidas' not in c:
        c = c.replace(
            'meta_abastecimento_valor: float = 2.5',
            'meta_abastecimento_valor: float = 2.5\n    mostrar_seed_medidas: bool = False'
        )
        with open(model_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Model Parametrização: flag mostrar_seed_medidas adicionada.")

    # 2. Atualizar Router da Parametrização
    router_path = os.path.join(raiz, "app", "backend", "routers", "parametrizacao.py")
    with open(router_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'mostrar_seed_medidas' not in c:
        c = c.replace(
            'meta_abastecimento_valor=config.get("meta_abastecimento_valor", 2.5)',
            'meta_abastecimento_valor=config.get("meta_abastecimento_valor", 2.5),\n        mostrar_seed_medidas=config.get("mostrar_seed_medidas", False)'
        )
        c = c.replace(
            '"meta_abastecimento_valor": body.meta_abastecimento_valor,',
            '"meta_abastecimento_valor": body.meta_abastecimento_valor,\n            "mostrar_seed_medidas": body.mostrar_seed_medidas,'
        )
        with open(router_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Router Parametrização atualizado.")

def fix_parametrizacao_front(raiz):
    # Adicionar o toggle na tela de Parametrização
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Parametrizacao.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    if 'mostrarSeedMedidas' not in c:
        # Adicionar estado
        c = c.replace(
            'const [mostrarSeed, setMostrarSeed] = useState(false);',
            'const [mostrarSeed, setMostrarSeed] = useState(false);\n  const [mostrarSeedMedidas, setMostrarSeedMedidas] = useState(false);'
        )
        # Adicionar no useEffect
        c = c.replace(
            'setMostrarSeed(config.mostrar_seed_fornecedores || false);',
            'setMostrarSeed(config.mostrar_seed_fornecedores || false);\n      setMostrarSeedMedidas(config.mostrar_seed_medidas || false);'
        )
        # Adicionar no payload de salvamento
        c = c.replace(
            'mostrar_seed_fornecedores: mostrarSeed,',
            'mostrar_seed_fornecedores: mostrarSeed,\n      mostrar_seed_medidas: mostrarSeedMedidas,'
        )
        # Adicionar a linha na tabela (após a linha de "Popular Lista Base")
        alvo = '''<TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">
                Exibir botão "Popular Lista Base" na tela de Tipos de Fornecedores
              </TableCell>
              <TableCell>
                <button
                  type="button"
                  onClick={() => setMostrarSeed(!mostrarSeed)}
                  className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                    mostrarSeed
                      ? "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"
                      : "bg-red-500/20 text-red-400 hover:bg-red-500/30"
                  }`}
                >
                  {mostrarSeed ? <CheckCircle2 className="size-3" /> : <XCircle className="size-3" />}
                  {mostrarSeed ? "Visível" : "Oculto"}
                </button>
              </TableCell>
              <TableCell colSpan={2} className="text-xs text-slate-500 italic">Útil apenas para setup inicial do sistema.</TableCell>
            </TableRow>'''
        
        novo = alvo + '''
            <TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">
                Exibir botão "Popular Medidas" na tela de Medidas de Pneus
              </TableCell>
              <TableCell>
                <button
                  type="button"
                  onClick={() => setMostrarSeedMedidas(!mostrarSeedMedidas)}
                  className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                    mostrarSeedMedidas
                      ? "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"
                      : "bg-red-500/20 text-red-400 hover:bg-red-500/30"
                  }`}
                >
                  {mostrarSeedMedidas ? <CheckCircle2 className="size-3" /> : <XCircle className="size-3" />}
                  {mostrarSeedMedidas ? "Visível" : "Oculto"}
                </button>
              </TableCell>
              <TableCell colSpan={2} className="text-xs text-slate-500 italic">Útil apenas para setup inicial do sistema.</TableCell>
            </TableRow>'''
        
        if alvo in c:
            c = c.replace(alvo, novo)
            print("✅ Toggle 'Popular Medidas' adicionado à Parametrização.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

def fix_medidas_front(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "PneuMedidas.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Corrigir o modal: adicionar campo "Requer Câmara"
    if 'requer_camara' not in c or 'Requer Câmara' not in c:
        alvo = '''<div className="grid gap-1.5"><Label className="text-xs text-slate-400">Construção</Label><Input value={form.tipo_construcao} onChange={(e) => setForm(s => ({ ...s, tipo_construcao: e.target.value }))} placeholder="RADIAL" /></div>'''
        
        novo = alvo + '''
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Requer Câmara?</Label>
                <FieldSelect 
                  value={form.requer_camara ? "sim" : "nao"} 
                  onChange={(v) => setForm(s => ({ ...s, requer_camara: v === "sim" }))} 
                  options={[{ value: "nao", label: "Não" }, { value: "sim", label: "Sim" }]} 
                />
              </div>'''
        
        if alvo in c:
            c = c.replace(alvo, novo)
            print("✅ Campo 'Requer Câmara' adicionado ao modal.")

    # 2. Controlar visibilidade do botão "Popular Medidas" via parametrização
    if 'queryKey: ["parametrizacao-meta"]' not in c:
        # Adicionar a query da parametrização
        c = c.replace(
            'const { data: medidas = [] } = useQuery({ queryKey: ["pneu-medidas"], queryFn: () => apiGet<any[]>("/pneu-medidas") });',
            '''const { data: medidas = [] } = useQuery({ queryKey: ["pneu-medidas"], queryFn: () => apiGet<any[]>("/pneu-medidas") });
  const { data: config } = useQuery({ queryKey: ["parametrizacao-meta"], queryFn: () => apiGet<any>("/parametrizacao/meta") });'''
        )
        
        # Esconder o botão se a flag não estiver habilitada
        c = c.replace(
            'actions={\n          <div className="flex gap-2">\n            <Button variant="outline" onClick={popularMedidas} disabled={seed.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10 h-9">\n              {seed.isPending ? "Populando..." : "Popular Medidas"}\n            </Button>\n            <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Nova Medida</Button>\n          </div>\n        }',
            '''actions={
          <div className="flex gap-2">
            {config?.mostrar_seed_medidas && (
              <Button variant="outline" onClick={popularMedidas} disabled={seed.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10 h-9">
                {seed.isPending ? "Populando..." : "Popular Medidas"}
              </Button>
            )}
            <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Nova Medida</Button>
          </div>
        }'''
        )
        print("✅ Botão 'Popular Medidas' agora respeita a parametrização.")

    # 3. Garantir import do FieldSelect (se não existir)
    if 'FieldSelect' not in c.split('lucide-react')[0]:
        c = c.replace(
            'import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";',
            'import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";\nimport { FieldSelect } from "@/components/common/FieldSelect";'
        )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_parametrizacao_front(raiz)
    fix_medidas_front(raiz)
    print("\n✅ Script aplicado com sucesso!")