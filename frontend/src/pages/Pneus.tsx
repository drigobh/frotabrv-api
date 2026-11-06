import { useState, useMemo, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { BarChart3, Plus, Pencil, Trash2, Disc, Search, AlertTriangle, RefreshCw, ArrowRightLeft, ShieldAlert, CheckCircle2, Activity, X, Wrench, FileDown, FileSpreadsheet, Truck, Container, Upload, Loader2, ArrowLeftRight, QrCode } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";
import { ChassiMapa } from "@/components/ChassiMapa";
import { brl } from "@/lib/format";
import * as XLSX from "xlsx";

const parseDate = (val: any): string => {
  if (!val) return "";
  if (val instanceof Date) {
    if (isNaN(val.getTime())) return "";
    return `${val.getFullYear()}-${String(val.getMonth()+1).padStart(2,'0')}-${String(val.getDate()).padStart(2,'0')}`;
  }
  const str = String(val).trim();
  if (!str) return "";
  if (/^\d{4}-\d{2}-\d{2}/.test(str)) return str.slice(0, 10);
  if (/^\d+(\.\d+)?$/.test(str)) {
    const num = parseFloat(str);
    if (num > 1000) {
      const d = new Date((num - 25569) * 86400 * 1000);
      return `${d.getUTCFullYear()}-${String(d.getUTCMonth()+1).padStart(2,'0')}-${String(d.getUTCDate()).padStart(2,'0')}`;
    }
  }
  const parts = str.split(/[\/\-]/);
  if (parts.length === 3) {
     let p1 = parseInt(parts[0]), p2 = parseInt(parts[1]), p3 = parseInt(parts[2]);
     let d, m, y;
     if (p3 > 1000) { y = p3; } else { y = p3 + 2000; }
     if (p1 > 12) { d = p1; m = p2; } else { m = p1; d = p2; }
     if (d >= 1 && d <= 31 && m >= 1 && m <= 12) {
         return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
     }
  }
  return "";
};

export default function Pneus() {
  const qc = useQueryClient();
  const [abaAtiva, setAbaAtiva] = useState<"cadastrados" | "movimentacao" | "manutencao" | "estoque" | "dashboard">("cadastrados");
  
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [importOpen, setImportOpen] = useState(false);
  const [importProgresso, setImportProgresso] = useState(0);
  const [importTotal, setImportTotal] = useState(0);
  const [importProcessados, setImportProcessados] = useState(0);
  const [importErros, setImportErros] = useState<string[]>([]);
  const [importando, setImportando] = useState(false);

  // Estados do Checklist Borracheiro
  const [checklistOpen, setChecklistOpen] = useState(false);
  const [pneuChecklist, setPneuChecklist] = useState<any>(null);
  const [formChecklist, setFormChecklist] = useState({ tipo: "RETORNO", avaliacao: "APROVADA", borracheiro: "", obs: "", km: "" });

  const [filtro, setFiltro] = useState("");
  const [filtroMarca, setFiltroMarca] = useState("");
  const [filtroMedida, setFiltroMedida] = useState("");
  const [filtroTipo, setFiltroTipo] = useState("");
  const [filtroStatus, setFiltroStatus] = useState("");

  const [tipoAtivo, setTipoAtivo] = useState<"cavalo" | "carreta">("cavalo");
  const [veiculoMapa, setVeiculoMapa] = useState<string>("");
  const [buscaPlaca, setBuscaPlaca] = useState("");

  const { data: pneus = [] } = useQuery({ queryKey: ["pneus"], queryFn: () => apiGet<any[]>("/pneus") });
  const { data: dash = { total: 0, aplicados: 0, sucateados: 0, sulco_critico: 0, top_marcas: [] } } = useQuery({ queryKey: ["pneus-dashboard"], queryFn: () => apiGet<any>("/pneus/dashboard") });
  const { data: carretas = [] } = useQuery({ queryKey: ["carretas"], queryFn: () => apiGet<any[]>("/carretas") });
  const { data: veiculosApi = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: marcasDb = [] } = useQuery({ queryKey: ["marcas-pneus"], queryFn: () => apiGet<any[]>("/pneus/marcas") });
  const { data: medidasDb = [] } = useQuery({ queryKey: ["medidas-pneus"], queryFn: () => apiGet<any[]>("/pneus/medidas") });
  const { data: modelosDb = [] } = useQuery({ queryKey: ["modelos-pneus"], queryFn: () => apiGet<any[]>("/pneus/modelos") });
  const { data: config } = useQuery({ queryKey: ["parametrizacao-meta"], queryFn: () => apiGet<any>("/parametrizacao/meta") });

  const [form, setForm] = useState({
    numero_fogo: "", marca: "", modelo: "", medida: "", dot: "", tipo: "Tração", status: "Estoque", custo_aquisicao: "", observacoes: "",
    equipamento: "", posicao: "", banda_rod: "", estrutura: "", n_serie: "", n_recap: "", data_compra: "", data_descarte: "",
    custo_total_atual: "", profundidade_atual: "", uso_atual: "", custo_por_km: "", km_posicao: ""
  });

  const stats = useMemo(() => {
    const total = pneus.length;
    const sucateados = pneus.filter((p: any) => p.status === "Sucateado").length;
    const emManutencao = pneus.filter((p: any) => ["Recapagem", "Conserto"].includes(p.status)).length;
    const emEstoque = pneus.filter((p: any) => p.status === "Estoque");
    
    const marcasCount: Record<string, number> = {};
    pneus.forEach((p: any) => {
      if (p.marca) marcasCount[p.marca] = (marcasCount[p.marca] || 0) + 1;
    });
    const topMarcas = Object.entries(marcasCount).sort((a, b) => b[1] - a[1]).slice(0, 5);

    const custoCompra = pneus.reduce((acc: number, p: any) => acc + (Number(p.custo_aquisicao) || 0), 0);
    const custoManutencao = emManutencao * 150;

    return { total, sucateados, emManutencao, topMarcas, emEstoque, custoCompra, custoManutencao };
  }, [pneus]);

  const veiculosFiltrados = useMemo(() => {
    const lista = tipoAtivo === "cavalo" 
      ? (veiculosApi ?? []).map((v: any) => ({ id: v.id, label: `${v.placa} - ${v.modelo}`, template_chassi_id: v.template_chassi_id }))
      : carretas.map((c: any) => ({ id: c.id, label: `${c.codigo} - ${c.tipo}`, template_chassi_id: c.template_chassi_id }));

    if (!buscaPlaca) return lista;
    return lista.filter((v: any) => v.label.toLowerCase().includes(buscaPlaca.toLowerCase()));
  }, [veiculosApi, carretas, tipoAtivo, buscaPlaca]);

  const veiculoSelecionado = tipoAtivo === "cavalo" ? veiculosApi.find((v: any) => v.id === veiculoMapa) : carretas.find((c: any) => c.id === veiculoMapa);

  const salvar = useMutation({
    mutationFn: () => {
      const payload = { ...form, custo_aquisicao: Number(String(form.custo_aquisicao).replace(",", ".")) || 0 };
      return editingId ? apiPut(`/pneus/${editingId}`, payload) : apiPost("/pneus", payload);
    },
    onSuccess: () => { toast.success("Pneu salvo!"); setOpen(false); qc.invalidateQueries({ queryKey: ["pneus"] }); qc.invalidateQueries({ queryKey: ["pneus-dashboard"] }); },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/pneus/${id}`),
    onSuccess: () => { toast.success("Pneu excluído."); setExcluirId(null); qc.invalidateQueries({ queryKey: ["pneus"] }); qc.invalidateQueries({ queryKey: ["pneus-dashboard"] }); }
  });

  const movimentar = useMutation({
    mutationFn: ({ pneu_id, status, dados }: { pneu_id: string, status: string, dados?: any }) => {
      const p = pneus.find((x:any) => x.id === pneu_id);
      return apiPut(`/pneus/${pneu_id}`, { ...p, status, ...dados });
    },
    onSuccess: () => {
      toast.success("Ação registrada com sucesso!");
      qc.invalidateQueries({ queryKey: ["pneus"] });
      qc.invalidateQueries({ queryKey: ["pneus-dashboard"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const abrirNovo = () => { 
    setEditingId(null); 
    setForm({ numero_fogo: "", marca: "", modelo: "", medida: "", dot: "", tipo: "Tração", status: "Estoque", custo_aquisicao: "", observacoes: "", equipamento: "", posicao: "", banda_rod: "", estrutura: "", n_serie: "", n_recap: "", data_compra: "", data_descarte: "", custo_total_atual: "", profundidade_atual: "", uso_atual: "", custo_por_km: "", km_posicao: "" }); 
    setOpen(true); 
  };

  const abrirEdicao = (r: any) => { 
    setEditingId(r.id); 
    setForm({ ...r, custo_aquisicao: String(r.custo_aquisicao || ""), equipamento: r.equipamento || "", posicao: r.posicao || "", banda_rod: r.banda_rod || "", estrutura: r.estrutura || "", n_serie: r.n_serie || "", n_recap: r.n_recap || "", data_compra: parseDate(r.data_compra), data_descarte: parseDate(r.data_descarte), custo_total_atual: r.custo_total_atual || "", profundidade_atual: r.profundidade_atual || "", uso_atual: r.uso_atual || "", custo_por_km: r.custo_por_km || "", km_posicao: r.km_posicao || "" }); 
    setOpen(true); 
  };

  const getValor = (row: any, ...chaves: string[]) => {
    for (const chave of chaves) {
      const valor = row[chave];
      if (valor !== undefined && valor !== null && String(valor).trim() !== "") return String(valor).trim();
    }
    return "";
  };

  const handleImportFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (evt) => {
      try {
        const bstr = evt.target?.result;
        const wb = XLSX.read(bstr, { type: 'binary' });
        const wsname = wb.SheetNames[0];
        const ws = wb.Sheets[wsname];
        const data: any[] = XLSX.utils.sheet_to_json(ws, { defval: "", raw: true });
        
        if (data.length === 0) { toast.error("A planilha está vazia."); return; }

        const payload = data.map((row: any) => {
          const numero_fogo = getValor(row, "Marca Fogo", "MarcaFogo", "Nº Fogo", "N.º Fogo", "Fogo");
          const marca = getValor(row, "Marca", "MARCA");
          const modelo = getValor(row, "Modelo", "MODELO");
          const medida = getValor(row, "Tamanho", "Medida", "TAMANHO", "MEDIDA").replace(",", ".").replace(" ", "/");
          
          if (!numero_fogo || !marca) return null;

          const data_descarte_raw = getValor(row, "Data Descarte", "DataDescarte", "Descarte");
          const data_compra_raw = getValor(row, "Data Compra", "DataCompra", "Compra");
          const equipamento = getValor(row, "Equipamento", "EQUIPAMENTO", "Equip.", "Placa");
          
          let status = "Estoque";
          if (data_descarte_raw) status = "Sucateado";
          else if (equipamento) status = "Aplicado";

          const tipo_raw = getValor(row, "Tipo", "TIPO").toUpperCase();
          let tipo = "Misto";
          if (tipo_raw === "LISO" || tipo_raw === "BORRACHUDO") tipo = "Misto";
          else if (tipo_raw === "DIRECIONAL") tipo = "Direcional";
          else if (tipo_raw === "TRACAO" || tipo_raw === "TRAÇÃO") tipo = "Tração";
          else if (tipo_raw === "BANDA") tipo = "Banda";

          return {
            numero_fogo, marca, modelo, medida, dot: getValor(row, "DOT", "Dot"), tipo, status,
            custo_aquisicao: Number(getValor(row, "Custo Total Atual", "CustoTotalAtual", "Custo", "Custo Aquisição").replace(".", "").replace(",", ".")) || 0,
            equipamento, posicao: getValor(row, "Posição", "Posicao", "POSIÇÃO", "Posição Pneu"),
            banda_rod: getValor(row, "Banda Rod.", "BandaRod", "Banda", "BANDA ROD."), estrutura: getValor(row, "Estrutura", "ESTRUTURA"),
            n_serie: getValor(row, "N.º Série", "NSerie", "N Serie", "Número de Série", "Serie"), n_recap: getValor(row, "N.º Recap.", "NRecap", "N Recap", "Recapagem", "Recap"),
            data_compra: parseDate(data_compra_raw), data_descarte: parseDate(data_descarte_raw),
            custo_total_atual: Number(getValor(row, "Custo Total Atual", "CustoTotalAtual").replace(".", "").replace(",", ".")) || 0,
            profundidade_atual: Number(getValor(row, "Profundidade Atual", "ProfundidadeAtual", "Profundidade").replace(",", ".")) || 0,
            uso_atual: getValor(row, "Uso Atual", "UsoAtual", "Uso", "KM na Posição", "KM"),
            custo_por_km: Number(getValor(row, "Custo por KM", "CustoPorKM", "Custo KM", "CPK").replace(",", ".")) || 0,
            km_posicao: Number(getValor(row, "KM na Posição", "KMnaPosicao", "KM Posição", "KM").replace(".", "").replace(",", ".")) || 0,
          };
        }).filter((p): p is any => p !== null);

        if (payload.length === 0) { toast.error("Nenhum pneu válido encontrado."); return; }

        setImportOpen(true); setImportTotal(payload.length); setImportProcessados(0); setImportProgresso(0); setImportErros([]); setImportando(true);

        let processados = 0;
        const interval = setInterval(() => {
          processados += Math.ceil(payload.length / 20);
          if (processados >= payload.length) { processados = payload.length; clearInterval(interval); }
          setImportProcessados(processados); setImportProgresso(Math.round((processados / payload.length) * 100));
        }, 200);

        const res = await apiPost<any>("/pneus/importar", payload);
        clearInterval(interval);
        
        setImportProcessados(payload.length); setImportProgresso(100); setImportando(false);
        if (res.erros?.length > 0) setImportErros(res.erros);

        qc.invalidateQueries({ queryKey: ["pneus"] }); qc.invalidateQueries({ queryKey: ["pneus-dashboard"] });
      } catch (err) {
        setImportando(false); toast.error("Erro ao ler a planilha.");
      }
    };
    reader.readAsBinaryString(file);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const pneusFiltrados = useMemo(() => {
    return pneus.filter((p: any) => {
      const matchText = !filtro || p.numero_fogo.toLowerCase().includes(filtro.toLowerCase()) || p.marca.toLowerCase().includes(filtro.toLowerCase());
      const matchMarca = !filtroMarca || p.marca === filtroMarca;
      const matchMedida = !filtroMedida || p.medida === filtroMedida;
      const matchTipo = !filtroTipo || p.tipo === filtroTipo;
      const matchStatus = !filtroStatus || p.status === filtroStatus;
      return matchText && matchMarca && matchMedida && matchTipo && matchStatus;
    });
  }, [pneus, filtro, filtroMarca, filtroMedida, filtroTipo, filtroStatus]);

  const statusColor = (status: string) => {
    if (status === "Estoque") return "bg-sky-500/20 text-sky-400";
    if (status === "Aplicado") return "bg-emerald-600 text-white";
    if (status === "Recapagem" || status === "Conserto") return "bg-amber-600 text-white";
    if (status === "Sucateado") return "bg-rose-600 text-white";
    return "bg-slate-800 text-slate-400";
  };

  const StatusIcon = ({ status }: { status: string }) => {
    if (status === "Aplicado") return <span title="Rodando"><Disc className="size-4 text-white mr-2 inline" /></span>;
    if (status === "Conserto" || status === "Recapagem") return <span title="Em Manutenção"><Disc className="size-4 text-white mr-2 inline animate-pulse" /></span>;
    if (status === "Sucateado") return <span title="Sucateado"><X className="size-4 text-white mr-2 inline" /></span>;
    if (status === "Estoque") return <span title="Em Estoque"><Disc className="size-4 text-sky-400 mr-2 inline" /></span>;
    return <span title="Desconhecido"><Disc className="size-4 text-slate-400 mr-2 inline" /></span>;
  };

  const getInfoAplicacao = (p: any) => {
    let placa = "—", tipoAtivo = "", km = "—";
    if (p.veiculo_id) {
      const v = veiculosApi.find((v: any) => v.id === p.veiculo_id);
      if (v) { placa = v.placa; tipoAtivo = "Cavalo"; if (v.hodometro_km) km = `${v.hodometro_km.toLocaleString('pt-BR')} km`; }
    } else if (p.carreta_id) {
      const c = carretas.find((c: any) => c.id === p.carreta_id);
      if (c) { placa = c.codigo; tipoAtivo = "Carreta"; }
    }
    if (p.km_aplicacao && km === "—") km = `${Number(p.km_aplicacao).toLocaleString('pt-BR')} km`;
    return { placa, tipoAtivo, km, quemAplicou: p.updated_by || p.created_by || "Usuário do Sistema" };
  };

  const exportToExcel = () => {
    const headers = ["Nº Fogo", "Marca", "Modelo", "Medida", "DOT", "Tipo", "Status", "Custo (R$)"];
    const rows = pneusFiltrados.map((p: any) => [p.numero_fogo, p.marca, p.modelo || "-", p.medida, p.dot || "-", p.tipo, p.status, String(p.custo_aquisicao || 0).replace(".", ",")]);
    const csvContent = [headers, ...rows].map(e => e.join(";")).join("\n");
    const blob = new Blob(["\uFEFF" + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a"); link.href = URL.createObjectURL(blob); link.download = `Relatorio_Pneus_${new Date().toISOString().split('T')[0]}.csv`; link.click();
    toast.success("Download do Excel iniciado!");
  };

  const exportToPDF = () => {
    const printWindow = window.open('', '_blank');
    if (!printWindow) { toast.error("Permita pop-ups."); return; }
    const html = `<html><head><title>Relatório de Pneus</title><style>body{font-family:sans-serif;padding:20px}table{width:100%;border-collapse:collapse}th,td{border:1px solid #ccc;padding:8px;font-size:12px;text-align:left}th{background:#f1f5f9}</style></head><body><h2>Relatório de Pneus</h2><table><thead><tr><th>Nº Fogo</th><th>Marca/Modelo</th><th>Medida</th><th>DOT</th><th>Tipo</th><th>Status</th><th>Custo</th></tr></thead><tbody>${pneusFiltrados.map((p: any) => `<tr><td><strong>${p.numero_fogo}</strong></td><td>${p.marca} ${p.modelo ? '/ ' + p.modelo : ''}</td><td>${p.medida}</td><td>${p.dot || '-'}</td><td>${p.tipo}</td><td>${p.status}</td><td>R$ ${Number(p.custo_aquisicao || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td></tr>`).join('')}</tbody></table></body></html>`;
    printWindow.document.write(html); printWindow.document.close(); printWindow.focus(); setTimeout(() => { printWindow.print(); printWindow.close(); }, 500);
  };

  return (
    <div>

      

      <PageHeader
        eyebrow="Operação"
        title="Controle de Pneus"
        description="Gestão completa de pneus, oficina e sucata."
        actions={
          <div className="flex gap-2">
            {config?.mostrar_importacao_pneus && (
              <>
                <input type="file" accept=".xlsx, .xls, .csv" ref={fileInputRef} onChange={handleImportFile} className="hidden" />
                <Button onClick={() => fileInputRef.current?.click()} variant="outline" className="border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10 h-9"><Upload className="size-4 mr-2" /> Importar Planilha</Button>
              </>
            )}
            <a href="/operacao/pneus/scanner"><Button variant="outline" className="border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10 h-9 mr-2"><QrCode className="size-4 mr-2" /> Scanner QR Code</Button></a>
            <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Novo Pneu</Button>
          </div>
        }
      />

      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-6 mb-6">
        <div className="glass p-3 rounded-xl flex justify-between items-center">
          <div><p className="text-[10px] uppercase text-slate-400">Total</p><p className="text-xl font-bold text-slate-100">{stats.total}</p></div><Disc className="size-5 text-sky-400" />
        </div>
        <div className="glass p-3 rounded-xl flex justify-between items-center border border-amber-500/30">
          <div><p className="text-[10px] uppercase text-slate-400">Manutenção</p><p className="text-xl font-bold text-amber-400">{stats.emManutencao}</p></div><Wrench className="size-5 text-amber-400" />
        </div>
        <div className="glass p-3 rounded-xl flex justify-between items-center">
          <div><p className="text-[10px] uppercase text-slate-400">Sucateados</p><p className="text-xl font-bold text-rose-400">{stats.sucateados}</p></div><Trash2 className="size-5 text-rose-400" />
        </div>
        <div className="glass p-3 rounded-xl flex flex-col justify-center">
          <p className="text-[10px] uppercase text-slate-400">Top Marcas</p><p className="text-xs text-sky-400 font-bold truncate">{stats.topMarcas[0]?.[0] || "—"}</p>
        </div>
        <div className="glass p-3 rounded-xl flex flex-col justify-center border-l-2 border-white">
          <p className="text-[10px] uppercase text-slate-400">Custo Compra</p><p className="text-sm font-bold text-white">{brl(stats.custoCompra)}</p>
        </div>
        <div className="glass p-3 rounded-xl flex flex-col justify-center border-l-2 border-rose-500">
          <p className="text-[10px] uppercase text-slate-400">Custo Manutenção</p><p className="text-sm font-bold text-rose-500">{brl(stats.custoManutencao)}</p>
        </div>
      </div>

      <div className="flex gap-2 mb-4 border-b border-slate-800 pb-2 overflow-x-auto">
        <button className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${abaAtiva === 'cadastrados' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => setAbaAtiva('cadastrados')}><Disc className="size-4 inline mr-2" /> Cadastrados</button>
        <button className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${abaAtiva === 'movimentacao' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => setAbaAtiva('movimentacao')}><ArrowRightLeft className="size-4 inline mr-2" /> Movimentação (Chassi)</button>
        <button className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${abaAtiva === 'manutencao' ? 'bg-slate-800 text-amber-400' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => setAbaAtiva('manutencao')}><Wrench className="size-4 inline mr-2" /> Borracharia</button>
        <button className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${abaAtiva === 'estoque' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => setAbaAtiva('estoque')}><RefreshCw className="size-4 inline mr-2" /> Estoque x Envio</button>
        <button className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${abaAtiva === 'dashboard' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => setAbaAtiva('dashboard')}><BarChart3 className="size-4 inline mr-2" /> Indicadores</button>
      </div>

      {abaAtiva === "cadastrados" && (
        <div>
          <div className="mb-4 flex gap-2 flex-wrap items-center">
            <div className="relative w-64"><Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" /><Input placeholder="Buscar Nº fogo ou marca..." value={filtro} onChange={(e) => setFiltro(e.target.value)} className="pl-9 h-9" /></div>
            <select value={filtroMarca} onChange={(e) => setFiltroMarca(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3"><option value="">Todas as Marcas</option>{marcasDb.map((m: any) => <option key={m.id} value={m.nome}>{m.nome}</option>)}</select>
            <select value={filtroMedida} onChange={(e) => setFiltroMedida(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3"><option value="">Todas as Medidas</option>{medidasDb.map((m: any) => <option key={m.id} value={m.medida}>{m.medida}</option>)}</select>
            <select value={filtroTipo} onChange={(e) => setFiltroTipo(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3"><option value="">Todos os Tipos</option>{TIPOS_PNEU.map((t: string) => <option key={t} value={t}>{t}</option>)}</select>
            <select value={filtroStatus} onChange={(e) => setFiltroStatus(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3"><option value="">Todos os Status</option>{STATUS_PNEU.map((s: string) => <option key={s} value={s}>{s}</option>)}</select>
            <div className="flex gap-2 ml-auto">
              <Button onClick={exportToExcel} variant="outline" className="h-9 border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10"><FileSpreadsheet className="size-4 mr-2" /> Excel</Button>
              <Button onClick={exportToPDF} variant="outline" className="h-9 border-rose-500/40 text-rose-400 hover:bg-rose-500/10"><FileDown className="size-4 mr-2" /> PDF</Button>
            </div>
          </div>
          <div className="glass rounded-2xl overflow-visible">
            <Table>
              <TableHeader>
                <TableRow className="border-slate-800">
                  <TableHead className="text-xs uppercase text-slate-500">Nº Fogo</TableHead><TableHead className="text-xs uppercase text-slate-500">Marca / Modelo</TableHead><TableHead className="text-xs uppercase text-slate-500">Medida</TableHead><TableHead className="text-xs uppercase text-slate-500">DOT</TableHead><TableHead className="text-xs uppercase text-slate-500">Tipo</TableHead><TableHead className="text-xs uppercase text-slate-500">Status</TableHead><TableHead className="text-xs uppercase text-slate-500">Custo</TableHead><TableHead className="text-xs uppercase text-slate-500 text-right pr-6">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pneusFiltrados.length === 0 ? (<TableRow><TableCell colSpan={8} className="text-center py-8 text-slate-500">Nenhum pneu encontrado.</TableCell></TableRow>) : (
                  pneusFiltrados.map((p: any) => {
                    const info = getInfoAplicacao(p);
                    return (
                      <TableRow key={p.id} className="border-slate-800 hover:bg-slate-800/30">
                        <TableCell className="font-bold text-slate-100"><StatusIcon status={p.status} /> {p.numero_fogo}</TableCell>
                        <TableCell className="text-slate-300">{p.marca} {p.modelo && `/ ${p.modelo}`}</TableCell>
                        <TableCell className="text-slate-400 font-mono">{p.medida}</TableCell>
                        <TableCell className="text-slate-400">{p.dot || "—"}</TableCell>
                        <TableCell className="text-slate-400">{p.tipo}</TableCell>
                        <TableCell><span className={`px-2 py-0.5 rounded text-[10px] font-bold ${statusColor(p.status)}`}>{p.status}</span></TableCell>
                        <TableCell className="text-amber-400 font-mono">{brl(p.custo_aquisicao)}</TableCell>
                        <TableCell className="text-right pr-6">
                          <div className="flex items-center justify-end gap-1">
                            {p.status === "Aplicado" && (
                              <div className="relative group inline-block">
                                <Button size="icon-sm" variant="ghost" className="cursor-help">{p.veiculo_id ? <Truck className="size-4 text-emerald-400" /> : <Container className="size-4 text-emerald-400" />}</Button>
                                <div className="absolute top-1/2 -translate-y-1/2 right-full mr-2 hidden group-hover:block w-48 bg-slate-800 border border-slate-700 rounded-lg p-3 text-xs z-50 shadow-xl pointer-events-none">
                                  <p className="font-bold text-slate-100 mb-1">Aplicado em:</p><p className="text-slate-300">{info.placa} ({info.tipoAtivo})</p><p className="text-slate-400 mt-2">KM: <span className="text-slate-200">{info.km}</span></p><p className="text-slate-400">Por: <span className="text-slate-200">{info.quemAplicou}</span></p>
                                </div>
                              </div>
                            )}
                            <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(p)}><Pencil className="size-4 text-sky-400" /></Button>
                            <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(p.id)}><Trash2 className="size-4 text-red-300" /></Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </div>
        </div>
      )}

      {abaAtiva === "movimentacao" && (
        <div>
          <div className="flex items-center gap-4 mb-4 flex-wrap">
            <h3 className="text-lg font-bold text-slate-100">Chassi do Veículo</h3>
            <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-700">
              <button className={`px-3 py-1 text-sm rounded-md font-medium ${tipoAtivo === 'cavalo' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => { setTipoAtivo('cavalo'); setVeiculoMapa(''); }}>Cavalo</button>
              <button className={`px-3 py-1 text-sm rounded-md font-medium ${tipoAtivo === 'carreta' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => { setTipoAtivo('carreta'); setVeiculoMapa(''); }}>Carreta</button>
            </div>
            <div className="relative w-64"><Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" /><Input placeholder={tipoAtivo === 'cavalo' ? "Buscar placa..." : "Buscar código..."} value={buscaPlaca} onChange={(e) => setBuscaPlaca(e.target.value)} className="pl-9 h-9" /></div>
            <select value={veiculoMapa} onChange={(e) => setVeiculoMapa(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3 min-w-[200px]"><option value="">Selecione...</option>{veiculosFiltrados.map((v: any) => (<option key={v.id} value={v.id}>{v.label}</option>))}</select>
          </div>
          {veiculoMapa ? (<ChassiMapa pneus={pneus} veiculoId={veiculoMapa} tipo={tipoAtivo} templateChassiId={veiculoSelecionado?.template_chassi_id} />) : (
            <div className="glass p-6 rounded-2xl text-center text-slate-500"><p className="text-sm">Selecione um veículo acima para visualizar o chassi.</p></div>
          )}
        </div>
      )}

      {abaAtiva === "manutencao" && (
        <div className="space-y-6">
          <div className="glass p-6 rounded-2xl border border-amber-500/30 bg-amber-950/10">
            <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
              <Wrench className="size-5 text-amber-400" /> Pneus na Borracharia
            </h3>
            {pneus.filter((p: any) => ["Recapagem", "Conserto"].includes(p.status)).length === 0 ? (
              <div className="text-center py-12 text-slate-500 flex flex-col items-center"><CheckCircle2 className="size-12 text-slate-700 mb-4" /><p>Nenhum pneu na oficina no momento.</p></div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {pneus.filter((p: any) => ["Recapagem", "Conserto"].includes(p.status)).map((p: any) => (
                  <div key={p.id} className="glass p-4 rounded-xl border border-amber-500/50 hover:scale-[1.02] transition-transform">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <p className="text-base font-bold text-amber-400">{p.numero_fogo}</p>
                        <p className="text-xs text-slate-300">{p.marca} - {p.medida}</p>
                        <span className="inline-block mt-2 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-600 text-white">{p.status}</span>
                      </div>
                      <span className="text-xs font-mono text-slate-400">{brl(p.custo_aquisicao)}</span>
                    </div>
                    <Button size="sm" className="w-full bg-slate-800 hover:bg-slate-700 text-amber-400 border border-amber-500/30" onClick={() => {
                      setPneuChecklist(p); setFormChecklist({ tipo: "RETORNO", avaliacao: "APROVADA", borracheiro: "", obs: "", km: "" }); setChecklistOpen(true);
                    }}>
                      <Wrench className="size-4 mr-2" /> Abrir Checklist de Saída
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {abaAtiva === "estoque" && (
        <div className="space-y-8">
          <div className="glass p-6 rounded-2xl border border-sky-500/20">
            <h3 className="text-lg font-bold text-slate-100 mb-6 flex items-center gap-2">
              <RefreshCw className="size-5 text-sky-400" /> Pneus Disponíveis (Estoque x Envio)
            </h3>
            {stats.emEstoque.length === 0 ? (
              <div className="text-center py-8 text-slate-500">Nenhum pneu em estoque no momento.</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {stats.emEstoque.map((p: any) => (
                  <div key={p.id} className="glass p-4 rounded-xl border border-sky-500/30 hover:scale-[1.02] transition-transform">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm font-bold text-sky-400">{p.numero_fogo}</p>
                        <p className="text-xs text-slate-300">{p.marca} - {p.medida}</p>
                        <p className="text-[10px] text-slate-500 mt-1">DOT: {p.dot || "—"} | Sulco: {p.profundidade_atual || "—"} mm</p>
                      </div>
                      <span className="text-xs font-mono text-amber-400">{brl(p.custo_aquisicao)}</span>
                    </div>
                    <div className="mt-4">
                      <Button size="sm" variant="outline" className="w-full text-xs border-amber-500/40 text-amber-400 hover:bg-amber-500/10" onClick={() => {
                        setPneuChecklist(p); setFormChecklist({ tipo: "RECAPAGEM", avaliacao: "APROVADA", borracheiro: "", obs: "", km: "" }); setChecklistOpen(true);
                      }}>
                        <Wrench className="size-3 mr-2" /> Enviar p/ Manutenção
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="glass p-6 rounded-2xl border border-rose-500/20 bg-rose-950/5">
            <h3 className="text-lg font-bold text-slate-100 mb-6 flex items-center gap-2">
              <Trash2 className="size-5 text-rose-400" /> Histórico de Sucatas
            </h3>
            {pneus.filter((p: any) => p.status === "Sucateado").length === 0 ? (
              <div className="text-center py-8 text-slate-500">Nenhum pneu sucateado.</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {pneus.filter((p: any) => p.status === "Sucateado").map((p: any) => (
                  <div key={p.id} className="glass p-4 rounded-xl border border-rose-500/20 opacity-75">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm font-bold text-rose-400 line-through">{p.numero_fogo}</p>
                        <p className="text-xs text-slate-400">{p.marca} - {p.medida}</p>
                        <p className="text-[10px] text-slate-500 mt-1">Descarte: {parseDate(p.data_descarte) || "—"}</p>
                      </div>
                      <span className="text-xs font-mono text-slate-500">{brl(p.custo_aquisicao)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {abaAtiva === "dashboard" && (
        <div className="space-y-6">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="glass p-4 rounded-xl flex justify-between items-center"><div><p className="text-xs uppercase text-slate-400">Total de Pneus</p><p className="text-2xl font-bold text-slate-100">{dash.total}</p></div><div className="p-2 bg-sky-500/10 rounded-lg"><Disc className="size-5 text-sky-400" /></div></div>
            <div className="glass p-4 rounded-xl flex justify-between items-center"><div><p className="text-xs uppercase text-slate-400">Aplicados</p><p className="text-2xl font-bold text-emerald-400">{dash.aplicados}</p></div><div className="p-2 bg-emerald-500/10 rounded-lg"><CheckCircle2 className="size-5 text-emerald-400" /></div></div>
            <div className="glass p-4 rounded-xl flex justify-between items-center border border-amber-500/30"><div><p className="text-xs uppercase text-amber-500 font-bold">Sulco Crítico (≤3mm)</p><p className="text-2xl font-bold text-amber-400">{dash.sulco_critico}</p></div><div className="p-2 bg-amber-500/10 rounded-lg"><AlertTriangle className="size-5 text-amber-400" /></div></div>
            <div className="glass p-4 rounded-xl flex justify-between items-center"><div><p className="text-xs uppercase text-slate-400">Sucateados</p><p className="text-2xl font-bold text-rose-400">{dash.sucateados}</p></div><div className="p-2 bg-rose-500/10 rounded-lg"><Trash2 className="size-5 text-rose-400" /></div></div>
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="glass p-6 rounded-2xl">
              <h3 className="text-sm font-bold text-slate-100 mb-6 flex items-center gap-2"><BarChart3 className="size-4 text-sky-400" /> Top 5 Marcas na Frota</h3>
              <div className="space-y-4">
                {dash.top_marcas.length === 0 ? (<p className="text-sm text-slate-500">Sem dados.</p>) : (
                  dash.top_marcas.map((m: any, i: number) => {
                    const maxQtd = dash.top_marcas[0].qtd; const pct = (m.qtd / maxQtd) * 100;
                    return (<div key={i}><div className="flex justify-between text-xs mb-1"><span className="text-slate-300 font-medium">{m.marca}</span><span className="text-sky-400 font-bold">{m.qtd} un</span></div><div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden"><div className="h-full bg-sky-500 rounded-full" style={{ width: `${pct}%` }} /></div></div>);
                  })
                )}
              </div>
            </div>
            <div className="glass p-6 rounded-2xl flex flex-col justify-center">
              <h3 className="text-sm font-bold text-slate-100 mb-6 flex items-center gap-2"><Activity className="size-4 text-emerald-400" /> Saúde da Frota</h3>
              <div className="space-y-3">
                 <div className="flex items-center justify-between text-sm"><span className="text-slate-400">Aplicados (Rodando)</span><span className="font-bold text-emerald-400">{dash.aplicados}</span></div>
                 <div className="flex items-center justify-between text-sm"><span className="text-slate-400">Em Estoque / Oficina</span><span className="font-bold text-sky-400">{dash.total - dash.aplicados - dash.sucateados}</span></div>
                 <div className="flex items-center justify-between text-sm border-t border-slate-800 pt-3 mt-3"><span className="text-slate-400">Fora de Operação (Sucata)</span><span className="font-bold text-rose-400">{dash.sucateados}</span></div>
              </div>
            </div>
          </div>
        </div>
      )}

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-4xl p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">{editingId ? "Editar Pneu" : "Novo Pneu"}</h2>
            <div className="grid grid-cols-3 gap-4">
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Marca Fogo *</Label><Input value={form.numero_fogo} onChange={(e) => setForm(s => ({ ...s, numero_fogo: e.target.value }))} placeholder="Ex: FOG-10492" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Equipamento</Label><Input value={form.equipamento} onChange={(e) => setForm(s => ({ ...s, equipamento: e.target.value }))} placeholder="Ex: QPN5139" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Posição</Label><Input value={form.posicao} onChange={(e) => setForm(s => ({ ...s, posicao: e.target.value }))} placeholder="Ex: 1-E" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Tipo</Label><FieldSelect value={form.tipo} onChange={(v) => setForm(s => ({ ...s, tipo: v }))} options={TIPOS_PNEU.map(t => ({ value: t, label: t }))} testId="pneu-tipo" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Marca *</Label><FieldSelect value={form.marca} onChange={(v) => setForm(s => ({ ...s, marca: v }))} options={marcasDb.map((m: any) => ({ value: m.nome, label: m.nome }))} placeholder="Selecione..." testId="pneu-marca" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Modelo</Label><FieldSelect value={form.modelo} onChange={(v) => setForm(s => ({ ...s, modelo: v }))} options={modelosDb.map((m: any) => ({ value: m.nome, label: m.nome }))} placeholder="Selecione..." testId="pneu-modelo" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Tamanho *</Label><FieldSelect value={form.medida} onChange={(v) => setForm(s => ({ ...s, medida: v }))} options={medidasDb.map((m: any) => ({ value: m.medida, label: m.medida }))} placeholder="Selecione..." testId="pneu-medida" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Banda Rod.</Label><Input value={form.banda_rod} onChange={(e) => setForm(s => ({ ...s, banda_rod: e.target.value }))} placeholder="Ex: Original" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Estrutura</Label><Input value={form.estrutura} onChange={(e) => setForm(s => ({ ...s, estrutura: e.target.value }))} placeholder="Ex: Radial" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">N.º Série</Label><Input value={form.n_serie} onChange={(e) => setForm(s => ({ ...s, n_serie: e.target.value }))} placeholder="Ex: 12345" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">DOT</Label><Input value={form.dot} onChange={(e) => setForm(s => ({ ...s, dot: e.target.value }))} placeholder="Ex: 4523" maxLength={4} /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">N.º Recap.</Label><Input value={form.n_recap} onChange={(e) => setForm(s => ({ ...s, n_recap: e.target.value }))} placeholder="Ex: 1" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Data Compra</Label><Input type="date" value={form.data_compra} onChange={(e) => setForm(s => ({ ...s, data_compra: e.target.value }))} /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Data Descarte</Label><Input type="date" value={form.data_descarte} onChange={(e) => setForm(s => ({ ...s, data_descarte: e.target.value }))} /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Status</Label><FieldSelect value={form.status} onChange={(v) => setForm(s => ({ ...s, status: v }))} options={STATUS_PNEU.map(s => ({ value: s, label: s }))} testId="pneu-status" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Custo Total (R$)</Label><Input value={form.custo_total_atual} onChange={(e) => setForm(s => ({ ...s, custo_total_atual: e.target.value }))} placeholder="0,00" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Profundidade (mm)</Label><Input value={form.profundidade_atual} onChange={(e) => setForm(s => ({ ...s, profundidade_atual: e.target.value }))} placeholder="Ex: 8.5" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Uso Atual</Label><Input value={form.uso_atual} onChange={(e) => setForm(s => ({ ...s, uso_atual: e.target.value }))} placeholder="Ex: Rodando" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Custo por KM (R$)</Label><Input value={form.custo_por_km} onChange={(e) => setForm(s => ({ ...s, custo_por_km: e.target.value }))} placeholder="0,00" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">KM na Posição</Label><Input value={form.km_posicao} onChange={(e) => setForm(s => ({ ...s, km_posicao: e.target.value }))} placeholder="Ex: 50000" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Custo Aquisição (R$)</Label><Input value={form.custo_aquisicao} onChange={(e) => setForm(s => ({ ...s, custo_aquisicao: e.target.value }))} placeholder="0,00" /></div>
              <div className="col-span-3 grid gap-1.5"><Label className="text-xs text-slate-400">Observações</Label><Input value={form.observacoes} onChange={(e) => setForm(s => ({ ...s, observacoes: e.target.value }))} placeholder="Ex: Comprado na loja X" /></div>
            </div>
            <div className="flex justify-end gap-3 mt-6"><Button variant="outline" onClick={() => setOpen(false)}>Cancelar</Button><Button onClick={() => salvar.mutate()} disabled={salvar.isPending}>{salvar.isPending ? "Salvando..." : "Salvar"}</Button></div>
          </div>
        </div>
      )}

      {checklistOpen && pneuChecklist && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-1 flex items-center gap-2"><Wrench className="size-5 text-amber-400" /> Checklist Borracheiro</h2>
            <p className="text-sm text-slate-400 mb-4">Pneu Nº Fogo: <strong className="text-amber-400">{pneuChecklist.numero_fogo}</strong></p>
            <div className="space-y-4">
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Ação a ser tomada</Label>
                <select value={formChecklist.tipo} onChange={(e) => setFormChecklist(s => ({ ...s, tipo: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                  {pneuChecklist.status === "Estoque" ? (
                    <><option value="RECAPAGEM">Enviar para Recapagem</option><option value="CONSERTO">Enviar para Conserto</option></>
                  ) : (
                    <><option value="RETORNO">Aprovar e Retornar ao Estoque</option><option value="DESCARTE">Reprovar e Enviar para Sucata</option></>
                  )}
                </select>
              </div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Nome do Borracheiro / Responsável *</Label><Input value={formChecklist.borracheiro} onChange={(e) => setFormChecklist(s => ({ ...s, borracheiro: e.target.value }))} placeholder="Ex: João da Silva" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">KM Atual do Veículo (Opcional)</Label><Input type="number" value={formChecklist.km} onChange={(e) => setFormChecklist(s => ({ ...s, km: e.target.value }))} placeholder="Ex: 150000" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Observações Técnicas</Label><Input value={formChecklist.obs} onChange={(e) => setFormChecklist(s => ({ ...s, obs: e.target.value }))} placeholder="Ex: Furo no ombro, carcaça íntegra." /></div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setChecklistOpen(false)}>Cancelar</Button>
              <Button onClick={() => { 
                if (!formChecklist.borracheiro) return toast.error("Informe o nome do borracheiro.");
                
                let novoStatus = pneuChecklist.status;
                let dadosExtra: any = {};
                
                if (formChecklist.tipo === "RETORNO") novoStatus = "Estoque";
                else if (formChecklist.tipo === "DESCARTE") { novoStatus = "Sucateado"; dadosExtra.data_descarte = new Date().toISOString().split('T')[0]; }
                else if (formChecklist.tipo === "RECAPAGEM") novoStatus = "Recapagem";
                else if (formChecklist.tipo === "CONSERTO") novoStatus = "Conserto";

                movimentar.mutate({ pneu_id: pneuChecklist.id, status: novoStatus, dados: dadosExtra }); 
                setChecklistOpen(false); 
              }} disabled={movimentar.isPending || !formChecklist.borracheiro} className="bg-amber-600 hover:bg-amber-500 text-white">
                Confirmar Checklist
              </Button>
            </div>
          </div>
        </div>
      )}

      {importOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-2">Importando Pneus</h2>
            <p className="text-sm text-slate-400 mb-6">Lendo a planilha e gravando no banco...</p>
            <div className="space-y-4">
              <div className="flex justify-between text-sm"><span className="text-slate-400">Progresso:</span><span className="font-bold text-sky-400">{importProgresso}%</span></div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden"><div className="h-full bg-sky-500 rounded-full transition-all duration-300" style={{ width: `${importProgresso}%` }} /></div>
              <div className="flex justify-between text-sm"><span className="text-slate-400">Processados:</span><span className="font-bold text-slate-200">{importProcessados} de {importTotal}</span></div>
              {importando && (<div className="flex items-center gap-2 text-xs text-sky-400"><Loader2 className="size-4 animate-spin" /> Processando...</div>)}
              {importErros.length > 0 && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg max-h-32 overflow-y-auto"><p className="text-xs font-bold text-red-400 mb-2">Erros encontrados:</p><ul className="list-disc list-inside text-xs text-red-300 space-y-1">{importErros.map((erro, i) => <li key={i}>{erro}</li>)}</ul></div>
              )}
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setImportOpen(false)} disabled={importando}>Fechar</Button>
              {!importando && importProgresso === 100 && (<Button onClick={() => setImportOpen(false)} className="bg-emerald-600 hover:bg-emerald-500">Concluir</Button>)}
            </div>
          </div>
        </div>
      )}

      {excluirId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-sm p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-2">Excluir Pneu?</h2>
            <div className="flex justify-end gap-3 mt-4"><Button variant="outline" onClick={() => setExcluirId(null)}>Cancelar</Button><Button variant="destructive" onClick={() => excluirId && excluir.mutate(excluirId)}>Excluir</Button></div>
          </div>
        </div>
      )}
    </div>
  );
}
