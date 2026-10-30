import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_REL_SEGURO_{agora}.zip")
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

    # 1. Adicionar os novos itens no menu lateral (se não existirem)
    if 'relatorio-ratio' not in c:
        # Localiza o item "MTBF" no menu e insere antes
        alvo = '{ id: "mtbf", label: "MTBF (Entre Falhas)", icon: ShieldAlert },'
        novos_itens = '''{ id: "relatorio-ratio", label: "Ratio Preve. x Corret.", icon: TrendingUp },
        { id: "relatorio-faixa-km", label: "Faixa de Hodômetro", icon: Activity },
        { id: "relatorio-desvio-consumo", label: "Desvio de Consumo", icon: GitCompare },
        { id: "relatorio-previsao", label: "Previsão Orçamentária", icon: DollarSign },
        { id: "relatorio-oficina-tempo", label: "Tempo vs. Custo", icon: Clock },
        { id: "relatorio-oleo-atraso", label: "Óleo em Atraso", icon: RotateCcw },
        ''' + alvo

        if alvo in c:
            c = c.replace(alvo, novos_itens, 1)
            print("✅ Itens do menu adicionados.")
        else:
            print("⚠️ Âncora do menu não encontrada.")

    # 2. Adicionar os cases no renderAba
    if 'case "relatorio-ratio"' not in c:
        alvo_case = 'case "cpk": return'
        novos_cases = '''case "relatorio-ratio": return <RelatorioRatio />;
      case "relatorio-faixa-km": return <RelatorioFaixaKm />;
      case "relatorio-desvio-consumo": return <RelatorioDesvioConsumo />;
      case "relatorio-previsao": return <RelatorioPrevisao />;
      case "relatorio-oficina-tempo": return <RelatorioOficinaTempo />;
      case "relatorio-oleo-atraso": return <RelatorioOleoAtraso />;
      ''' + alvo_case

        if alvo_case in c:
            c = c.replace(alvo_case, novos_cases, 1)
            print("✅ Cases adicionados ao renderAba.")
        else:
            print("⚠️ Case 'cpk' não encontrado.")

    # 3. Adicionar os componentes no final do arquivo (se não existirem)
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
        # Adiciona no final do arquivo
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