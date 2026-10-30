import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PNEUS_DASHBOARD_{agora}.zip")
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
    path = os.path.join(raiz, "app", "backend", "routers", "pneus.py")
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    if '/dashboard' not in c:
        rota_dash = '''
@router.get("/dashboard")
async def dashboard_pneus(_u: dict = Depends(require("read"))):
    pneus = await db.pneus.find({}, {"_id": 0}).to_list(2000)
    
    total = len(pneus)
    aplicados = sum(1 for p in pneus if p.get("status") == "Aplicado")
    sucateados = sum(1 for p in pneus if p.get("status") == "Sucateado")
    # Critério de sulco crítico: <= 3.0 mm
    sulco_critico = sum(1 for p in pneus if p.get("sulco_atual") is not None and p.get("sulco_atual") <= 3.0)
    
    # Agrupamento por marca
    marcas = {}
    for p in pneus:
        m = p.get("marca") or "Desconhecida"
        marcas[m] = marcas.get(m, 0) + 1
    
    top_marcas = [{"marca": k, "qtd": v} for k, v in sorted(marcas.items(), key=lambda item: item[1], reverse=True)[:5]]
    
    return {
        "total": total,
        "aplicados": aplicados,
        "sucateados": sucateados,
        "sulco_critico": sulco_critico,
        "top_marcas": top_marcas
    }

'''
        # Inserir antes das rotas com parâmetro (ex: /marcas, /medidas, /{id})
        pos = c.find('# --- ROTAS FIXAS PRIMEIRO ---')
        if pos == -1:
            pos = c.find('@router.get("/marcas")')
        if pos == -1:
            pos = c.find('@router.put("/{id}"')
            
        if pos != -1:
            c = c[:pos] + rota_dash + "\n" + c[pos:]
        else:
            c += rota_dash

        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota /dashboard criada.")

