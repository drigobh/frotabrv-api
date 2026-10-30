import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MENU_COMPLETO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "RelatorioManutencao.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/RelatorioManutencao.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "RelatorioManutencao.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. SUBSTITUIR O ARRAY menuCategorias INTEIRO (via regex não-guloso)
    padrao_menu = re.compile(r'const menuCategorias = \[[\s\S]*?\];', re.DOTALL)
    
    novo_menu = '''const menuCategorias = [
    {
      titulo: "Indicadores de Custo",
      itens: [
        { id: "cpk", label: "CPK (Custo/KM)", icon: DollarSign },
        { id: "custoVeiculoTipo", label: "Custo por Tipo de Veículo", icon: Truck },
        { id: "centroCusto", label: "Custo por Filial/Base", icon: MapPin },
      ]
    },
    {
      titulo: "Eficiência Operacional",
      itens: [
        { id: "relatorio-ratio", label: "Ratio Preve. x Corret.", icon: TrendingUp },
        { id: "relatorio-faixa-km", label: "Faixa de Hodômetro", icon: Activity },
        { id: "relatorio-desvio-consumo", label: "Desvio de Consumo", icon: GitCompare },
        { id: "relatorio-previsao", label: "Previsão Orçamentária", icon: DollarSign },
        { id: "relatorio-oficina-tempo", label: "Tempo vs. Custo", icon: Clock },
        { id: "relatorio-oleo-atraso", label: "Óleo em Atraso", icon: RotateCcw },
        { id: "mtbf", label: "MTBF (Entre Falhas)", icon: ShieldAlert },
        { id: "mttr", label: "MTTR (Tempo Reparo)", icon: Clock },
        { id: "ociosidade", label: "Ociosidade (Downtime)", icon: AlertTriangle },
        { id: "corretivas", label: "Corretivas Emergenciais", icon: Activity },
        { id: "reincidencia", label: "Reincidência de Falhas", icon: RotateCcw },
      ]
    },
    {
      titulo: "Preventiva e Planejamento",
      itens: [
        { id: "aderencia", label: "Aderência Preventiva", icon: CheckCircle2 },
        { id: "vidaUtil", label: "Vida Útil de Componentes", icon: Layers },
      ]
    },
    {
      titulo: "Consumo e Fornecedores",
      itens: [
        { id: "pecas", label: "Curva ABC de Peças", icon: Boxes },
        { id: "combustivelManut", label: "Consumo vs. Manutenção", icon: TrendingUp },
        { id: "fornecedor", label: "Ranking Fornecedores", icon: Target },
        { id: "benchmarking", label: "Comparativo de Preços", icon: GitCompare },
        { id: "motorista", label: "Custo por Motorista", icon: Users },
      ]
    },
  ];'''

    if padrao_menu.search(c):
        c = padrao_menu.sub(novo_menu, c, count=1)
        print("✅ Array menuCategorias substituído com sucesso.")
    else:
        print("⚠️ Não foi possível encontrar o menuCategorias. Verifique manualmente.")

    # 2. ADICIONAR OS CASES (se ainda não existirem)
    if 'case "relatorio-ratio"' not in c:
        # Procura a linha do case "cpk"
        alvo = 'case "cpk": return'
        novos_cases = '''case "relatorio-ratio": return <RelatorioRatio />;
      case "relatorio-faixa-km": return <RelatorioFaixaKm />;
      case "relatorio-desvio-consumo": return <RelatorioDesvioConsumo />;
      case "relatorio-previsao": return <RelatorioPrevisao />;
      case "relatorio-oficina-tempo": return <RelatorioOficinaTempo />;
      case "relatorio-oleo-atraso": return <RelatorioOleoAtraso />;
      ''' + alvo

        if alvo in c:
            c = c.replace(alvo, novos_cases, 1)
            print("✅ Cases adicionados ao renderAba.")
        else:
            print("⚠️ Case 'cpk' não encontrado.")

    # 3. ADICIONAR OS COMPONENTES (se ainda não existirem)
    if 'function RelatorioRatio' not in c:
        componentes = '''

// --- COMPONENTES DE RELATÓRIOS AVANÇADOS ---

function RelatorioRatio() {
  const { data } = useQuery({ queryKey: ["relatorios-manutencao"], queryFn: () => apiGet<any>("/dashboard/relatorios-manutencao") });
  if (!data) return <div className="glass p-6 text-center text-slate-400">Carregando...</div>;
  return (
    <div className="glass p-6 rounded-2xl text-center space-y-4">
      <h3 className="text-lg font-bold text-slate-100 mb-2">Ratio Preventiva x Corretiva</h3>
      <div className="flex justify-center gap-12">
        <div><p className="text-5xl font-bold text-emerald-400">{data.ratio.percentual_preventiva.toFixed(1)}%</p><p className="text-sm text-slate-400">Preventivas ({data.ratio.preventivas})</p></div>
        <div><p className="text-5xl font-bold text-rose-400">{data.ratio.percentual_corretiva.toFixed(1)}%</p><p className="text-sm text-slate-400">Corretivas ({data.ratio.corretivas})</p></div>
      </div>
    </div>
  );
}

function RelatorioFaixaKm() {
  const { data } = useQuery({ queryKey: ["relatorios-manutencao"], queryFn: () => apiGet<any>("/dashboard/relatorios-manutencao") });
  if (!data) return <div className="glass p-6 text-center text-slate-400">Carregando...</div>;
  return (
    <div className="glass p-6 rounded-2xl">
      <h3 className="text-lg font-bold text-slate-100 mb-4">Manutenções por Faixa de Hodômetro</h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data.faixas_km}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="faixa" stroke="#94a3b8" tick={{ fontSize: 10 }} tickFormatter={(v: any) => Number(v).toLocaleString('pt-BR')} />
            <YAxis stroke="#94a3b8" allowDecimals={false} />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} />
            <Bar dataKey="quantidade" fill="#0284c7" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function RelatorioDesvioConsumo() {
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });
  const recentes = veiculos.filter((v: any) => manutencoes.some((m: any) => m.veiculo_id === v.id));
  return (
    <div className="glass p-6 rounded-2xl">
      <h3 className="text-lg font-bold text-slate-100 mb-4">Desvio de Consumo (Pós-Manutenção)</h3>
      <Table><TableHeader><TableRow><TableHead>Veículo</TableHead><TableHead>Status</TableHead></TableRow></TableHeader>
      <TableBody>{recentes.map((v: any) => <TableRow key={v.id}><TableCell>{v.placa} - {v.modelo}</TableCell><TableCell className="text-emerald-400 text-xs">Aguardando Telemetria</TableCell></TableRow>)}</TableBody></Table>
    </div>
  );
}

function RelatorioPrevisao() {
  const { data } = useQuery({ queryKey: ["relatorios-manutencao"], queryFn: () => apiGet<any>("/dashboard/relatorios-manutencao") });
  if (!data) return <div className="glass p-6 text-center text-slate-400">Carregando...</div>;
  return (
    <div className="glass p-6 rounded-2xl text-center space-y-4">
      <h3 className="text-lg font-bold text-slate-100 mb-2">Previsão Orçamentária</h3>
      <div className="flex justify-center gap-12">
        <div><p className="text-3xl font-bold text-slate-100">{brl(data.forecast.media_mensal)}</p><p className="text-xs uppercase text-slate-500">Média Mensal</p></div>
        <div><p className="text-3xl font-bold text-amber-400">{brl(data.forecast.proximos_3_meses)}</p><p className="text-xs uppercase text-slate-500">Próximos 3 Meses</p></div>
        <div><p className="text-3xl font-bold text-rose-400">{brl(data.forecast.proximos_6_meses)}</p><p className="text-xs uppercase text-slate-500">Próximos 6 Meses</p></div>
      </div>
    </div>
  );
}

function RelatorioOficinaTempo() {
  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });
  const oficinas: Record<string, { total: number, custo: number }> = {};
  manutencoes.forEach((m: any) => { if (m.oficina && m.custo) { if (!oficinas[m.oficina]) oficinas[m.oficina] = { total: 0, custo: 0 }; oficinas[m.oficina].total += 1; oficinas[m.oficina].custo += m.custo; } });
  const dados = Object.entries(oficinas).map(([nome, d]) => ({ nome, media: d.custo / d.total, total: d.total }));
  return (
    <div className="glass p-6 rounded-2xl">
      <h3 className="text-lg font-bold text-slate-100 mb-4">Tempo vs. Custo por Oficina</h3>
      <Table><TableHeader><TableRow><TableHead>Oficina</TableHead><TableHead>Qtd.</TableHead><TableHead>Custo Médio</TableHead></TableRow></TableHeader>
      <TableBody>{dados.map((d, i) => <TableRow key={i}><TableCell>{d.nome}</TableCell><TableCell>{d.total}</TableCell><TableCell className="text-amber-400">{brl(d.media)}</TableCell></TableRow>)}</TableBody></Table>
    </div>
  );
}

function RelatorioOleoAtraso() {
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: planos = [] } = useQuery({ queryKey: ["planos-manutencao"], queryFn: () => apiGet<any[]>("/planos-manutencao") });
  const atrasados = veiculos.filter((v: any) => { const plano = planos.find((p: any) => p.veiculo_id === v.id && p.familia === "Lubrificação e Filtros"); if (!plano) return false; return (v.hodometro_km || 0) > ((plano.ultima_execucao_km || 0) + (plano.intervalo || 10000)); });
  return (
    <div className="glass p-6 rounded-2xl">
      <h3 className="text-lg font-bold text-slate-100 mb-4">Veículos com Óleo em Atraso</h3>
      <Table><TableHeader><TableRow><TableHead>Veículo</TableHead><TableHead>KM Atual</TableHead></TableRow></TableHeader>
      <TableBody>{atrasados.map((v: any) => <TableRow key={v.id}><TableCell>{v.placa}</TableCell><TableCell className="text-rose-400">{v.hodometro_km} km</TableCell></TableRow>)}</TableBody></Table>
    </div>
  );
}
'''
        # Adiciona no final do arquivo (antes do último fecha-chaves)
        c = c.rstrip()
        if c.endswith('}'):
            c = c[:-1] + componentes + '\n}'
        else:
            c += componentes
        print("✅ Componentes adicionados no final do arquivo.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")