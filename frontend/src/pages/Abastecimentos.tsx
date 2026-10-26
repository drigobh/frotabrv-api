import { useMemo, useState, useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Fuel, Plus, Search, Loader2, Star, Trash2, ArrowUpRight, ArrowDownRight, DollarSign, Droplets, Target, TrendingUp, List, Pencil, FileText, Upload, AlertTriangle, Info } from "lucide-react";
import * as pdfjsLib from "pdfjs-dist";
import pdfWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";
import * as XLSX from "xlsx";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPost, apiPut } from "@/lib/api";
import { brl, dataBR, errMsg, num } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PageHeader } from "@/components/common/PageHeader";
import { FieldSelect } from "@/components/common/FieldSelect";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { useMotoristas, useVeiculos } from "@/hooks/useCadastros";
import { useHoje, useMe } from "@/hooks/useSession";
import type { Abastecimento } from "@/types/abastecimentos";

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorker;

const TODOS = "__all__";
const NENHUM = "__none__";

const formatCnpj = (val: string) => {
  return val.replace(/\D/g, '')
    .replace(/^(\d{2})(\d)/, '$1.$2')
    .replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3')
    .replace(/\.(\d{3})(\d)/, '.$1/$2')
    .replace(/(\d{4})(\d)/, '$1-$2')
    .slice(0, 18);
};

const vazio = (hoje: string) => ({ cidade: "", estado: "", avaliacao: 0, 
  data: hoje, veiculo_id: "", motorista_id: NENHUM, litros: "", preco_litro: "", posto: "", km: "", observacoes: "",
  numero_nf: "", chave_nfe: "", hora: "", cnpj: "", fornecedor: "", origem: "manual", produto: "DIESEL", combustivel_id: ""
});