def fix_frontend(raiz):
    path = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar a aba "dashboard" no estado inicial se não existir
    if 'useState("cadastrados")' in c:
        c = c.replace('useState("cadastrados")', 'useState<"cadastrados" | "movimentacao" | "estoque" | "dashboard">("cadastrados")')

    # 2. Adicionar a Query do dashboard se não existir
    if 'queryKey: ["pneus-dashboard"]' not in c:
        c = c.replace(
            'const { data: pneus = [] } = useQuery({ queryKey: ["pneus"], queryFn: () => apiGet<any[]>("/pneus") });',
            'const { data: pneus = [] } = useQuery({ queryKey: ["pneus"], queryFn: () => apiGet<any[]>("/pneus") });\n  const { data: dash = { total: 0, aplicados: 0, sucateados: 0, sulco_critico: 0, top_marcas: [] } } = useQuery({ queryKey: ["pneus-dashboard"], queryFn: () => apiGet<any>("/pneus/dashboard") });'
        )

    # 3. Adicionar o Botão da Aba no Menu de Navegação
    if 'Indicadores' not in c:
        botao_dash = '''
        <button 
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${abaAtiva === 'dashboard' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`}
          onClick={() => setAbaAtiva('dashboard')}
        >
          <BarChart3 className="size-4 inline mr-2" /> Indicadores
        </button>
'''
        # Inserir antes do botão de Estoque/Sucata
        c = c.replace('<RefreshCw className="size-4 inline mr-2" /> Estoque / Sucata', botao_dash + '<RefreshCw className="size-4 inline mr-2" /> Estoque / Sucata')
        
        # Garantir import do BarChart3
        if 'BarChart3' not in c.split('lucide-react')[0]:
            c = c.replace('import { Plus,', 'import { BarChart3, Plus,')

    # 4. Criar a Renderização Condicional do Dashboard
    if '{abaAtiva === "dashboard" && (' not in c:
        render_dash = '''
      {/* Aba 4: Dashboard */}
      {abaAtiva === "dashboard" && (
        <div className="space-y-6">
          {/* Cards de KPI */}
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="glass p-4 rounded-xl flex justify-between items-center">
              <div><p className="text-xs uppercase text-slate-400">Total de Pneus</p><p className="text-2xl font-bold text-slate-100">{dash.total}</p></div>
              <div className="p-2 bg-sky-500/10 rounded-lg"><Disc className="size-5 text-sky-400" /></div>
            </div>
            <div className="glass p-4 rounded-xl flex justify-between items-center">
              <div><p className="text-xs uppercase text-slate-400">Pneus Aplicados</p><p className="text-2xl font-bold text-emerald-400">{dash.aplicados}</p></div>
              <div className="p-2 bg-emerald-500/10 rounded-lg"><CheckCircle2 className="size-5 text-emerald-400" /></div>
            </div>
            <div className="glass p-4 rounded-xl flex justify-between items-center border border-amber-500/30">
              <div><p className="text-xs uppercase text-amber-500 font-bold">Sulco Crítico (≤3mm)</p><p className="text-2xl font-bold text-amber-400">{dash.sulco_critico}</p></div>
              <div className="p-2 bg-amber-500/10 rounded-lg"><AlertTriangle className="size-5 text-amber-400" /></div>
            </div>
            <div className="glass p-4 rounded-xl flex justify-between items-center">
              <div><p className="text-xs uppercase text-slate-400">Sucateados</p><p className="text-2xl font-bold text-rose-400">{dash.sucateados}</p></div>
              <div className="p-2 bg-rose-500/10 rounded-lg"><Trash2 className="size-5 text-rose-400" /></div>
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            {/* Gráfico de Marcas */}
            <div className="glass p-6 rounded-2xl">
              <h3 className="text-sm font-bold text-slate-100 mb-6 flex items-center gap-2">
                <BarChart3 className="size-4 text-sky-400" /> Top 5 Marcas na Frota
              </h3>
              <div className="space-y-4">
                {dash.top_marcas.length === 0 ? (
                  <p className="text-sm text-slate-500">Sem dados suficientes.</p>
                ) : (
                  dash.top_marcas.map((m: any, i: number) => {
                    const maxQtd = dash.top_marcas[0].qtd;
                    const pct = (m.qtd / maxQtd) * 100;
                    return (
                      <div key={i}>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-slate-300 font-medium">{m.marca}</span>
                          <span className="text-sky-400 font-bold">{m.qtd} un</span>
                        </div>
                        <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-sky-500 rounded-full" style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {/* Saúde da Frota */}
            <div className="glass p-6 rounded-2xl flex flex-col justify-center">
              <h3 className="text-sm font-bold text-slate-100 mb-6 flex items-center gap-2">
                <Activity className="size-4 text-emerald-400" /> Saúde da Frota
              </h3>
              <div className="space-y-3">
                 <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">Aplicados (Rodando)</span>
                    <span className="font-bold text-emerald-400">{dash.aplicados}</span>
                 </div>
                 <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">Em Estoque / Manutenção</span>
                    <span className="font-bold text-sky-400">{dash.total - dash.aplicados - dash.sucateados}</span>
                 </div>
                 <div className="flex items-center justify-between text-sm border-t border-slate-800 pt-3 mt-3">
                    <span className="text-slate-400">Fora de Operação (Sucata)</span>
                    <span className="font-bold text-rose-400">{dash.sucateados}</span>
                 </div>
              </div>
            </div>
          </div>
        </div>
      )}
'''
        # Inserir antes do modal de cadastro
        c = c.replace('{/* Modal de Cadastro/Edição */}', render_dash + '\n      {/* Modal de Cadastro/Edição */}')
        
        # Adicionar import do CheckCircle2 e Activity
        if 'CheckCircle2' not in c.split('lucide-react')[0]:
            c = c.replace('import { Plus,', 'import { CheckCircle2, Activity, Plus,')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Aba de Dashboard e gráficos inseridos.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso! O Vite deve atualizar na hora.")