import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_FILTROS_RELATORIOS_{agora}.zip")
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

    # 1. Adicionar estados dos filtros
    if 'filtroDataInicio' not in c:
        c = c.replace(
            'const [abaAtiva, setAbaAtiva] = useState("cpk");',
            '''const [abaAtiva, setAbaAtiva] = useState("cpk");
  const [filtroDataInicio, setFiltroDataInicio] = useState("");
  const [filtroDataFim, setFiltroDataFim] = useState("");
  const [filtroTipo, setFiltroTipo] = useState("__all__");
  const [filtroVeiculo, setFiltroVeiculo] = useState("__all__");
  const [filtroEmpresa, setFiltroEmpresa] = useState("__all__");
  const [filtroOficina, setFiltroOficina] = useState("__all__");'''
        )
        print("✅ Estados dos filtros adicionados.")

    # 2. Adicionar a lógica de filtragem global
    if 'const manutencoesFiltradas' not in c:
        c = c.replace(
            'const cpkData = useMemo(() => {',
            '''// FILTRAGEM GLOBAL
  const manutencoesFiltradas = useMemo(() => {
    let filtered = manutencoes;
    
    if (filtroDataInicio) {
      filtered = filtered.filter((m: any) => m.data >= filtroDataInicio);
    }
    if (filtroDataFim) {
      filtered = filtered.filter((m: any) => m.data <= filtroDataFim);
    }
    if (filtroTipo !== "__all__") {
      filtered = filtered.filter((m: any) => m.tipo === filtroTipo);
    }
    if (filtroVeiculo !== "__all__") {
      filtered = filtered.filter((m: any) => m.veiculo_id === filtroVeiculo);
    }
    if (filtroOficina !== "__all__") {
      filtered = filtered.filter((m: any) => m.oficina === filtroOficina);
    }
    // Filtro por empresa: busca os veículos daquela empresa
    if (filtroEmpresa !== "__all__") {
      const veiculosEmpresa = veiculos.filter((v: any) => v.empresa_id === filtroEmpresa).map((v: any) => v.id);
      filtered = filtered.filter((m: any) => veiculosEmpresa.includes(m.veiculo_id));
    }

    return filtered;
  }, [manutencoes, filtroDataInicio, filtroDataFim, filtroTipo, filtroVeiculo, filtroEmpresa, filtroOficina, veiculos]);

  // Dados para os selects
  const listaOficinas = [...new Set(manutencoes.map((m: any) => m.oficina).filter(Boolean))].sort();

  const cpkData = useMemo(() => {'''
        )
        print("✅ Lógica de filtragem adicionada.")

    # 3. Substituir as referências de "manutencoes" por "manutencoesFiltradas" nos cálculos
    c = c.replace('manutencoes.forEach', 'manutencoesFiltradas.forEach')
    c = c.replace('manutencoes.filter', 'manutencoesFiltradas.filter')
    c = c.replace('}, [manutencoes]', '}, [manutencoesFiltradas]')
    c = c.replace('}, [manutencoes, veiculos]', '}, [manutencoesFiltradas, veiculos]')
    c = c.replace('}, [manutencoes, veiculos, empresas]', '}, [manutencoesFiltradas, veiculos, empresas]')
    c = c.replace('}, [veiculos, manutencoes, abastecimentos]', '}, [veiculos, manutencoesFiltradas, abastecimentos]')
    print("✅ Referências atualizadas para a lista filtrada.")

    # 4. Adicionar a Barra de Filtros no topo (após o PageHeader)
    if 'Barra de Filtros' not in c:
        filtros_ui = '''
      {/* Barra de Filtros */}
      <div className="glass p-4 rounded-xl mb-6 flex flex-wrap gap-3 items-end">
        <div className="flex flex-col gap-1">
          <Label className="text-[10px] uppercase text-slate-500">Data Início</Label>
          <Input type="date" value={filtroDataInicio} onChange={(e) => setFiltroDataInicio(e.target.value)} className="h-9 w-36 bg-slate-950" />
        </div>
        <div className="flex flex-col gap-1">
          <Label className="text-[10px] uppercase text-slate-500">Data Fim</Label>
          <Input type="date" value={filtroDataFim} onChange={(e) => setFiltroDataFim(e.target.value)} className="h-9 w-36 bg-slate-950" />
        </div>
        <div className="flex flex-col gap-1">
          <Label className="text-[10px] uppercase text-slate-500">Tipo</Label>
          <select value={filtroTipo} onChange={(e) => setFiltroTipo(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-xs text-slate-300 px-2 w-32">
            <option value="__all__">Todos</option>
            <option value="Preventiva">Preventiva</option>
            <option value="Corretiva">Corretiva</option>
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <Label className="text-[10px] uppercase text-slate-500">Veículo</Label>
          <select value={filtroVeiculo} onChange={(e) => setFiltroVeiculo(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-xs text-slate-300 px-2 w-44">
            <option value="__all__">Todos os Veículos</option>
            {veiculos.map((v: any) => <option key={v.id} value={v.id}>{v.placa} - {v.modelo}</option>)}
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <Label className="text-[10px] uppercase text-slate-500">Filial</Label>
          <select value={filtroEmpresa} onChange={(e) => setFiltroEmpresa(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-xs text-slate-300 px-2 w-40">
            <option value="__all__">Todas</option>
            {empresas.map((e: any) => <option key={e.id} value={e.id}>{e.nome_fantasia || e.razao_social}</option>)}
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <Label className="text-[10px] uppercase text-slate-500">Oficina</Label>
          <select value={filtroOficina} onChange={(e) => setFiltroOficina(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-xs text-slate-300 px-2 w-40">
            <option value="__all__">Todas</option>
            {listaOficinas.map((o: any) => <option key={o} value={o}>{o}</option>)}
          </select>
        </div>
        <Button variant="ghost" size="sm" onClick={() => { setFiltroDataInicio(""); setFiltroDataFim(""); setFiltroTipo("__all__"); setFiltroVeiculo("__all__"); setFiltroEmpresa("__all__"); setFiltroOficina("__all__"); }} className="text-xs text-red-400 hover:text-red-300 h-9">
          Limpar Filtros
        </Button>
      </div>
'''
        c = c.replace('      <div className="flex gap-6">', filtros_ui + '      <div className="flex gap-6">')
        print("✅ Barra de Filtros adicionada.")

    # 5. Garantir imports do Input e Label
    if 'import { Input }' not in c:
        c = c.replace('import { Table,', 'import { Input } from "@/components/ui/input";\nimport { Label } from "@/components/ui/label";\nimport { Table,')
        print("✅ Imports de Input e Label adicionados.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")