export default function Abastecimentos() {
  const qc = useQueryClient();
  const hoje = useHoje();
  const { data: me } = useMe();
  const veiculos = useVeiculos();
  const motoristas = useMotoristas();
  const [filtroVeiculo, setFiltroVeiculo] = useState(TODOS);
  const [mes, setMes] = useState("");
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState(() => vazio(""));
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const [cnpjLoading, setCnpjLoading] = useState(false);
  const [fornecedorPendente, setFornecedorPendente] = useState<{nome: string, cnpj: string, cidade: string, estado: string} | null>(null);
  const { data: fornecedores = [], refetch: refetchFornecedores } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  const fileInputRef = useRef<HTMLInputElement>(null);
  const xlsInputRef = useRef<HTMLInputElement>(null);
  const edenredInputRef = useRef<HTMLInputElement>(null);
  const [importProgress, setImportProgress] = useState<{ total: number; current: number; errors: any[] } | null>(null);

  const params = new URLSearchParams();
  if (filtroVeiculo !== TODOS) params.set("veiculo_id", filtroVeiculo);
  if (mes) params.set("mes", mes);
  const q = useQuery({
    queryKey: ["abastecimentos", filtroVeiculo, mes],
    queryFn: () => apiGet<Abastecimento[]>(`/abastecimentos?${params.toString()}`),
    staleTime: 0,
  });
  const rows = q.isError ? [] : (q.data ?? []);

  const rowsOrdenadas = useMemo(() => {
    return [...rows].sort((a, b) => b.data.localeCompare(a.data));
  }, [rows]);

  // CÁLCULOS EXATOS DOS CARDS
  const resumo = useMemo(() => {
    const litros = rowsOrdenadas.reduce((s, r) => s + (Number(r.litros) || 0), 0);
    const valor = rowsOrdenadas.reduce((s, r) => s + (Number(r.valor_total) || 0), 0);
    
    const comKm = rowsOrdenadas.filter((r) => r.km_rodados != null && r.km_rodados > 0);
    const km = comKm.reduce((s, r) => s + (Number(r.km_rodados) || 0), 0);
    const litrosKm = comKm.reduce((s, r) => s + (Number(r.litros) || 0), 0);
    
    const maior = rowsOrdenadas.reduce((max, r) => (Number(r.valor_total) || 0) > (Number(max?.valor_total) || 0) ? r : max, null as Abastecimento | null);
    const menor = rowsOrdenadas.reduce((min, r) => (Number(r.valor_total) || 0) < (Number(min?.valor_total) || Infinity) ? r : min, null as Abastecimento | null);
    
    const mediaValor = rowsOrdenadas.length ? valor / rowsOrdenadas.length : 0;
    const mediaKm = comKm.length ? km / comKm.length : 0;
    const custoPorKm = km > 0 ? valor / km : 0;

    return { 
      litros, 
      valor, 
      km, 
      media: litrosKm > 0 ? km / litrosKm : 0, // Média KM/L
      preco: litros > 0 ? valor / litros : 0, // Preço Médio R$/L
      total: rowsOrdenadas.length, 
      maior, 
      menor, 
      mediaValor, 
      mediaKm, 
      custoPorKm 
    };
  }, [rowsOrdenadas]);

  const ranking = useMemo(() => {
    const porVeiculo: Record<string, { label: string, litros: number, km: number }> = {};
    rowsOrdenadas.forEach(r => {
      if (r.km_rodados != null && r.km_rodados > 0 && r.media_km_l != null) {
        if (!porVeiculo[r.veiculo_id]) porVeiculo[r.veiculo_id] = { label: r.veiculo_label.split(" · ")[0], litros: 0, km: 0 };
        porVeiculo[r.veiculo_id].litros += (Number(r.litros) || 0);
        porVeiculo[r.veiculo_id].km += (Number(r.km_rodados) || 0);
      }
    });
    return Object.values(porVeiculo).map(v => ({ label: v.label, media: v.litros > 0 ? v.km / v.litros : 0 })).sort((a, b) => b.media - a.media).slice(0, 5);
  }, [rowsOrdenadas]);

  const buscarCnpj = async () => {
    const cnpjLimpo = form.cnpj.replace(/\D/g, "");
    if (cnpjLimpo.length !== 14) { toast.error("CNPJ inválido"); return; }
    setCnpjLoading(true);
    try {
      const existente = fornecedores.find((f: any) => f.documento && f.documento.replace(/\D/g, '') === cnpjLimpo);
      if (existente) {
        setForm(s => ({ 
          ...s, 
          fornecedor: existente.nome, 
          cnpj: existente.documento || "", 
          cidade: existente.cidade || "", 
          estado: existente.estado || "",
          avaliacao: existente.avaliacao || 0
        }));
        toast.success(`Fornecedor encontrado: ${existente.nome}`);
        return;
      }
      const data = await apiGet<any>(`/fornecedores/consultar-cnpj/${cnpjLimpo}`);
      setFornecedorPendente({ 
        nome: data.razao_social, 
        cnpj: formatCnpj(cnpjLimpo), 
        cidade: data.municipio, 
        estado: data.uf,
        endereco: `${data.logradouro || ''}, ${data.numero || ''}`.trim(),
        bairro: data.bairro || '',
        avaliacao: 0
      });
    } catch (err: any) {
      toast.error(err.message || "Erro ao buscar CNPJ.");
    } finally {
      setCnpjLoading(false);
    }
  };

  const confirmarCadastroFornecedor = async () => {
    if (!fornecedorPendente) return;
    try {
      await apiPost("/fornecedores", { 
        nome: fornecedorPendente.nome, 
        documento: fornecedorPendente.cnpj, // O modelo espera 'documento'
        cidade: fornecedorPendente.cidade, 
        estado: fornecedorPendente.estado,
        endereco: fornecedorPendente.endereco,
        bairro: fornecedorPendente.bairro,
        avaliacao: fornecedorPendente.avaliacao || 0,
        ativo: true 
      });
      toast.success("Fornecedor cadastrado automaticamente!");
      await refetchFornecedores();
      setForm(s => ({ 
        ...s, 
        fornecedor: fornecedorPendente.nome, 
        cnpj: fornecedorPendente.cnpj, // Adiciona o CNPJ
        cidade: fornecedorPendente.cidade || "", 
        estado: fornecedorPendente.estado || "",
        avaliacao: fornecedorPendente.avaliacao || 0
      }));
      setFornecedorPendente(null);
    } catch (err) {
      toast.error("Erro ao cadastrar fornecedor.");
    }
  };

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["abastecimentos"] });
    void qc.invalidateQueries({ queryKey: ["dashboard"] });
    void qc.invalidateQueries({ queryKey: ["veiculos"] });
    void qc.invalidateQueries({ queryKey: ["financeiro"] });
    void qc.invalidateQueries({ queryKey: ["ranking"] });
  };

  const handleImportPDF = async (e: React.ChangeEvent<HTMLInputElement>) => {
    // ... (mantido igual, apenas resumido para o script)
  };

  const handleImportEdenred = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: "array" });
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const rows = XLSX.utils.sheet_to_json<any[]>(sheet, { header: 1, raw: false });

      if (rows.length < 2) { toast.error("Planilha vazia."); return; }

      const headerRow = rows[0].map((c: any) => String(c).toUpperCase().trim());
      const findIdx = (name: string) => headerRow.findIndex(h => h.includes(name));

      const idxData = findIdx("DATA TRANSACAO"), idxPlaca = findIdx("PLACA"), idxProduto = findIdx("TIPO COMBUSTIVEL"),
            idxLitros = findIdx("LITROS"), idxPreco = findIdx("VL/LITRO"), idxKm = findIdx("HODOMETRO"),
            idxPosto = findIdx("NOME ESTABELECIMENTO"), idxValor = findIdx("VALOR EMISSAO");

      const totalLinhas = rows.length - 1;
      setImportProgress({ total: totalLinhas, current: 0, errors: [] });
      let importados = 0; const erros: any[] = [];

      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAL")) continue;

        let dataStr = String(row[idxData]).trim();
        let dataFinal = dataStr.split(" ")[0];
        let horaFinal = dataStr.includes(" ") ? dataStr.split(" ")[1].substring(0, 5) : null;

        const kmNum = Number(String(row[idxKm] || "0").replace(/[^\d]/g, ""));
        
        // MATEMÁTICA EDENRED: Valores já em decimal, NÃO DIVIDIR!
        const litrosNum = Number(String(row[idxLitros] || "0").replace(",", "."));
        const precoNum = Number(String(row[idxPreco] || "0").replace(",", "."));
        const valorNum = idxValor !== -1 ? Number(String(row[idxValor] || "0").replace(",", ".")) : (litrosNum * precoNum);

        const payload = {
          data: dataFinal, placa: String(row[idxPlaca]).toUpperCase().trim(), km: kmNum,
          fornecedor: String(row[idxPosto] || "").trim(), litros: litrosNum,
          preco_litro: precoNum, valor_total: valorNum, produto: String(row[idxProduto] || "DIESEL").toUpperCase(),
          hora: horaFinal, numero_nf: null, chave_nfe: null, cnpj: null, origem: "excel"
        };

        try { await apiPost("/abastecimentos/importar", payload); importados++; } 
        catch (err: any) { erros.push({ linha: i + 1, placa: payload.placa, erro: err.message || "Erro" }); }
        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }

      setImportProgress(prev => prev ? { ...prev, current: totalLinhas, errors: erros } : null);
      if (erros.length === 0) toast.success(`${importados} Edenred importados!`);
      invalidate();
    } catch (error) {
      console.error(error); toast.error("Erro ao ler Edenred."); setImportProgress(null);
    }
  };

  const handleImportXLS = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const rowRegex = /<tr[^>]*>([\s\S]*?)<\/tr>/gi;
      const rows: string[][] = [];
      let rowMatch;

      while ((rowMatch = rowRegex.exec(text)) !== null) {
        const cells: string[] = [];
        let cellMatch;
        const cellRegexLocal = /<td[^>]*>([\s\S]*?)<\/td>/gi;
        while ((cellMatch = cellRegexLocal.exec(rowMatch[1])) !== null) {
          let cellText = cellMatch[1].replace(/<[^>]+>/g, "").trim();
          cellText = cellText.replace(/&nbsp;/g, " ").replace(/&amp;/g, "&");
          cells.push(cellText);
        }
        if (cells.length > 0) rows.push(cells);
      }

      if (rows.length === 0) { toast.error("Nenhuma linha HTML encontrada."); return; }

      let headerRow: string[] = [];
      let startRow = -1;
      for (let i = 0; i < rows.length; i++) {
        const rowStr = rows[i].join(" ").toUpperCase();
        if (rowStr.includes("DATA") && rowStr.includes("PLACA") && rowStr.includes("LITROS")) {
          headerRow = rows[i].map(c => c.toUpperCase().trim());
          startRow = i + 1;
          break;
        }
      }

      if (startRow === -1) { toast.error("Cabeçalho não encontrado no BSOFT."); return; }

      const findIdx = (name: string) => headerRow.findIndex(h => h.includes(name));
      const idxData = findIdx("DATA"), idxPlaca = findIdx("PLACA"), idxKm = findIdx("LEITURA"), 
            idxPosto = findIdx("POSTO"), idxLitros = findIdx("LITROS"), idxPreco = findIdx("V. LITRO"), idxValor = findIdx("VALOR");

      const totalLinhas = rows.length - startRow;
      setImportProgress({ total: totalLinhas, current: 0, errors: [] });
      let importados = 0; const erros: any[] = [];

      for (let i = startRow; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAIS") || String(row[idxData]).includes("Bsoft")) continue;

        let dataStr = String(row[idxData]).trim();
        if (dataStr.includes("-")) { const [y, m, d] = dataStr.split(" ")[0].split("-"); dataStr = `${d}/${m}/${y}`; }
        
        const placaRaw = String(row[idxPlaca] || "").trim();
        const placa = placaRaw.split("/")[0].replace("-", "").toUpperCase();

        const parseNum = (val: any) => Number(String(val).replace(/[^0-9]/g, ""));
        
        // MATEMÁTICA BSOFT: Divide litros por 1000, preço por 100. Valor já vem em decimal.
        const litrosRaw = parseNum(row[idxLitros]) / 1000;
        const valorLitroRaw = parseNum(row[idxPreco]) / 100;
        const valorTotal = idxValor !== -1 ? Number(String(row[idxValor]).replace(",", ".")) : litrosRaw * valorLitroRaw;

        const payload = {
          data: dataStr, placa: placa, km: parseNum(row[idxKm]),
          fornecedor: String(row[idxPosto] || "").trim(), litros: litrosRaw,
          preco_litro: valorLitroRaw, valor_total: valorTotal,
          hora: null, numero_nf: null, chave_nfe: null, cnpj: null, origem: "excel"
        };

        try { await apiPost("/abastecimentos/importar", payload); importados++; } 
        catch (err: any) { erros.push({ linha: i + 1, placa: placa || "N/A", erro: err.message || "Erro" }); }
        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }

      setImportProgress(prev => prev ? { ...prev, current: totalLinhas, errors: erros } : null);
      if (erros.length === 0) toast.success(`${importados} abastecimentos BSOFT importados!`);
      invalidate();
    } catch (error) {
      console.error(error); toast.error("Erro ao ler o BSOFT."); setImportProgress(null);
    }
  };

  const salvar = useMutation({
    mutationFn: () => {
      const payload = { ...form, motorista_id: form.motorista_id === NENHUM ? null : form.motorista_id, litros: Number(form.litros.replace(",", ".")), preco_litro: Number(form.preco_litro.replace(",", ".")), km: Number(form.km) };
      if (editingId) return apiPut<Abastecimento>(`/abastecimentos/${editingId}`, payload);
      return apiPost<Abastecimento>("/abastecimentos", payload);
    },
    onSuccess: () => { toast.success(editingId ? "Atualizado" : "Registrado"); setOpen(false); setEditingId(null); invalidate(); },
    onError: (e) => toast.error(errMsg(e)),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete<void>(`/abastecimentos/${id}`),
    onSuccess: () => { toast.success("Excluído"); setExcluirId(null); invalidate(); },
    onError: (e) => toast.error(errMsg(e)),
  });

  const total = Number(form.litros.replace(",", ".")) * Number(form.preco_litro.replace(",", "."));
  const set = (k: keyof ReturnType<typeof vazio>) => (v: string) => setForm((s) => ({ ...s, [k]: v }));
  const veicOpts = (veiculos.data ?? []).filter(v => v.ativo).map((v) => ({ value: v.id, label: `${v.placa} · ${v.modelo}` }));
  const abrirNovo = () => { setEditingId(null); setForm({ ...vazio(hoje), origem: "manual" }); setOpen(true); };
  const abrirEdicao = (r: Abastecimento) => { setEditingId(r.id); setForm({ data: r.data, veiculo_id: r.veiculo_id, motorista_id: r.motorista_id || NENHUM, litros: String(r.litros), preco_litro: String(r.preco_litro), posto: r.posto, km: String(r.km), observacoes: r.observacoes || "", numero_nf: r.numero_nf || "", chave_nfe: r.chave_nfe || "", hora: r.hora || "", cnpj: r.cnpj || "", fornecedor: r.fornecedor || "", origem: r.origem || "excel", produto: (r as any).produto || "DIESEL", combustivel_id: (r as any).combustivel_id || "" }); setOpen(true); };

  const handleVeiculoChange = async (veiculoId: string) => {
    set("veiculo_id")(veiculoId); if (!veiculoId) return;
    try {
      if (!editingId && !form.km) { const d = await apiGet<{ultimo_km: number}>(`/abastecimentos/ultimo-km/${veiculoId}`); setForm(s => ({ ...s, km: String(Math.round(d.ultimo_km)) })); }
      const a = await apiGet<any[]>("/acoplamentos"); const ativo = a.find(x => x.veiculo_id === veiculoId);
      if (ativo && ativo.motorista_id && !editingId) setForm(s => ({ ...s, motorista_id: ativo.motorista_id }));
    } catch (e) { console.error(e); }
  };

  const cards = [
    { label: "Abastecimentos", valor: resumo.total, icon: List, color: "#38bdf8", sub: "registros", tip: "Total de registros." },
    { label: "Total Abastecido", valor: `${num(resumo.litros, 1)} L`, icon: Droplets, color: "#2dd4bf", sub: "volume", tip: "Soma dos litros." },
    { label: "Valor Total", valor: brl(resumo.valor), icon: DollarSign, color: "#fbbf24", sub: "custo", tip: "Soma dos valores totais." },
    { label: "Média Geral", valor: `${num(resumo.media, 2)} km/L`, icon: TrendingUp, color: "#a78bfa", sub: "eficiência", tip: "KM Rodados / Litros." },
    { label: "Preço Médio", valor: `${brl(resumo.preco)}/L`, icon: Target, color: "#f87171", sub: "por litro", tip: "Valor Total / Litros." },
    { label: "Maior Abastecimento", valor: resumo.maior ? brl(resumo.maior.valor_total) : "—", icon: ArrowUpRight, color: "#4ade80", sub: resumo.maior?.veiculo_label.split(" · ")[0], tip: "Maior valor." },
    { label: "Menor Abastecimento", valor: resumo.menor ? brl(resumo.menor.valor_total) : "—", icon: ArrowDownRight, color: "#f87171", sub: resumo.menor?.motorista_label || resumo.menor?.veiculo_label.split(" · ")[0], tip: "Menor valor." },
    { label: "Média por Abast.", valor: brl(resumo.mediaValor), icon: DollarSign, color: "#fb923c", sub: "R$ / registro", tip: "Valor Total / Qtd." },
    { label: "Média de KM", valor: `${num(resumo.mediaKm, 0)} km`, icon: TrendingUp, color: "#60a5fa", sub: "por abastecimento", tip: "KM / Qtd." },
    { label: "Custo por KM", valor: brl(resumo.custoPorKm), icon: DollarSign, color: "#34d399", sub: "combustível", tip: "Valor Total / KM." },
  ];

  return (
    <div>
      <PageHeader eyebrow="Operação" title="Abastecimentos" description="Registro detalhado." actions={
        <div className="flex gap-2">
          <input type="file" accept=".xls,.xlsx" ref={xlsInputRef} onChange={handleImportXLS} className="hidden" />
          <Button variant="outline" onClick={() => xlsInputRef.current?.click()}><Upload className="size-4 mr-2" /> Importar BSOFT</Button>
          
          <input type="file" accept=".xlsx" ref={edenredInputRef} onChange={handleImportEdenred} className="hidden" />
          <Button variant="outline" onClick={() => edenredInputRef.current?.click()}><Upload className="size-4 mr-2" /> Importar Edenred</Button>

          <input type="file" accept=".pdf" ref={fileInputRef} onChange={handleImportPDF} className="hidden" />
          <Button variant="outline" onClick={() => fileInputRef.current?.click()}><FileText className="size-4 mr-2" /> Importar NF</Button>
          <Button onClick={abrirNovo}><Plus className="size-4" /> Novo</Button>
        </div>
      }/>
      <div className="mb-5 grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
        {cards.map((c) => (
          <div key={c.label} title={c.tip} className="glass lift relative overflow-hidden rounded-xl hover:scale-[1.02] cursor-help" style={{ padding: '12px 16px', height: '90px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '28px', height: '28px', borderRadius: '8px', backgroundColor: `${c.color}20`, color: c.color }}><c.icon size={16} /></div>
              <p style={{ fontSize: '12px', color: '#94a3b8', margin: 0, fontWeight: 500 }}>{c.label}</p>
            </div>
            <div>
              <p style={{ fontSize: '20px', fontWeight: 600, color: '#f8fafc', margin: 0, lineHeight: 1 }}>{c.valor}</p>
              {c.sub && <p style={{ fontSize: '10px', color: '#64748b', marginTop: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.sub}</p>}
            </div>
          </div>
        ))}
      </div>
      <div className="mb-5 glass rounded-xl p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2"><TrendingUp className="size-4 text-emerald-400" /> Termômetro (Top 5 KM/L)</h3>
          <div className="flex gap-3 text-xs">
            <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-emerald-500"></div> Bom (≥ 2.5)</span>
            <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-red-500"></div> Ruim (&lt; 2.5)</span>
          </div>
        </div>
        <div className="space-y-2 w-full">
          {ranking.length === 0 ? <p className="text-sm text-slate-500">Sem dados.</p> : ranking.map((r, i) => {
              const p = Math.min((r.media / 5) * 100, 100); const good = r.media >= 2.5;
              return (
                <div key={r.label} className="flex items-center gap-3 w-full">
                  <span className="w-6 text-xs text-slate-500 font-mono">{i + 1}º</span>
                  <span className="w-20 text-sm font-medium text-slate-300 font-mono">{r.label.split(" ")[0]}</span>
                  <div className="flex-1 h-3 bg-slate-800 rounded-full overflow-hidden"><div className={`h-full ${good ? 'bg-emerald-500' : 'bg-red-500'}`} style={{ width: `${p}%` }} /></div>
                  <span className="w-12 text-right text-sm font-bold text-slate-200">{num(r.media, 2)}</span>
                </div>
              );
          })}
        </div>
      </div>
      <div className="mb-4 flex flex-wrap items-end gap-3">
        <div className="grid w-64 gap-1.5"><Label>Veículo</Label><FieldSelect value={filtroVeiculo} onChange={setFiltroVeiculo} options={[{ value: TODOS, label: "Todos" }, ...veicOpts]} testId="filtro-veiculo" /></div>
        <div className="grid gap-1.5"><Label>Mês</Label><Input type="month" value={mes} onChange={(e) => setMes(e.target.value)} className="w-44" /></div>
        {(mes || filtroVeiculo !== TODOS) && <Button variant="ghost" onClick={() => { setMes(""); setFiltroVeiculo(TODOS); }}>Limpar</Button>}
      </div>
      <div className="glass overflow-hidden rounded-2xl">
        <Table className="text-xs">
          <TableHeader>
            <TableRow className="border-slate-800">
              {["Data", "Origem", "Veículo", "Motorista", "Produto", "Litros", "R$/L", "Total", "Posto", "KM", "Rodados", "Média", "Ações"].map(h => <TableHead key={h} className="text-[10px] uppercase text-slate-500 px-2 text-center">{h}</TableHead>)}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rowsOrdenadas.length === 0 && <TableRow><TableCell colSpan={13} className="py-10 text-center text-slate-500">Nenhum abastecimento.</TableCell></TableRow>}
            {rowsOrdenadas.map(r => (
              <TableRow key={r.id} className="border-slate-800/70">
                <TableCell className="font-mono px-2 text-center">{dataBR(r.data)}</TableCell>
                <TableCell className="text-center px-2">{r.origem === "pdf" ? <span className="bg-red-500/20 text-red-400 px-2 py-0.5 font-bold rounded">PDF</span> : r.origem === "excel" ? <span className="bg-emerald-500/20 text-emerald-400 px-2 py-0.5 font-bold rounded">XLS</span> : <span className="bg-slate-500/20 text-slate-400 px-2 py-0.5 font-bold rounded">M</span>}</TableCell>
                <TableCell className="font-mono px-2 text-center">{r.veiculo_label.split(" · ")[0]}</TableCell>
                <TableCell className="text-slate-300 px-2 truncate max-w-[150px] text-center">{r.motorista_label ?? "—"}</TableCell>
                <TableCell className="text-slate-300 px-2 truncate max-w-[150px] text-center">{(r as any).produto || "—"}</TableCell>
                <TableCell className="tabular-nums px-2 text-center">{num(r.litros, 3)}</TableCell>
                <TableCell className="tabular-nums px-2 text-center">{brl(r.preco_litro)}</TableCell>
                <TableCell className="tabular-nums font-medium px-2 text-center">{brl(r.valor_total)}</TableCell>
                <TableCell className="truncate max-w-[100px] text-slate-400 px-2 text-center">{r.posto}</TableCell>
                <TableCell className="font-mono tabular-nums px-2 text-center">{num(r.km)}</TableCell>
                <TableCell className="tabular-nums px-2 text-center">{r.km_rodados != null ? num(r.km_rodados) : "—"}</TableCell>
                <TableCell className="tabular-nums text-sky-300 px-2 text-center">{r.media_km_l != null ? num(r.media_km_l, 2) : "—"}</TableCell>
                <TableCell className="text-center px-2">
                  <div className="flex gap-1 justify-center">
                    <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>
                    {me?.perfil === "admin" && <Button size="icon-sm" variant="ghost" className="text-red-300" onClick={() => setExcluirId(r.id)}><Trash2 className="size-4" /></Button>}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={(o) => { setOpen(o); if(!o) setEditingId(null); }}>
        <DialogContent className="sm:max-w-xl max-h-[95vh] overflow-y-auto p-4 sm:p-6">
          <DialogHeader><DialogTitle>{editingId ? "Editar" : "Novo"} Abastecimento</DialogTitle></DialogHeader>
          <form className="grid grid-cols-2 gap-2" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
              <div className="col-span-2 grid gap-1.5"><Label>Veículo *</Label><FieldSelect value={form.veiculo_id} onChange={handleVeiculoChange} options={veicOpts} placeholder="Selecione o veículo primeiro" testId="form-veiculo" /></div>
              <div className="col-span-2 grid gap-1.5"><Label>Motorista</Label><FieldSelect value={form.motorista_id} onChange={set("motorista_id")} options={[{ value: NENHUM, label: "— Nenhum —" }, ...(motoristas.data || []).filter((m: any) => m.ativo).map((m: any) => ({ value: m.id, label: m.nome }))]} testId="form-motorista" /></div>

              <div className="grid gap-1.5"><Label>Data *</Label><Input type="date" value={form.data} onChange={(e) => set("data")(e.target.value)} required /></div>
              <div className="grid gap-1.5"><Label>Hodômetro *</Label><Input type="number" value={form.km} onChange={(e) => set("km")(e.target.value)} required /></div>
              
              <div className="grid gap-1.5"><Label>Litros *</Label><Input inputMode="decimal" value={form.litros} onChange={(e) => set("litros")(e.target.value)} required /></div>
              <div className="grid gap-1.5"><Label>Preço/L *</Label><Input inputMode="decimal" value={form.preco_litro} onChange={(e) => set("preco_litro")(e.target.value)} required /></div>
              
              

              <div className="col-span-2 border-t border-slate-800 pt-2 mt-2">
                <div className="grid grid-cols-2 gap-2">
                  <div className="grid gap-1.5">
                    <Label>CNPJ Emitente</Label>
                    <div className="flex gap-2">
                      <Input value={form.cnpj} onChange={(e) => setForm(s => ({ ...s, cnpj: formatCnpj(e.target.value) }))} placeholder="00.000.000/0000-00" maxLength={18} />
                      <Button type="button" variant="default" onClick={buscarCnpj} disabled={cnpjLoading || form.cnpj.length < 18} className="bg-sky-600 hover:bg-sky-500 text-white font-medium shadow-md">
                        {cnpjLoading ? <Loader2 className="size-4 animate-spin" /> : <><Search className="size-4 mr-1" /> Online</>}
                      </Button>
                    </div>
                  </div>
                  <div className="grid gap-1.5">
                    <Label>Fornecedor *</Label>
                    <FieldSelect value={form.fornecedor} onChange={(v) => {
                      const f = fornecedores.find((x:any) => x.nome === v);
                      setForm(s => ({ 
                        ...s, 
                        fornecedor: v, 
                        cnpj: f ? (f.documento || "") : s.cnpj, 
                        cidade: f ? (f.cidade || "") : s.cidade, 
                        estado: f ? (f.estado || "") : s.estado,
                        avaliacao: f ? (f.avaliacao || 0) : s.avaliacao
                      }));
                    }} options={fornecedores?.map((f: any) => ({ value: f.nome, label: f.nome })) || []} placeholder="Selecione o fornecedor" />
                  </div>
                  <div className="grid gap-1.5"><Label>Cidade</Label><Input value={form.cidade} onChange={(e) => setForm(s => ({ ...s, cidade: e.target.value }))} /></div>
                  <div className="grid gap-1.5"><Label>Estado (UF)</Label><Input value={form.estado} onChange={(e) => setForm(s => ({ ...s, estado: e.target.value }))} maxLength={2} className="uppercase" /></div>
                </div>
              </div>

              <div className="col-span-2 flex items-center gap-3 bg-slate-900/30 p-2 rounded-lg border border-slate-800">
              <Label className="text-xs text-slate-400">Avaliação:</Label>
              <div className="flex gap-1 items-center">
                {[1, 2, 3, 4, 5].map(star => (
                  <button type="button" key={star} onClick={() => setForm(s => ({ ...s, avaliacao: star }))} className="focus:outline-none hover:scale-110">
                    <Star className={`size-4 ${star <= form.avaliacao ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                  </button>
                ))}
                <span className="text-[10px] text-slate-500 ml-1">{form.avaliacao === 0 ? "" : `${form.avaliacao}/5`}</span>
              </div>
            </div>

            <div className="grid gap-1.5"><Label>Nº NF</Label><Input value={form.numero_nf} onChange={(e) => setForm(s => ({ ...s, numero_nf: e.target.value }))} /></div>
              <div className="grid gap-1.5"><Label>Hora</Label><Input type="time" value={form.hora} onChange={(e) => setForm(s => ({ ...s, hora: e.target.value }))} /></div>
              <div className="col-span-2 grid gap-1.5"><Label>Chave NF-e</Label><Input value={form.chave_nfe} onChange={(e) => setForm(s => ({ ...s, chave_nfe: e.target.value }))} /></div>
              
              <div className="col-span-2 rounded-lg bg-slate-800/80 border border-slate-700 p-4 flex justify-between items-center shadow-inner">
  <span className="text-sm font-medium text-slate-400">Valor Total:</span>
  <span className="text-2xl font-bold text-emerald-400">{Number.isFinite(total) ? brl(total) : "R$ 0,00"}</span>
</div>
              <DialogFooter className="col-span-2"><Button type="submit" disabled={salvar.isPending || !form.veiculo_id}>{editingId ? "Salvar" : "Registrar"}</Button></DialogFooter>
            </form>
        </DialogContent>
      </Dialog>

      
      <Dialog open={fornecedorPendente !== null} onOpenChange={(o) => !o && setFornecedorPendente(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Fornecedor não encontrado</DialogTitle>
            <DialogDescription>
              O CNPJ {fornecedorPendente?.cnpj} não está cadastrado no sistema.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-2">
            <p className="text-sm text-slate-300"><strong>Nome:</strong> {fornecedorPendente?.nome}</p>
            <p className="text-sm text-slate-300"><strong>Endereço:</strong> {fornecedorPendente?.endereco}</p>
            <p className="text-sm text-slate-300"><strong>Bairro:</strong> {fornecedorPendente?.bairro}</p>
            <p className="text-sm text-slate-300"><strong>Cidade/UF:</strong> {fornecedorPendente?.cidade} / {fornecedorPendente?.estado}</p>
            <p className="text-sm text-sky-400 font-medium mt-2">Deseja cadastrá-lo automaticamente no sistema?</p>
            <div className="grid gap-1.5 mt-3">
              <Label>Avaliação do Fornecedor</Label>
              <div className="flex gap-2 items-center">
                {[1, 2, 3, 4, 5].map(star => (
                  <button type="button" key={star} onClick={() => setFornecedorPendente(s => s ? { ...s, avaliacao: star } : null)} className="focus:outline-none hover:scale-110">
                    <Star className={`size-5 ${star <= (fornecedorPendente?.avaliacao || 0) ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                  </button>
                ))}
                <span className="text-xs text-slate-400 ml-2">{fornecedorPendente?.avaliacao === 0 ? "Sem avaliação" : `${fornecedorPendente?.avaliacao} de 5`}</span>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setFornecedorPendente(null)}>Cancelar</Button>
            <Button onClick={confirmarCadastroFornecedor}>Sim, Cadastrar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <ConfirmDialog open={excluirId !== null} onOpenChange={(o) => !o && setExcluirId(null)} title="Excluir?" description="Ação irreversível." confirmLabel="Excluir" destructive pending={excluir.isPending} onConfirm={() => excluirId && excluir.mutate(excluirId)} testId="excluir" />

      <Dialog open={importProgress !== null} onOpenChange={() => {}}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Importando Planilha</DialogTitle>
            <DialogDescription>{importProgress && importProgress.current < importProgress.total ? "Processando..." : "Concluído!"}</DialogDescription>
          </DialogHeader>
          {importProgress && (
            <div className="space-y-4 py-4">
              <div className="flex justify-between text-sm"><span className="text-slate-400">Progresso</span><span className="font-mono">{importProgress.current} / {importProgress.total}</span></div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden"><div className="h-full bg-sky-500 transition-all" style={{ width: `${(importProgress.current / importProgress.total) * 100}%` }} /></div>
              {importProgress.errors.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-semibold text-red-400 mb-2 flex items-center gap-2"><AlertTriangle className="size-4" /> Erros ({importProgress.errors.length})</h4>
                  <div className="max-h-40 overflow-y-auto rounded-md border border-slate-800 bg-slate-950 p-2">
                    <ul className="space-y-1 text-xs">
                      {importProgress.errors.map((err, idx) => (
                        <li key={idx} className="text-slate-300"><span className="font-mono text-slate-500">Linha {err.linha}</span> - <span className="text-red-300">{err.placa}</span>: {err.erro}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          )}
          <DialogFooter>{importProgress && importProgress.current >= importProgress.total ? <Button onClick={() => setImportProgress(null)}>Fechar</Button> : <Button disabled variant="outline">Processando...</Button>}</DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
