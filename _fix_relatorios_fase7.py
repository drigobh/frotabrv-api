import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_RELATORIOS_FASE7_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/routers/dashboard.py",
        "frontend/src/pages/RelatorioManutencao.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    # Adicionar rota de relatórios no backend (para os cálculos pesados)
    caminho = os.path.join(raiz, "app", "backend", "routers", "dashboard.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    if '/relatorios-manutencao' not in c:
        rota = '''
@router.get("/relatorios-manutencao")
async def relatorios_manutencao(_u: dict = Depends(require("read"))):
    # 1. Ratio Preventiva vs. Corretiva
    total = await db.manutencoes.count_documents({})
    preventivas = await db.manutencoes.count_documents({"tipo": "Preventiva"})
    corretivas = await db.manutencoes.count_documents({"tipo": "Corretiva"})
    
    ratio = {
        "total": total,
        "preventivas": preventivas,
        "corretivas": corretivas,
        "percentual_preventiva": (preventivas / total * 100) if total > 0 else 0,
        "percentual_corretiva": (corretivas / total * 100) if total > 0 else 0
    }

    # 2. Manutenções por Faixa de Hodômetro (Agrupado)
    pipeline_km = [
        {"$match": {"km_manutencao": {"$ne": None}}},
        {"$bucket": {
            "groupBy": "$km_manutencao",
            "boundaries": [0, 100000, 200000, 300000, 400000, 500000, 600000, 700000, 800000, 1000000],
            "default": "1000000+",
            "output": {"count": {"$sum": 1}}
        }}
    ]
    faixas = await db.manutencoes.aggregate(pipeline_km).to_list(20)

    # 3. Forecast (Previsão Orçamentária para os próximos 3 meses)
    # Projeta com base na média dos últimos 3 meses
    manutencoes_recentes = await db.manutencoes.find({}, {"custo": 1, "data": 1}).sort("data", -1).to_list(100)
    custos_mensais = {}
    for m in manutencoes_recentes:
        if m.get("data") and m.get("custo"):
            mes = m["data"][:7]
            custos_mensais[mes] = custos_mensais.get(mes, 0) + m["custo"]
    
    ultimos_meses = sorted(custos_mensais.items(), reverse=True)[:3]
    media_mensal = sum(c[1] for c in ultimos_meses) / len(ultimos_meses) if ultimos_meses else 0

    forecast = {
        "media_mensal": media_mensal,
        "proximos_3_meses": media_mensal * 3,
        "proximos_6_meses": media_mensal * 6
    }

    return {
        "ratio": ratio,
        "faixas_km": [{"faixa": str(f["_id"]), "quantidade": f["count"]} for f in faixas],
        "forecast": forecast
    }
'''
        c += rota
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota /relatorios-manutencao adicionada.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "RelatorioManutencao.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar os novos itens no menu lateral
    if 'relatorio-ratio' not in c:
        c = c.replace(
            '''{
              titulo: "Eficiência Operacional",
              itens: [
                { id: "mtbf", label: "MTBF (Entre Falhas)", icon: ShieldAlert },''',
            '''{
              titulo: "Eficiência Operacional",
              itens: [
                { id: "relatorio-ratio", label: "Ratio Preve. x Corret.", icon: TrendingUp },
                { id: "relatorio-faixa-km", label: "Faixa de Hodômetro", icon: Activity },
                { id: "relatorio-desvio-consumo", label: "Desvio de Consumo", icon: GitCompare },
                { id: "relatorio-previsao", label: "Previsão Orçamentária", icon: DollarSign },
                { id: "relatorio-oficina-tempo", label: "Tempo vs. Custo", icon: Clock },
                { id: "relatorio-oleo-atraso", label: "Óleo em Atraso", icon: RotateCcw },
                { id: "mtbf", label: "MTBF (Entre Falhas)", icon: ShieldAlert },'''
        )
        print("✅ Itens do menu adicionados.")

    # 2. Adicionar os cases no renderAba
    novos_cases = '''
      case "relatorio-ratio": return <RelatorioRatio />;
      case "relatorio-faixa-km": return <RelatorioFaixaKm />;
      case "relatorio-desvio-consumo": return <RelatorioDesvioConsumo />;
      case "relatorio-previsao": return <RelatorioPrevisao />;
      case "relatorio-oficina-tempo": return <RelatorioOficinaTempo />;
      case "relatorio-oleo-atraso": return <RelatorioOleoAtraso />;
'''
    if 'case "relatorio-ratio"' not in c:
        c = c.replace(
            '      case "cpk": return',
            novos_cases + '      case "cpk": return'
        )
        print("✅ Cases do renderAba adicionados.")

    # 3. Adicionar os componentes auxiliares no final do arquivo
    componentes = '''

// --- COMPONENTES DE RELATÓRIOS AVANÇADOS ---

function RelatorioRatio() {
  const { data } = useQuery({ queryKey: ["relatorios-manutencao"], queryFn: () => apiGet<any>("/dashboard/relatorios-manutencao") });
  if (!data) return <div className="glass p-6 text-center text-slate-400">Carregando...</div>;

  return (
    <div className="glass p-6 rounded-2xl text-center space-y-4">
      <h3 className="text-lg font-bold text-slate-100 mb-2 flex items-center justify-center gap-2"><TrendingUp className="size-5 text-emerald-400" /> Ratio Preventiva x Corretiva</h3>
      <div className="flex justify-center gap-12">
        <div>
          <p className="text-5xl font-bold text-emerald-400">{data.ratio.percentual_preventiva.toFixed(1)}%</p>
          <p className="text-sm text-slate-400">Preventivas ({data.ratio.preventivas})</p>
        </div>
        <div>
          <p className="text-5xl font-bold text-rose-400">{data.ratio.percentual_corretiva.toFixed(1)}%</p>
          <p className="text-sm text-slate-400">Corretivas ({data.ratio.corretivas})</p>
        </div>
      </div>
      <p className="text-sm text-slate-400 mt-4">Meta recomendada: 80% Preventiva / 20% Corretiva</p>
    </div>
  );
}

function RelatorioFaixaKm() {
  const { data } = useQuery({ queryKey: ["relatorios-manutencao"], queryFn: () => apiGet<any>("/dashboard/relatorios-manutencao") });
  if (!data) return <div className="glass p-6 text-center text-slate-400">Carregando...</div>;

  return (
    <div className="glass p-6 rounded-2xl">
      <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2"><Activity className="size-5 text-sky-400" /> Manutenções por Faixa de Hodômetro</h3>
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
  
  // Simulação: Veículos com manutenção nos últimos 30 dias
  const recentes = veiculos.filter((v: any) => {
    const manuts = manutencoes.filter((m: any) => m.veiculo_id === v.id);
    return manuts.length > 0;
  });

  return (
    <div className="glass p-6 rounded-2xl">
      <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2"><GitCompare className="size-5 text-amber-400" /> Desvio de Consumo (Pós-Manutenção)</h3>
      <p className="text-sm text-slate-400">Veículos com manutenção nos últimos 30 dias. O consumo deve ser comparado antes e depois.</p>
      <Table>
        <TableHeader>
          <TableRow className="border-slate-800">
            <TableHead className="text-xs uppercase text-slate-500">Veículo</TableHead>
            <TableHead className="text-xs uppercase text-slate-500">Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {recentes.map((v: any) => (
            <TableRow key={v.id} className="border-slate-800">
              <TableCell className="text-slate-200">{v.placa} - {v.modelo}</TableCell>
              <TableCell className="text-emerald-400 text-xs">Aguardando Telemetria</TableCell>
            </TableRow>
          ))}
          {recentes.length === 0 && <TableRow><TableCell colSpan={2} className="text-center text-slate-500">Nenhum veículo com manutenção recente.</TableCell></TableRow>}
        </TableBody>
      </Table>
    </div>
  );
}

function RelatorioPrevisao() {
  const { data } = useQuery({ queryKey: ["relatorios-manutencao"], queryFn: () => apiGet<any>("/dashboard/relatorios-manutencao") });
  if (!data) return <div className="glass p-6 text-center text-slate-400">Carregando...</div>;

  return (
    <div className="glass p-6 rounded-2xl text-center space-y-4">
      <h3 className="text-lg font-bold text-slate-100 mb-2 flex items-center justify-center gap-2"><DollarSign className="size-5 text-amber-400" /> Previsão Orçamentária</h3>
      <p className="text-sm text-slate-400 mb-4">Projeção baseada na média dos últimos 3 meses.</p>
      <div className="flex justify-center gap-12">
        <div>
          <p className="text-3xl font-bold text-slate-100">{brl(data.forecast.media_mensal)}</p>
          <p className="text-xs uppercase text-slate-500">Média Mensal</p>
        </div>
        <div>
          <p className="text-3xl font-bold text-amber-400">{brl(data.forecast.proximos_3_meses)}</p>
          <p className="text-xs uppercase text-slate-500">Próximos 3 Meses</p>
        </div>
        <div>
          <p className="text-3xl font-bold text-rose-400">{brl(data.forecast.proximos_6_meses)}</p>
          <p className="text-xs uppercase text-slate-500">Próximos 6 Meses</p>
        </div>
      </div>
    </div>
  );
}

function RelatorioOficinaTempo() {
  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });
  
  // Simulação: Agrupar por oficina e contar tempo médio
  const oficinas: Record<string, { total: number, custo: number }> = {};
  manutencoes.forEach((m: any) => {
    if (m.oficina && m.custo) {
      if (!oficinas[m.oficina]) oficinas[m.oficina] = { total: 0, custo: 0 };
      oficinas[m.oficina].total += 1;
      oficinas[m.oficina].custo += m.custo;
    }
  });

  const dados = Object.entries(oficinas).map(([nome, d]) => ({ nome, media: d.custo / d.total, total: d.total }));

  return (
    <div className="glass p-6 rounded-2xl">
      <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2"><Clock className="size-5 text-sky-400" /> Tempo vs. Custo por Oficina</h3>
      <Table>
        <TableHeader>
          <TableRow className="border-slate-800">
            <TableHead className="text-xs uppercase text-slate-500">Oficina</TableHead>
            <TableHead className="text-xs uppercase text-slate-500">Qtd. Serviços</TableHead>
            <TableHead className="text-xs uppercase text-slate-500">Custo Médio</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {dados.map((d, i) => (
            <TableRow key={i} className="border-slate-800">
              <TableCell className="text-slate-200">{d.nome}</TableCell>
              <TableCell className="text-slate-400">{d.total}</TableCell>
              <TableCell className="text-amber-400">{brl(d.media)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

function RelatorioOleoAtraso() {
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: planos = [] } = useQuery({ queryKey: ["planos-manutencao"], queryFn: () => apiGet<any[]>("/planos-manutencao") });

  const atrasados = veiculos.filter((v: any) => {
    const plano = planos.find((p: any) => p.veiculo_id === v.id && p.familia === "Lubrificação e Filtros");
    if (!plano) return false;
    const limite = (plano.ultima_execucao_km || 0) + (plano.intervalo || 10000);
    return (v.hodometro_km || 0) > limite;
  });

  return (
    <div className="glass p-6 rounded-2xl">
      <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2"><RotateCcw className="size-5 text-rose-400" /> Veículos com Óleo em Atraso</h3>
      <Table>
        <TableHeader>
          <TableRow className="border-slate-800">
            <TableHead className="text-xs uppercase text-slate-500">Veículo</TableHead>
            <TableHead className="text-xs uppercase text-slate-500">KM Atual</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {atrasados.map((v: any) => (
            <TableRow key={v.id} className="border-slate-800">
              <TableCell className="text-slate-200">{v.placa} - {v.modelo}</TableCell>
              <TableCell className="text-rose-400 font-mono">{(v.hodometro_km || 0).toLocaleString('pt-BR')} km</TableCell>
            </TableRow>
          ))}
          {atrasados.length === 0 && <TableRow><TableCell colSpan={2} className="text-center text-slate-500">Nenhum veículo com óleo em atraso.</TableCell></TableRow>}
        </TableBody>
      </Table>
    </div>
  );
}
'''
    if 'function RelatorioRatio' not in c:
        # Remove o último fechamento de chaves do arquivo para adicionar os componentes
        c = c.rstrip()
        if c.endswith('}'):
            c = c[:-1] + componentes + '\n}'
        print("✅ Componentes auxiliares adicionados.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend atualizado com os novos relatórios.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso!")