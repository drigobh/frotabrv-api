import { useMemo, useState, useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Fuel, Plus, Trash2, ArrowUpRight, ArrowDownRight, DollarSign, Droplets, Target, TrendingUp, List, Pencil, FileText, Upload, AlertTriangle } from "lucide-react";
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
import { useQuery as useQueryComb } from "@tanstack/react-query";
import { useHoje, useMe } from "@/hooks/useSession";
import type { Abastecimento } from "@/types/abastecimentos";

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorker;

const TODOS = "__all__";
const NENHUM = "__none__";

const vazio = (hoje: string) => ({ 
  data: hoje, veiculo_id: "", motorista_id: NENHUM, litros: "", preco_litro: "", posto: "", km: "", observacoes: "",
  numero_nf: "", chave_nfe: "", hora: "", cnpj: "", fornecedor: "", origem: "excel"
});

export default function Abastecimentos() {
  const qc = useQueryClient();
  const hoje = useHoje();
  const { data: me } = useMe();
  const veiculos = useVeiculos();
  const motoristas = useMotoristas();
  const combQ = useQueryComb({ queryKey: ["combustiveis"], queryFn: () => apiGet<any[]>("/combustiveis") });
  const combOpts = (combQ.data ?? []).filter(c => c.ativo).map(c => ({ value: c.id, label: c.nome }));
  const [filtroVeiculo, setFiltroVeiculo] = useState(TODOS);
  const [mes, setMes] = useState("");
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState(() => vazio(""));
  const [excluirId, setExcluirId] = useState<string | null>(null);
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
  });
  const rows = q.isError ? [] : (q.data ?? []);

  // 1. Ordena os dados por data (mais recente primeiro)
  const rowsOrdenadas = useMemo(() => {
    return [...rows].sort((a, b) => b.data.localeCompare(a.data));
  }, [rows]);

  // 2. Calcula o Resumo com os valores EXATOS
  const resumo = useMemo(() => {
    const litros = rowsOrdenadas.reduce((s, r) => s + r.litros, 0);
    const valor = rowsOrdenadas.reduce((s, r) => s + r.valor_total, 0);
    
    const comKm = rowsOrdenadas.filter((r) => r.km_rodados != null);
    const km = comKm.reduce((s, r) => s + (r.km_rodados ?? 0), 0);
    const litrosKm = comKm.reduce((s, r) => s + r.litros, 0);
    
    const maior = rowsOrdenadas.reduce((max, r) => r.valor_total > (max?.valor_total || 0) ? r : max, null as Abastecimento | null);
    const menor = rowsOrdenadas.reduce((min, r) => r.valor_total < (min?.valor_total || Infinity) ? r : min, null as Abastecimento | null);
    
    const mediaValor = rowsOrdenadas.length ? valor / rowsOrdenadas.length : 0;
    const mediaKm = comKm.length ? km / comKm.length : 0;
    const custoPorKm = km > 0 ? valor / km : 0;

    return { 
      litros, 
      valor, 
      km, 
      media: litrosKm > 0 ? km / litrosKm : 0, // Média Geral (KM/L) 
      preco: litros > 0 ? valor / litros : 0, // Preço Médio (R$/L)
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
      if (r.km_rodados != null) {
        if (!porVeiculo[r.veiculo_id]) porVeiculo[r.veiculo_id] = { label: r.veiculo_label.split(" · ")[0], litros: 0, km: 0 };
        porVeiculo[r.veiculo_id].litros += r.litros;
        porVeiculo[r.veiculo_id].km += r.km_rodados;
      }
    });
    return Object.values(porVeiculo).map(v => ({ label: v.label, media: v.litros > 0 ? v.km / v.litros : 0 })).sort((a, b) => b.media - a.media).slice(0, 5);
  }, [rowsOrdenadas]);

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["abastecimentos"] });
    void qc.invalidateQueries({ queryKey: ["dashboard"] });
    void qc.invalidateQueries({ queryKey: ["veiculos"] });
    void qc.invalidateQueries({ queryKey: ["financeiro"] });
    void qc.invalidateQueries({ queryKey: ["ranking"] });
  };

  const handleImportPDF = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      let text = "";

      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const content = await page.getTextContent();
        text += content.items.map((item: any) => item.str).join(" ") + "\n";
      }

      // 1. Extração da Placa
      const placaMatch = text.match(/PLACA[:\s]*([A-Z]{3}[0-9][A-Z0-9][0-9]{2})/i) || text.match(/PLACA[:\s]*([A-Z0-9]{7})/i);
      
      // 2. Extração do KM (Lida como número inteiro, ignorando pontos)
      const kmMatch = text.match(/KM[:\s]*([\d.,]+)/i);
      const kmNum = kmMatch ? Number(String(kmMatch[1]).replace(/\D/g, "")) : 0;

      // 3. Extração de Litros e Preço
      const litrosMatch = text.match(/L\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)/i) || text.match(/L\s+([\d.,]+)\s+([\d.,]+)/i);
      
      // 4. Extração do Posto (Emitente)
      const postoMatch = text.match(/RECEBEMOS DE\s+([^,]+)/i);
      
      // 5. Extração do Produto
      const produtoMatch = text.match(/(OLEO DIESEL[^\d]*|DIESEL[^\d]*|ARLA[^\d]*)/i);

      // 6. Extração da Data de Emissão
      const dateMatch = text.match(/DATA DA EMISSÃO\s*(\d{2}\/\d{2}\/\d{4})/i);
      let dataStr = new Date().toISOString().split('T')[0]; // Fallback para hoje
      if (dateMatch) {
         const [d, m, y] = dateMatch[1].split("/");
         dataStr = `${y}-${m}-${d}`;
      }

      const parseNum = (val: string) => {
        if (!val) return 0;
        let str = String(val).replace(/[^\d.,]/g, "");
        if (str.includes('.') && str.includes(',')) {
            str = str.replace(/\./g, '').replace(',', '.');
        } else if (str.includes(',')) {
            str = str.replace(',', '.');
        }
        return Number(str);
      };

      const payload = {
        data: dataStr,
        hora: null, 
        numero_nf: null, 
        chave_nfe: null, 
        cnpj: null, 
        fornecedor: postoMatch ? postoMatch[1].trim() : "Importado",
        placa: placaMatch ? placaMatch[1].toUpperCase() : null, 
        litros: litrosMatch ? parseNum(litrosMatch[1]) : 0,
        preco_litro: litrosMatch ? parseNum(litrosMatch[2]) : 0, 
        km: kmNum, 
        origem: "pdf",
        produto: produtoMatch ? produtoMatch[0].trim().toUpperCase() : "DIESEL S-10"
      };

      await apiPost("/abastecimentos/importar", payload);
      toast.success("Nota Fiscal importada com sucesso!");
      invalidate();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao importar o PDF.");
    }
  };

  const handleImportXLS = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: "array" });
      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];
      const rows = XLSX.utils.sheet_to_json<any[]>(sheet, { header: 1, raw: false });

      if (rows.length === 0) { toast.error("Nenhuma linha encontrada."); return; }

      let headerRow: string[] = [];
      let startRow = -1;
      
      for (let i = 0; i < rows.length; i++) {
        const row = rows[i] || [];
        const rowStr = row.join(" ").toUpperCase();
        if (rowStr.includes("DATA") && rowStr.includes("PLACA") && rowStr.includes("LITROS")) {
          headerRow = row.map((c: any) => String(c).toUpperCase().trim());
          startRow = i + 1;
          break;
        }
      }

      if (startRow === -1) { toast.error("Cabeçalho não encontrado."); return; }

      const findIdx = (name: string) => headerRow.findIndex(h => h.includes(name.toUpperCase()));
      
      const idxData = findIdx("DATA");
      const idxPlaca = findIdx("PLACA");
      const idxKm = findIdx("LEITURA");
      const idxPosto = findIdx("POSTO");
      const idxLitros = findIdx("LITROS");
      const idxPreco = findIdx("V. LITRO");
      const idxValor = findIdx("VALOR"); // Coluna J

      if (idxData === -1 || idxPlaca === -1 || idxLitros === -1 || idxPreco === -1) {
        toast.error("Colunas essenciais não encontradas no cabeçalho."); return;
      }

      const totalLinhas = rows.length - startRow;
      setImportProgress({ total: totalLinhas, current: 0, errors: [] });
      
      let importados = 0;
      const erros: any[] = [];

      for (let i = startRow; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAIS") || String(row[idxData]).includes("Bsoft")) {
          setImportProgress(prev => prev ? { ...prev, current: prev.current + 1 } : null); continue;
        }

        let dataStr = String(row[idxData]).trim();
        if (dataStr.includes("-")) {
           const [y, m, d] = dataStr.split(" ")[0].split("-");
           dataStr = `${d}/${m}/${y}`;
        }

        const placaRaw = String(row[idxPlaca] || "").trim();
        const placa = placaRaw.split("/")[0].replace("-", "").toUpperCase();

        const litrosNum = typeof row[idxLitros] === "number" ? row[idxLitros] : Number(String(row[idxLitros]).replace(",", "."));
        const precoNum = typeof row[idxPreco] === "number" ? row[idxPreco] : Number(String(row[idxPreco]).replace(",", "."));
        const valorNum = idxValor !== -1 ? (typeof row[idxValor] === "number" ? row[idxValor] : Number(String(row[idxValor]).replace(",", "."))) : (litrosNum * precoNum);
        
        const kmStr = String(row[idxKm] || "0");
        
        const payload = {
          data: dataStr,
          placa: placa,
          km: Number(kmStr.replace(/\./g, "").replace(",", ".")),
          fornecedor: String(row[idxPosto] || "").trim(),
          litros: litrosNum,
          preco_litro: precoNum,
          valor_total: valorNum, // Envia o valor exato da coluna J
          hora: null,
          numero_nf: null,
          chave_nfe: null,
          cnpj: null,
          origem: "excel"
        };

        try {
          await apiPost("/abastecimentos/importar", payload);
          importados++;
        } catch (err: any) {
          erros.push({ linha: i + 1, placa: placa || "N/A", erro: err.response?.data?.detail || err.message || "Erro" });
        }
        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }

      setImportProgress(prev => prev ? { ...prev, current: totalLinhas, errors: erros } : null);
      if (erros.length === 0) toast.success(`${importados} abastecimentos importados com sucesso!`);
      invalidate();
    } catch (error) {
      console.error(error); toast.error("Erro ao ler o arquivo."); setImportProgress(null);
    }
  };

  const handleImportEdenred = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: "array" });
      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];
      const rows = XLSX.utils.sheet_to_json<any[]>(sheet, { header: 1, raw: false });

      if (rows.length < 2) { toast.error("Planilha vazia ou inválida."); return; }

      const headerRow = rows[0].map((c: any) => String(c).toUpperCase().trim());
      const findIdx = (name: string) => headerRow.findIndex(h => h.includes(name));

      const idxData = findIdx("DATA TRANSACAO");
      const idxPlaca = findIdx("PLACA");
      const idxProduto = findIdx("TIPO COMBUSTIVEL");
      const idxLitros = findIdx("LITROS");
      const idxPreco = findIdx("VL/LITRO");
      const idxKm = findIdx("HODOMETRO");
      const idxPosto = findIdx("NOME ESTABELECIMENTO");
      const idxValor = findIdx("VALOR EMISSAO");

      if (idxData === -1 || idxPlaca === -1 || idxLitros === -1) {
        toast.error("Colunas essenciais do Edenred não encontradas."); return;
      }

      const totalLinhas = rows.length - 1;
      setImportProgress({ total: totalLinhas, current: 0, errors: [] });
      let importados = 0;
      const erros: any[] = [];

      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAL") || String(row[idxPlaca]).toUpperCase().includes("TOTAL")) {
          setImportProgress(prev => prev ? { ...prev, current: prev.current + 1 } : null);
          continue;
        }

        let dataStr = String(row[idxData]).trim();
        let dataFinal = dataStr.split(" ")[0];
        let horaFinal = dataStr.includes(" ") ? dataStr.split(" ")[1].substring(0, 5) : null;

        const kmStr = String(row[idxKm] || "0");
        const kmNum = Number(kmStr.replace(/[^\d]/g, ""));

        const litrosNum = Number(String(row[idxLitros] || "0").replace(",", "."));
        const precoNum = Number(String(row[idxPreco] || "0").replace(",", "."));
        const valorNum = Number(String(row[idxValor] || "0").replace(",", "."));
        const produtoStr = String(row[idxProduto] || "DIESEL").toUpperCase();

        const payload = {
          data: dataFinal,
          placa: String(row[idxPlaca]).toUpperCase().trim(),
          km: kmNum,
          fornecedor: String(row[idxPosto] || "").trim(),
          litros: litrosNum,
          preco_litro: precoNum,
          valor_total: valorNum,
          produto: produtoStr,
          hora: horaFinal,
          numero_nf: null,
          chave_nfe: null,
          cnpj: null,
          origem: "excel"
        };

        try {
          await apiPost("/abastecimentos/importar", payload);
          importados++;
        } catch (err: any) {
          erros.push({ linha: i + 1, placa: payload.placa, erro: err.response?.data?.detail || err.message || "Erro" });
        }

        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }

      setImportProgress(prev => prev ? { ...prev, current: totalLinhas, errors: erros } : null);
      if (erros.length === 0) toast.success(`${importados} abastecimentos Edenred importados!`);
      invalidate();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao ler a planilha do Edenred.");
      setImportProgress(null);
    }
  };

  const salvar = useMutation({
    mutationFn: () => {
      const payload = { ...form, combustivel_id: form.combustivel_id, motorista_id: form.motorista_id === NENHUM ? null : form.motorista_id, litros: Number(form.litros.replace(",", ".")), preco_litro: Number(form.preco_litro.replace(",", ".")), km: Number(form.km) };
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
  const abrirNovo = () => { setEditingId(null); setForm(vazio(hoje)); setOpen(true); };
  const abrirEdicao = (r: Abastecimento) => { setEditingId(r.id); setForm({ data: r.data, veiculo_id: r.veiculo_id, motorista_id: r.motorista_id || NENHUM, litros: String(r.litros), preco_litro: String(r.preco_litro), posto: r.posto, km: String(r.km), observacoes: r.observacoes || "", numero_nf: r.numero_nf || "", chave_nfe: r.chave_nfe || "", hora: r.hora || "", cnpj: r.cnpj || "", fornecedor: r.fornecedor || "", origem: r.origem || "excel" }); setOpen(true); };

  const handleVeiculoChange = async (veiculoId: string) => {
    set("veiculo_id")(veiculoId); if (!veiculoId) return;
    try {
      if (!editingId && !form.km) { 
        const d = await apiGet<{ultimo_km: number}>(`/abastecimentos/ultimo-km/${veiculoId}`); 
        setForm(s => ({ ...s, km: String(Math.round(d.ultimo_km)) })); 
      }
      const a = await apiGet<any[]>("/acoplamentos"); const ativo = a.find(x => x.veiculo_id === veiculoId);
      if (ativo && ativo.motorista_id && !editingId) setForm(s => ({ ...s, motorista_id: ativo.motorista_id }));
    } catch (e) { console.error(e); }
  };

  const cards = [
    { label: "Abastecimentos", valor: resumo.total, icon: List, color: "#38bdf8", sub: "registros", tip: "Total de abastecimentos no período." },
    { label: "Total Abastecido", valor: `${num(resumo.litros, 3)} L`, icon: Droplets, color: "#2dd4bf", sub: "volume", tip: "Soma de todos os litros." },
    { label: "Valor Total", valor: brl(resumo.valor), icon: DollarSign, color: "#fbbf24", sub: "custo", tip: "Soma de todo o valor pago." },
    { label: "Média Geral", valor: `${num(resumo.media, 2)} km/L`, icon: TrendingUp, color: "#a78bfa", sub: "eficiência", tip: "Cálculo: (Soma KM Rodados) / (Soma Litros)." },
    { label: "Preço Médio", valor: `${brl(resumo.preco)}/L`, icon: Target, color: "#f87171", sub: "por litro", tip: "Cálculo: (Valor Total) / (Total Litros)." },
    { label: "Maior Abastecimento", valor: resumo.maior ? brl(resumo.maior.valor_total) : "—", icon: ArrowUpRight, color: "#4ade80", sub: resumo.maior?.veiculo_label.split(" · ")[0], tip: "O abastecimento de maior valor." },
    { label: "Menor Abastecimento", valor: resumo.menor ? brl(resumo.menor.valor_total) : "—", icon: ArrowDownRight, color: "#f87171", sub: resumo.menor?.motorista_label || resumo.menor?.veiculo_label.split(" · ")[0], tip: "O abastecimento de menor valor." },
    { label: "Média por Abast.", valor: brl(resumo.mediaValor), icon: DollarSign, color: "#fb923c", sub: "R$ / registro", tip: "Cálculo: (Valor Total) / (Qtd Abastecimentos)." },
    { label: "Média de KM", valor: `${num(resumo.mediaKm, 0)} km`, icon: TrendingUp, color: "#60a5fa", sub: "por abastecimento", tip: "Cálculo: (Soma KM Rodados) / (Qtd Abastecimentos)." },
    { label: "Custo por KM", valor: brl(resumo.custoPorKm), icon: DollarSign, color: "#34d399", sub: "combustível", tip: "Cálculo: (Valor Total) / (Soma KM Rodados)." },
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
      <div className="mb-4 grid gap-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
        {cards.map((c) => (
          <div key={c.label} title={c.tip} className="glass lift relative overflow-hidden rounded-xl hover:scale-[1.02] cursor-help" style={{ padding: '8px 12px', height: '72px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '22px', height: '22px', borderRadius: '6px', backgroundColor: `${c.color}20`, color: c.color }}><c.icon size={12} /></div>
              <p style={{ fontSize: '11px', color: '#94a3b8', margin: 0, fontWeight: 500 }}>{c.label}</p>
            </div>
            <div>
              <p style={{ fontSize: '16px', fontWeight: 600, color: '#f8fafc', margin: 0, lineHeight: 1.1 }}>{c.valor}</p>
              {c.sub && <p style={{ fontSize: '9px', color: '#64748b', marginTop: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.sub}</p>}
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
                <TableCell className="text-slate-300 px-2 truncate max-w-[150px] text-center">{r.produto || "—"}</TableCell>
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
        <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader><DialogTitle>{editingId ? "Editar" : "Novo"} Abastecimento</DialogTitle></DialogHeader>
          <form className="grid grid-cols-2 gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            <div className="grid gap-1.5"><Label>Data *</Label><Input type="date" value={form.data} onChange={(e) => set("data")(e.target.value)} required /></div>
            <div className="grid gap-1.5"><Label>Hodômetro *</Label><Input type="number" value={form.km} onChange={(e) => set("km")(e.target.value)} required /></div>
            <div className="col-span-2 grid gap-1.5"><Label>Veículo *</Label><FieldSelect value={form.veiculo_id} onChange={handleVeiculoChange} options={veicOpts} placeholder="Selecione" testId="form-veiculo" /></div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Combustível *</Label>
              <FieldSelect value={form.combustivel_id || ""} onChange={(v) => setForm(s => ({ ...s, combustivel_id: v }))} options={combOpts} placeholder="Selecione o combustível" testId="form-combustivel" />
            </div>
            <div className="col-span-2 grid gap-1.5"><Label>Motorista</Label><FieldSelect value={form.motorista_id} onChange={set("motorista_id")} options={[{ value: NENHUM, label: "— Nenhum —" }, ...(motoristas.data ?? []).filter((m: any) => m.ativo).map((m: any) => ({ value: m.id, label: m.nome }))]} testId="form-motorista" /></div>
            <div className="grid gap-1.5"><Label>Litros *</Label><Input inputMode="decimal" value={form.litros} onChange={(e) => set("litros")(e.target.value)} required /></div>
            <div className="grid gap-1.5"><Label>Preço/L *</Label><Input inputMode="decimal" value={form.preco_litro} onChange={(e) => set("preco_litro")(e.target.value)} required /></div>
            <div className="col-span-2 grid gap-1.5"><Label>Posto *</Label><Input value={form.posto} onChange={(e) => set("posto")(e.target.value)} required /></div>
            <div className="grid gap-1.5"><Label>Nº NF</Label><Input value={form.numero_nf} onChange={(e) => setForm(s => ({ ...s, numero_nf: e.target.value }))} /></div>
            <div className="grid gap-1.5"><Label>Hora</Label><Input type="time" value={form.hora} onChange={(e) => setForm(s => ({ ...s, hora: e.target.value }))} /></div>
            <div className="col-span-2 grid gap-1.5"><Label>Chave NF-e</Label><Input value={form.chave_nfe} onChange={(e) => setForm(s => ({ ...s, chave_nfe: e.target.value }))} /></div>
            <div className="grid gap-1.5"><Label>CNPJ Emitente</Label><Input value={form.cnpj} onChange={(e) => setForm(s => ({ ...s, cnpj: e.target.value }))} /></div>
            <div className="grid gap-1.5"><Label>Fornecedor</Label><Input value={form.fornecedor} onChange={(e) => setForm(s => ({ ...s, fornecedor: e.target.value }))} /></div>
            <p className="col-span-2 rounded-lg bg-slate-950/60 p-3 text-sm">Valor total: <span className="font-semibold text-slate-50">{Number.isFinite(total) ? brl(total) : "—"}</span></p>
            <DialogFooter className="col-span-2"><Button type="submit" disabled={salvar.isPending || !form.veiculo_id}>{editingId ? "Salvar" : "Registrar"}</Button></DialogFooter>
          </form>
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
