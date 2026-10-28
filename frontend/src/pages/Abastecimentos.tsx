import { useMemo, useState, useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Fuel, Plus, Eye, Trash2, ArrowUpRight, ArrowDownRight, DollarSign, Droplets, Target, TrendingUp, List, Pencil, FileText, Upload, AlertTriangle, Info, Search, Loader2, Star, CheckCircle2 } from "lucide-react";
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

const formatData = (d: string) => {
  if (!d) return "—";
  if (d.includes("/")) return d;
  if (d.includes("-")) {
      const parts = d.split("T")[0].split("-");
      if (parts.length === 3) return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }
  return d;
};

const formatCnpj = (val: string) => {
  return val.replace(/\D/g, '')
    .replace(/^(\d{2})(\d)/, '$1.$2')
    .replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3')
    .replace(/\.(\d{3})(\d)/, '.$1/$2')
    .replace(/(\d{4})(\d)/, '$1-$2')
    .slice(0, 18);
};

const vazio = (hoje: string) => ({ 
  data: hoje, veiculo_id: "", motorista_id: NENHUM, litros: "", preco_litro: "", posto: "", km: "", observacoes: "",
  numero_nf: "", chave_nfe: "", codigo_transacao: "", hora: "", cnpj: "", fornecedor: "", origem: "manual", produto: "DIESEL", combustivel_id: "",
  cidade: "", estado: "", avaliacao: 0
});

export default function Abastecimentos() {
  const qc = useQueryClient();
  const hoje = useHoje();
  const { data: me } = useMe();
  const veiculos = useVeiculos();
  const motoristas = useMotoristas();
  const [filtroVeiculo, setFiltroVeiculo] = useState(TODOS);
  const [mes, setMes] = useState("");
  const [filtroMotorista, setFiltroMotorista] = useState(TODOS);
  const [filtroPosto, setFiltroPosto] = useState("");
  const [filtroNF, setFiltroNF] = useState(TODOS);
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState(() => vazio(""));
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const [pendingEdenredRows, setPendingEdenredRows] = useState<any[]>([]);
  const [pdfPendingData, setPdfPendingData] = useState<any>(null);
  const [avaliacaoPendentePdf, setAvaliacaoPendentePdf] = useState(0);
  const [openPdfConfirm, setOpenPdfConfirm] = useState(false);
  const [importandoEdenred, setImportandoEdenred] = useState(false);
  const [importandoPDF, setImportandoPDF] = useState(false);
  const [pdfPendingFornecedor, setPdfPendingFornecedor] = useState<any>(null);
  const [openPdfFornecedorConfirm, setOpenPdfFornecedorConfirm] = useState(false);
  const [avaliacaoPdf, setAvaliacaoPdf] = useState(0);
  const [pdfArquivosLote, setPdfArquivosLote] = useState<File[]>([]);
  const [openPdfModal, setOpenPdfModal] = useState(false);
  const [pdfFilesSelected, setPdfFilesSelected] = useState<File[]>([]);
  const [openPdfLoteConfirm, setOpenPdfLoteConfirm] = useState(false);
  const isImportingPDFRef = useRef(false);
  const [openConfirmImport, setOpenConfirmImport] = useState(false);
  const [cliquesConfirmacao, setCliquesConfirmacao] = useState(0);
  const [openEdenredConfirm, setOpenEdenredConfirm] = useState(false);
  const isImportingEdenredRef = useRef(false);
  const [openFornecedoresModal, setOpenFornecedoresModal] = useState(false);
  const [fornecedoresPendentes, setFornecedoresPendentes] = useState<any[]>([]);
  const [selectedFornecedores, setSelectedFornecedores] = useState<Record<string, boolean>>({});
  const [avaliacoesPendentes, setAvaliacoesPendentes] = useState<Record<string, number>>({});
  const fileInputRef = useRef<HTMLInputElement>(null);
  const xlsInputRef = useRef<HTMLInputElement>(null);
  const edenredInputRef = useRef<HTMLInputElement>(null);
  const [importProgress, setImportProgress] = useState<{ total: number; current: number; errors: any[] } | null>(null);
  const [cnpjLoading, setCnpjLoading] = useState(false);
  const [pdfPendenteData, setPdfPendenteData] = useState<any | null>(null);
  const [fornecedorPendente, setFornecedorPendente] = useState<{nome: string, cnpj: string, cidade: string, estado: string, endereco?: string, bairro?: string, avaliacao?: number} | null>(null);
  
  const { data: fornecedores = [], refetch: refetchFornecedores } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });

  const params = new URLSearchParams();
  if (filtroVeiculo !== TODOS) params.set("veiculo_id", filtroVeiculo);
  if (mes) params.set("mes", mes);
  const q = useQuery({
    queryKey: ["abastecimentos", filtroVeiculo, mes],
    queryFn: () => apiGet<Abastecimento[]>(`/abastecimentos?${params.toString()}`),
    staleTime: 0,
  });
  const rows = q.isError ? [] : (q.data ?? []);

  const rowsComCalculo = useMemo(() => {
    const porVeiculo: Record<string, any[]> = {};
    rows.forEach(r => {
      if (!porVeiculo[r.veiculo_id]) porVeiculo[r.veiculo_id] = [];
      porVeiculo[r.veiculo_id].push(r);
    });

    const rowsFinais: any[] = [];
    Object.values(porVeiculo).forEach(lista => {
      lista.sort((a, b) => {
        const dateComp = a.data.localeCompare(b.data);
        if (dateComp !== 0) return dateComp;
        return a.km - b.km;
      });
      
      for (let i = 0; i < lista.length; i++) {
        const atual = { ...lista[i] };
        if (i > 0) {
          const anterior = lista[i - 1];
          if (atual.km > anterior.km) {
            atual.km_rodados = atual.km - anterior.km;
            if (atual.litros > 0 && !String(atual.produto || "").toUpperCase().includes("ARLA")) {
              atual.media_km_l = atual.km_rodados / atual.litros;
            }
          }
        }
        rowsFinais.push(atual);
      }
    });

    return rowsFinais.sort((a, b) => b.data.localeCompare(a.data) || b.km - a.km);
  }, [rows]);

  const rowsFiltradas = useMemo(() => {
    return rowsComCalculo.filter(r => {
      if (filtroVeiculo !== TODOS && r.veiculo_id !== filtroVeiculo) return false;
      if (filtroMotorista !== TODOS && r.motorista_id !== filtroMotorista) return false;
      if (filtroPosto && !(r.posto || (r as any).fornecedor || "").toLowerCase().includes(filtroPosto.toLowerCase())) return false;
      if (filtroNF === "com" && !(r.numero_nf || r.chave_nfe)) return false;
      if (filtroNF === "sem" && (r.numero_nf || r.chave_nfe)) return false;
      if (mes && !r.data.startsWith(mes)) return false;
      return true;
    });
  }, [rowsComCalculo, filtroVeiculo, filtroMotorista, filtroPosto, filtroNF, mes]);

  const parseSafe = (val: any) => {
        if (val === undefined || val === null || val === "") return 0;
        if (typeof val === 'number') return val;
        let str = String(val).replace(/[^0-9.,-]/g, "");
        if (str.includes('.') && str.includes(',')) str = str.replace(/\./g, '').replace(',', '.');
        else if (str.includes(',')) str = str.replace(',', '.');
        return Number(str) || 0;
      };

      
      const resumo = useMemo(() => {
        const litros = rowsFiltradas.reduce((s, r) => s + parseSafe(r.litros), 0);
        const valor = rowsFiltradas.reduce((s, r) => s + parseSafe(r.valor_total), 0);
        const km = rowsFiltradas.reduce((s, r) => s + parseSafe(r.km_rodados), 0);
        const comMedia = rowsFiltradas.filter(r => parseSafe(r.media_km_l) > 0);
        const mediaGeral = comMedia.length > 0 ? comMedia.reduce((s, r) => s + parseSafe(r.media_km_l), 0) / comMedia.length : 0;
        const preco = litros > 0 ? valor / litros : 0;
        const maior = rowsFiltradas.reduce((max, r) => parseSafe(r.valor_total) > parseSafe(max?.valor_total) ? r : max, null as Abastecimento | null);
        const menor = rowsFiltradas.reduce((min, r) => parseSafe(r.valor_total) < parseSafe(min?.valor_total) || !min ? r : min, null as Abastecimento | null);
        return { litros, valor, km, media: litros > 0 ? km / litros : 0, preco, total: rowsFiltradas.length, maior, menor, mediaValor: rowsFiltradas.length > 0 ? valor / rowsFiltradas.length : 0, mediaKm: rowsFiltradas.length > 0 ? km / rowsFiltradas.length : 0, custoPorKm: km > 0 ? valor / km : 0, comNF: rowsFiltradas.filter(r => r.numero_nf).length, semNF: rowsFiltradas.filter(r => !r.numero_nf).length };
      }, [rowsFiltradas]);

  const ranking = useMemo(() => {
    const porVeiculo: Record<string, { label: string, litros: number, km: number }> = {};
    rowsFiltradas.forEach(r => {
      if (r.km_rodados != null && r.km_rodados > 0 && r.media_km_l != null) {
        if (!porVeiculo[r.veiculo_id]) porVeiculo[r.veiculo_id] = { label: r.veiculo_label.split(" · ")[0], litros: 0, km: 0 };
        porVeiculo[r.veiculo_id].litros += (Number(r.litros) || 0);
        porVeiculo[r.veiculo_id].km += (Number(r.km_rodados) || 0);
      }
    });
    return Object.values(porVeiculo).map(v => ({ label: v.label, media: v.litros > 0 ? v.km / v.litros : 0 })).sort((a, b) => b.media - a.media).slice(0, 5);
  }, [rowsFiltradas]);

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ["abastecimentos"] });
    qc.invalidateQueries({ queryKey: ["fornecedores"] });
    qc.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const buscarCnpj = async () => {
    const cnpjLimpo = form.cnpj.replace(/\D/g, "");
    if (cnpjLimpo.length !== 14) { toast.error("CNPJ inválido"); return; }
    setCnpjLoading(true);
    try {
      const existente = fornecedores.find((f: any) => f.documento && f.documento.replace(/\D/g, '') === cnpjLimpo);
      if (existente) {
        setForm(s => ({ ...s, fornecedor: existente.nome, cnpj: existente.documento || "", cidade: existente.cidade || "", estado: existente.estado || "", avaliacao: existente.avaliacao || 0 }));
        toast.success(`Fornecedor encontrado: ${existente.nome}`);
        return;
      }
      const data = await apiGet<any>(`/fornecedores/consultar-cnpj/${cnpjLimpo}`);
      setFornecedorPendente({ 
        nome: data.razao_social, cnpj: formatCnpj(cnpjLimpo), cidade: data.municipio, estado: data.uf,
        endereco: `${data.logradouro || ''}, ${data.numero || ''}`.trim(), bairro: data.bairro || '', avaliacao: 0
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
        documento: fornecedorPendente.cnpj,
        cidade: fornecedorPendente.cidade, 
        estado: fornecedorPendente.estado,
        endereco: fornecedorPendente.endereco,
        bairro: fornecedorPendente.bairro,
        avaliacao: fornecedorPendente.avaliacao || 0,
        ativo: true 
      });
      toast.success("Fornecedor cadastrado automaticamente!");
      await refetchFornecedores();
      setForm(s => ({ ...s, fornecedor: fornecedorPendente.nome, cidade: fornecedorPendente.cidade, estado: fornecedorPendente.estado }));
      setFornecedorPendente(null);
    } catch (err: any) {
      // Se o erro for 409 (Conflict), significa que o fornecedor já existe
      if (err.message && (err.message.includes("409") || err.message.toLowerCase().includes("já cadastrado") || err.message.toLowerCase().includes("exist"))) {
        toast.warning("Este CNPJ já está cadastrado no sistema. Carregando os dados do fornecedor...");
        
        // Recarrega a lista para garantir que pegamos o ID/registro mais recente
        await refetchFornecedores();
        setFornecedorPendente(null);
      } else {
        toast.error(err.message || "Erro ao cadastrar fornecedor.");
      }
    }
  };

  

  

  

  
  

  

  
  

  const toggleAllFornecedores = (checked: boolean) => {
    const newSelected: Record<string, boolean> = {};
    fornecedoresPendentes.forEach(f => { newSelected[f.nome] = checked; });
    setSelectedFornecedores(newSelected);
  };

  const handleImportXLS = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: "array" });
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const rows = XLSX.utils.sheet_to_json<any[]>(sheet, { header: 1, raw: false });

      let headerIdx = -1;
      for (let i = 0; i < rows.length; i++) {
        const rowStr = rows[i].map((c: any) => String(c).toUpperCase()).join(" ");
        if (rowStr.includes("DATA") && rowStr.includes("PLACA") && rowStr.includes("LITROS")) {
          headerIdx = i;
          break;
        }
      }

      if (headerIdx === -1) { toast.error("Cabeçalho do BSOFT não encontrado."); return; }

      const header = rows[headerIdx].map((c: any) => String(c).toUpperCase().trim());
      const findIdx = (name: string) => header.findIndex(h => h.includes(name));

      const idxData = findIdx("DATA");
      const idxPlaca = findIdx("PLACA");
      const idxKm = findIdx("LEITURA");
      const idxPosto = findIdx("POSTO");
      const idxLitros = findIdx("LITROS");
      const idxValor = findIdx("VALOR");
      const idxPreco = findIdx("V. LITRO");
      const idxProduto = findIdx("PRODUTO");

      const totalLinhas = rows.length - headerIdx - 1;
      setImportProgress({ total: totalLinhas, current: 0, errors: [] });
      let importados = 0; const erros: any[] = [];

      const parseNum = (val: any) => {
        if (!val) return 0;
        let str = String(val).replace(/[^0-9.,-]/g, "");
        if (str.includes('.') && str.includes(',')) {
            if (str.lastIndexOf(',') > str.lastIndexOf('.')) str = str.replace(/\./g, '').replace(',', '.');
            else str = str.replace(/,/g, '');
        } else if (str.includes(',')) {
            str = str.replace(',', '.');
        }
        return Number(str) || 0;
      };

      for (let i = headerIdx + 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAIS")) continue;

        let dataStr = String(row[idxData]).trim().split(" ")[0]; 
        
        // CONVERSÃO INTELIGENTE DE DATA (M/D/YY -> YYYY-MM-DD)
        if (dataStr.includes("/")) {
            const parts = dataStr.split("/");
            if (parts.length === 3) {
                let month = parts[0].padStart(2, '0');
                let day = parts[1].padStart(2, '0');
                let year = parts[2];
                if (year.length === 2) year = "20" + year;
                dataStr = `${year}-${month}-${day}`;
            }
        }

        let placaRaw = String(row[idxPlaca] || "").trim();
        const placa = placaRaw.replace("-", "").split("/")[0].toUpperCase();

        if (!placa || placa.length < 7 || placa.includes("BSOFT")) continue;

        const litros = parseNum(row[idxLitros]);
        const preco_litro = parseNum(row[idxPreco]);
        const valor_total = parseNum(row[idxValor]);
        const km = parseNum(row[idxKm]);

        const payload = {
          data: dataStr,
          placa: placa,
          km: km,
          fornecedor: String(row[idxPosto] || "").trim(),
          litros: litros,
          preco_litro: preco_litro,
          valor_total: valor_total,
          produto: String(row[idxProduto] || "DIESEL").toUpperCase(),
          origem: "bsoft"
        };

        try { 
          await apiPost("/abastecimentos/importar", payload); 
          importados++; 
          await new Promise(r => setTimeout(r, 150)); 
        } catch (err: any) { 
          erros.push({ linha: i + 1, placa: placa, erro: err.message && err.message.includes("409") ? "Já importado" : (err.message || "Erro") }); 
        }
        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }

      setImportProgress(prev => prev ? { ...prev, current: totalLinhas, errors: erros } : null);
      if (erros.length === 0) {
        toast.success(`${importados} registros BSOFT importados!`);
      } else if (importados > 0) {
        toast.warning(`${importados} importados, mas ${erros.length} já existiam.`);
      } else {
        toast.error("Todos os registros já foram importados.");
      }
      invalidate();
    } catch (error) {
      console.error(error); toast.error("Erro ao ler o arquivo BSOFT."); setImportProgress(null);
    }
  };

  const salvar = useMutation({
    mutationFn: () => {
      const payload = { 
        data: form.data, veiculo_id: form.veiculo_id, 
        motorista_id: form.motorista_id === NENHUM ? null : form.motorista_id, 
        litros: Number(String(form.litros || "").replace(",", ".")) || 0, preco_litro: Number(String(form.preco_litro || "").replace(",", ".")) || 0,
        posto: form.fornecedor || "Importado", km: Number(form.km), observacoes: form.observacoes,
        numero_nf: form.numero_nf || null, chave_nfe: form.chave_nfe || null, hora: form.hora || null,
        cnpj: form.cnpj || null, fornecedor: form.fornecedor || null, cidade: form.cidade || null,
        estado: form.estado || null, produto: form.produto || "DIESEL", origem: form.origem
      };
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

  const total = (Number(String(form.litros || "").replace(",", ".")) || 0) * (Number(String(form.preco_litro || "").replace(",", ".")) || 0);
  const set = (k: keyof ReturnType<typeof vazio>) => (v: string) => setForm((s) => ({ ...s, [k]: v }));
  const veicOpts = (veiculos.data ?? []).filter(v => v.ativo).map((v) => ({ value: v.id, label: `${v.placa} · ${v.modelo}` }));
  const abrirNovo = () => { setEditingId(null); setForm({ ...vazio(hoje), origem: "manual" }); setOpen(true); };
  const abrirEdicao = (r: Abastecimento) => { 
    setEditingId(r.id); 
    let dataStr = r.data;
    if (dataStr.includes("/")) { const [d, m, y] = dataStr.split("/"); dataStr = `${y}-${m}-${d}`; } else { dataStr = dataStr.split("T")[0]; }
    setForm({ 
      data: dataStr, veiculo_id: r.veiculo_id, motorista_id: r.motorista_id || NENHUM, 
      combustivel_id: (r as any).combustivel_id || "", litros: String(r.litros || ""), preco_litro: String(r.preco_litro || ""), 
      posto: r.posto || "", km: String(r.km || ""), observacoes: r.observacoes || "", numero_nf: r.numero_nf || "", 
      chave_nfe: r.chave_nfe || "", codigo_transacao: (r as any).codigo_transacao || "", hora: r.hora || "", cnpj: r.cnpj || "", fornecedor: (r as any).fornecedor || r.posto || "", cidade: (r as any).cidade || "", estado: (r as any).estado || "", 
      fornecedor: (r as any).fornecedor || r.posto || "", cidade: (r as any).cidade || "", estado: (r as any).estado || "", 
      avaliacao: 0, origem: r.origem || "excel", produto: r.produto || "DIESEL" 
    }); 
    setOpen(true); 
  };

  const handleVeiculoChange = async (veiculoId: string) => {
    set("veiculo_id")(veiculoId); if (!veiculoId) return;
    try {
      if (!editingId && !form.km) { const d = await apiGet<{ultimo_km: number}>(`/abastecimentos/ultimo-km/${veiculoId}`); setForm(s => ({ ...s, km: String(Math.round(d.ultimo_km)) })); }
      const a = await apiGet<any[]>("/acoplamentos"); const ativo = a.find(x => x.veiculo_id === veiculoId);
      if (ativo && ativo.motorista_id && !editingId) setForm(s => ({ ...s, motorista_id: ativo.motorista_id }));
    } catch (e) { console.error(e); }
  };

  const cards = [
    { label: "Total Geral", valor: resumo.total, icon: List, color: "#38bdf8", sub: "registros", tip: "Total de abastecimentos no período." },
    { label: "Com NF", valor: resumo.comNF, icon: CheckCircle2, color: "#10b981", sub: "registros", tip: "Abastecimentos com Nota Fiscal." },
    { label: "Sem NF", valor: resumo.semNF, icon: AlertTriangle, color: "#ef4444", sub: "registros", tip: "Abastecimentos sem Nota Fiscal." },
    { label: "Total Litros", valor: `${num(resumo.litros, 1)} L`, icon: Droplets, color: "#2dd4bf", sub: "volume", tip: "Soma de todos os litros." },
    { label: "Valor Total", valor: brl(resumo.valor), icon: DollarSign, color: "#fbbf24", sub: "custo", tip: "Soma dos valores totais." },
    { label: "Média Geral", valor: `${num(resumo.media, 2)} km/L`, icon: TrendingUp, color: "#a78bfa", sub: "eficiência", tip: "KM Rodados / Litros." },
    { label: "Preço Médio", valor: `${brl(resumo.preco)}/L`, icon: Target, color: "#f87171", sub: "por litro", tip: "Valor Total / Litros." },
    { 
      label: "Maior Abast.", 
      valor: resumo.maior ? brl(resumo.maior.valor_total) : "—", 
      icon: ArrowUpRight, 
      color: "#4ade80", 
      sub: resumo.maior?.veiculo_label.split(" · ")[0], 
      tip: resumo.maior ? `DETALHES DO MAIOR:

Placa: ${resumo.maior.veiculo_label.split(" · ")[0]}
Data: ${dataBR(resumo.maior.data)}
Litros: ${num(resumo.maior.litros, 2)} L
Preço/L: ${brl(resumo.maior.preco_litro)}
Total: ${brl(resumo.maior.valor_total)}
Posto: ${resumo.maior.posto || resumo.maior.fornecedor || "—"}` : "Nenhum registro" 
    },
    { 
      label: "Menor Abast.", 
      valor: resumo.menor ? brl(resumo.menor.valor_total) : "—", 
      icon: ArrowDownRight, 
      color: "#f87171", 
      sub: resumo.menor?.veiculo_label.split(" · ")[0], 
      tip: resumo.menor ? `DETALHES DO MENOR:

Placa: ${resumo.menor.veiculo_label.split(" · ")[0]}
Data: ${dataBR(resumo.menor.data)}
Litros: ${num(resumo.menor.litros, 2)} L
Preço/L: ${brl(resumo.menor.preco_litro)}
Total: ${brl(resumo.menor.valor_total)}
Posto: ${resumo.menor.posto || resumo.menor.fornecedor || "—"}` : "Nenhum registro" 
    },
    { label: "Média por Abast.", valor: brl(resumo.mediaValor), icon: DollarSign, color: "#fb923c", sub: "R$ / registro", tip: "Valor Total / Qtd." },
    { label: "Média de KM", valor: `${num(resumo.mediaKm, 0)} km`, icon: TrendingUp, color: "#60a5fa", sub: "por abast.", tip: "KM / Qtd." },
    { label: "Custo por KM", valor: brl(resumo.custoPorKm), icon: DollarSign, color: "#34d399", sub: "combustível", tip: "Valor Total / KM." },
  ];

  

  

  

  

  

  

  

  

  
  const handleImportEdenred = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: "array" });
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const rows = XLSX.utils.sheet_to_json<any[]>(sheet, { header: 1, raw: false });

      if (rows.length < 2) { 
        toast.error("Planilha vazia."); 
        return; 
      }

      const headerRow = rows[0].map((c: any) => String(c).toUpperCase().trim());
      const findIdx = (name: string) => headerRow.findIndex(h => h.replace(/\\s+/g, '').includes(name.replace(/\\s+/g, '')));

      const idxCod = findIdx("CODIGO TRANSACAO");
      const idxData = findIdx("DATA TRANSACAO");
      const idxPlaca = findIdx("PLACA");
      const idxMotorista = findIdx("NOME MOTORISTA");
      const idxProduto = findIdx("TIPO COMBUSTIVEL");
      const idxLitros = findIdx("LITROS");
      const idxPreco = findIdx("VL/LITRO") !== -1 ? findIdx("VL/LITRO") : findIdx("V. LITRO");
      const idxKm = findIdx("HODOMETRO");
      const idxKmRodados = findIdx("KM RODADOS");
      const idxMedia = findIdx("KM/LITRO");
      const idxPosto = findIdx("NOME ESTABELECIMENTO");
      const idxValor = findIdx("VALOR EMISSAO");
      const idxCidade = findIdx("CIDADE");
      const idxEstado = findIdx("UF");
      const idxEndereco = findIdx("ENDERECO");
      const idxBairro = findIdx("BAIRRO");

      const parseNum = (val: any) => {
        if (val === undefined || val === null || val === "") return 0;
        if (typeof val === 'number') return val;
        let str = String(val).replace(/[^0-9.,-]/g, "");
        if (str.includes('.') && str.includes(',')) {
            if (str.lastIndexOf(',') > str.lastIndexOf('.')) str = str.replace(/\\./g, '').replace(',', '.');
            else str = str.replace(/,/g, '');
        } else if (str.includes(',')) {
            str = str.replace(',', '.');
        }
        return Number(str) || 0;
      };

      const mapFornecedores = new Set(fornecedores.map((f: any) => f.nome.toUpperCase().trim()));
      const unregistered = new Map<string, any>();
      const payloads: any[] = [];

      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAL")) continue;

        const dataStr = String(row[idxData]).trim();
        const dataFinal = dataStr.split(" ")[0];
        const horaFinal = dataStr.includes(" ") ? dataStr.split(" ")[1].substring(0, 5) : null;

        const kmNum = parseNum(row[idxKm]);
        const litrosNum = parseNum(row[idxLitros]);
        const precoNum = parseNum(row[idxPreco]);
        const valorNum = idxValor !== -1 ? parseNum(row[idxValor]) : (litrosNum * precoNum);
        const kmRodadosNum = idxKmRodados !== -1 ? parseNum(row[idxKmRodados]) : null;
        const mediaNum = idxMedia !== -1 ? parseNum(row[idxMedia]) : null;

        const motoristaNome = idxMotorista !== -1 ? String(row[idxMotorista] || "").trim() : "";
        let motoristaId = NENHUM;
        if (motoristaNome && motoristas.data) {
          const mot = motoristas.data.find((m: any) => m.nome.toUpperCase() === motoristaNome.toUpperCase() || m.nome.toUpperCase().includes(motoristaNome));
          if (mot) motoristaId = mot.id;
        }

        const fornecedorNome = String(row[idxPosto] || "").trim();
        const cidade = idxCidade !== -1 ? String(row[idxCidade] || "").trim() : "";
        const estado = idxEstado !== -1 ? String(row[idxEstado] || "").trim() : "";
        const endereco = idxEndereco !== -1 ? String(row[idxEndereco] || "").trim() : "";
        const bairro = idxBairro !== -1 ? String(row[idxBairro] || "").trim() : "";

        if (fornecedorNome && !mapFornecedores.has(fornecedorNome.toUpperCase().trim())) {
          unregistered.set(fornecedorNome, { nome: fornecedorNome, cidade, estado, endereco, bairro });
        }

        let cnpjFormatado = "";
        const existingForn = fornecedores.find((f: any) => f.nome.toUpperCase() === fornecedorNome.toUpperCase());
        if (existingForn && existingForn.documento) {
          cnpjFormatado = existingForn.documento;
        }

        payloads.push({
          data: dataFinal, placa: String(row[idxPlaca] || "").toUpperCase().trim(), km: kmNum,
          motorista_id: motoristaId, fornecedor: fornecedorNome, cnpj: cnpjFormatado,
          cidade, estado, litros: litrosNum, preco_litro: precoNum, valor_total: valorNum,
          km_rodados: kmRodadosNum, media_km_l: mediaNum,
          produto: String(row[idxProduto] || "DIESEL").toUpperCase(),
          codigo_transacao: String(row[idxCod] || "").trim(),
          hora: horaFinal, numero_nf: null, chave_nfe: null, origem: "excel"
        });
      }

      const pendentes = Array.from(unregistered.values());
      if (pendentes.length > 0) {
        const initialSelected: Record<string, boolean> = {};
        const initialAvaliacoes: Record<string, number> = {};
        pendentes.forEach(f => {
          initialSelected[f.nome] = true;
          initialAvaliacoes[f.nome] = 0;
        });
        setSelectedFornecedores(initialSelected);
        setAvaliacoesPendentes(initialAvaliacoes);
        setFornecedoresPendentes(pendentes);
        setPendingEdenredRows(payloads);
        setOpenFornecedoresModal(true);
      } else {
        setPendingEdenredRows(payloads);
        setOpenConfirmImport(true);
      }
    } catch (error) {
      console.error(error); 
      toast.error("Erro ao ler Edenred."); 
    }
  };

  const executarImportacaoEdenred = async (rowsData: any[]) => {
    if (isImportingEdenredRef.current) return;
    isImportingEdenredRef.current = true;
    
    // Fecha TODOS os modais ANTES de iniciar
    setOpenConfirmImport(false);
    setOpenFornecedoresModal(false);
    setOpenEdenredConfirm(false); // <--- FECHA O MODAL DE "IMPORTAR PLANILHA EDENRED?"
    setOpen(false); // Fecha qualquer outro modal que possa estar aberto
    
    setImportandoEdenred(true);
    setImportProgress({ total: rowsData.length, current: 0, errors: [] });
    
    let importados = 0; const erros: any[] = [];
    
    try {
      for (let i = 0; i < rowsData.length; i++) {
        const payload = rowsData[i];
        try { 
          await apiPost("/abastecimentos/importar", payload); 
          importados++; 
          await new Promise(resolve => setTimeout(resolve, 150));
        } catch (err: any) { 
          erros.push({ linha: i + 1, placa: payload.placa, erro: err.message && err.message.includes("409") ? "Já importado" : (err.message || "Erro") }); 
        }
        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }
      
      setImportProgress(prev => prev ? { ...prev, current: rowsData.length, errors: erros } : null);
      
      if (erros.length === 0) toast.success(`${importados} Edenred importados!`);
      else if (importados > 0) toast.warning(`${importados} importados, mas ${erros.length} deram erro ou já existiam.`);
      else toast.error("Todos os registros já foram importados ou deram erro.");
      
      invalidate();
    } finally {
      // DESLIGA O OVERLAY E LIMPA TUDO
      setImportandoEdenred(false);
      isImportingEdenredRef.current = false;
      setPendingEdenredRows([]);
      setImportProgress(null);
      
      // Garante que todos os modais estejam fechados no final
      setOpenConfirmImport(false);
      setOpenFornecedoresModal(false);
      setOpenEdenredConfirm(false);
      setOpen(false);
    }
  };

  const confirmarCadastroLote = async () => {
    if (isImportingEdenredRef.current) return;
    isImportingEdenredRef.current = true;
    
    const selecionados = fornecedoresPendentes.filter(f => selectedFornecedores[f.nome]);
    const semAvaliacao = selecionados.filter(f => !avaliacoesPendentes[f.nome] || avaliacoesPendentes[f.nome] === 0);
    
    if (semAvaliacao.length > 0) {
      toast.error("Por favor, atribua uma nota (estrelas) para todos os fornecedores selecionados.");
      isImportingEdenredRef.current = false;
      return;
    }

    try {
      for (const f of selecionados) {
        await apiPost("/fornecedores", {
          nome: f.nome, documento: "", endereco: f.endereco, bairro: f.bairro,
          cidade: f.cidade, estado: f.estado, ativo: true, avaliacao: avaliacoesPendentes[f.nome] || 0
        }).catch(err => {
          if (!err.message?.includes("409")) console.error(`Erro ao cadastrar ${f.nome}`, err);
        });
      }
      await refetchFornecedores();
      toast.success(`${selecionados.length} fornecedores cadastrados!`);
      
      setOpenFornecedoresModal(false);
      setOpenConfirmImport(true);
    } catch (err) {
      console.error(err);
    } finally {
      isImportingEdenredRef.current = false;
    }
  };
  

  

  

  

  
  
  

  
  
  

  

  
  

  

  
  
  
  

  
  

  
  const handleImportPDF = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    setPdfArquivosLote(Array.from(files));
    executarImportacaoPDFLote(Array.from(files));
    e.target.value = "";
  };

  const executarImportacaoPDFLote = async (arquivos: File[]) => {
    if (importandoPDF || arquivos.length === 0) return;

    setImportandoPDF(true);
    let importados = 0;
    const erros: string[] = [];
    let fornecedorPendenteData: any = null;

    for (let fileIdx = 0; fileIdx < arquivos.length; fileIdx++) {
      const file = arquivos[fileIdx];
      try {
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await Promise.race([
          pdfjsLib.getDocument({ data: arrayBuffer }).promise,
          new Promise((_, reject) => setTimeout(() => reject(new Error("Timeout (10s)")), 10000))
        ]) as any;

        let text = "";
        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const content = await page.getTextContent();
          text += content.items.map((item: any) => item.str).join(" ") + "\n";
        }
        text = text.replace(/\n/g, " ").replace(/\s+/g, " ");

        const placaMatch = text.match(/PLACA[:\s]*([A-Z0-9]{7})/i);
        const placa = placaMatch ? placaMatch[1].toUpperCase() : "";
        const veiculo = veiculos.data?.find((v: any) => v.placa.replace("-", "").toUpperCase() === placa.replace("-", "").toUpperCase());
        if (!veiculo) { erros.push(`${file.name}: veículo não encontrado`); continue; }

        const kmMatch = text.match(/KM[:\s]*(\d+)/i);
        const km = kmMatch ? Number(kmMatch[1]) : 0;
        const dateMatch = text.match(/DATA DA EMISS[ÃA]O.*?(\d{2}\/\d{2}\/\d{4})/i);
        let dataStr = new Date().toISOString().split("T")[0];
        if (dateMatch) { const [d, m, y] = dateMatch[1].split("/"); dataStr = `${y}-${m}-${d}`; }

        const timeMatch = text.match(/HORA DA SA[ÍI]DA.*?(\d{2}:\d{2})/i);
        const nfMatch = text.match(/N[º°]\s*(\d+)/i);
        const chaveMatch = text.match(/CHAVE DE ACESSO DA NF-E\s*([\d\s]+)/i);
        const cnpjMatch = text.match(/C\.N\.P\.J\.\s*\/\s*C\.P\.F\.\s*([\d\.\/\-]+)/i) || text.match(/C\.N\.P\.J\.\s*([\d\.\/\-]+)/i);
        const fornMatch = text.match(/RECEBEMOS DE\s+([^,]+?)(?:\s*\(|,)/i);
        const litrosMatch = text.match(/L\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)/i);
        
        const parseNum = (val: string) => {
          if (!val) return 0;
          let str = String(val).replace(/[^\d.,]/g, "");
          if (str.includes('.') && str.includes(',')) str = str.replace(/\./g, '').replace(',', '.');
          else if (str.includes(',')) str = str.replace(',', '.');
          return Number(str);
        };

        const cnpjLimpo = cnpjMatch ? cnpjMatch[1].replace(/\D/g, '') : "";
        const fornecedorNome = fornMatch ? fornMatch[1].trim() : "";
        const payload = {
          data: dataStr, placa, km,
          fornecedor: fornecedorNome,
          cnpj: cnpjLimpo ? formatCnpj(cnpjLimpo) : "",
          litros: litrosMatch ? parseNum(litrosMatch[1]) : 0,
          preco_litro: litrosMatch ? parseNum(litrosMatch[2]) : 0,
          valor_total: litrosMatch ? parseNum(litrosMatch[3]) : 0,
          produto: "DIESEL",
          numero_nf: nfMatch ? nfMatch[1] : null,
          chave_nfe: chaveMatch ? chaveMatch[1].replace(/\s/g, "") : null,
          hora: timeMatch ? timeMatch[1] : null,
          origem: "pdf"
        };

        // Se fornecedor não existe, para o lote e abre modal
        if (fornecedorNome) {
          const existingForn = fornecedores.find((f: any) => f.nome.toUpperCase() === fornecedorNome.toUpperCase());
          if (!existingForn) {
            fornecedorPendenteData = { nome: fornecedorNome, cnpj: payload.cnpj, payload, restantes: arquivos.slice(fileIdx + 1) };
            break; // Sai do loop para mostrar o modal
          }
        }

        // Se fornecedor existe (ou não tem nome), importa direto
        await apiPost("/abastecimentos/importar", payload);
        importados++;
        await new Promise(r => setTimeout(r, 150));
      } catch (err: any) {
        if (err.message && (err.message.includes("409") || err.message.toLowerCase().includes("duplicado"))) {
          erros.push(`${file.name}: Nota já importada anteriormente.`);
        } else {
          erros.push(`${file.name}: ${err.message || "Erro"}`);
        }
      }
    }

    setImportandoPDF(false);

    if (fornecedorPendenteData) {
      // Pausa e abre modal de avaliação
      setPdfPendingFornecedor(fornecedorPendenteData);
      setAvaliacaoPdf(0);
      setOpenPdfFornecedorConfirm(true);
      if (importados > 0) toast.success(`${importados} PDF(s) importado(s) antes da pausa.`);
      return;
    }

    if (erros.length === 0) toast.success(`${importados} PDF(s) importado(s)!`);
    else if (importados > 0) toast.warning(`${importados} importado(s), ${erros.length} com erro.`);
    else toast.error("Nenhum PDF importado.");

    invalidate();
    setPdfArquivosLote([]);
  };

  const confirmarFornecedorPdf = async (cadastrar: boolean) => {
    if (!pdfPendingFornecedor) return;

    const { nome, cnpj, payload, restantes } = pdfPendingFornecedor;

    if (cadastrar) {
      try {
        await apiPost("/fornecedores", {
          nome,
          documento: cnpj || "",
          ativo: true,
          avaliacao: avaliacaoPdf
        });
        await refetchFornecedores();
        toast.success(`Fornecedor ${nome} cadastrado!`);
      } catch (err: any) {
        if (err.message?.includes("409")) {
          toast.warning(`Fornecedor ${nome} já existe.`);
        }
      }
    }

    // Importa o abastecimento
    try {
      await apiPost("/abastecimentos/importar", payload);
      toast.success("Nota Fiscal importada com sucesso!");
    } catch (err: any) {
      if (err.message && (err.message.includes("409") || err.message.toLowerCase().includes("duplicado"))) {
        toast.error("Nota Fiscal já importada anteriormente.");
      } else {
        toast.error("Erro ao importar: " + (err.message || ""));
      }
    }

    invalidate();
    setOpenPdfFornecedorConfirm(false);
    setPdfPendingFornecedor(null);
    setAvaliacaoPdf(0);

    // Continua o lote com os arquivos restantes
    if (restantes && restantes.length > 0) {
      executarImportacaoPDFLote(restantes);
    } else {
      setPdfArquivosLote([]);
    }
  };  return (
    <div>
      <PageHeader eyebrow="Operação" title="Abastecimentos" description="Registro detalhado." actions={
        <div className="flex gap-2">
          <input type="file" accept=".xls,.xlsx" ref={xlsInputRef} onChange={handleImportXLS} className="hidden" />
          <Button variant="outline" onClick={() => xlsInputRef.current?.click()}><Upload className="size-4 mr-2" /> Importar BSOFT</Button>
          
          <input type="file" accept=".xlsx" ref={edenredInputRef} onChange={handleImportEdenred} className="hidden" />
          <Button 
            variant="outline" 
            
            disabled={importandoEdenred || openEdenredConfirm} 
            onClick={() => setOpenEdenredConfirm(true)}
          >
            <Upload className="size-4 mr-2" /> 
            {importandoEdenred ? "Importando..." : "Importar Edenred"}
          </Button>

          <input type="file" accept=".pdf" multiple ref={fileInputRef} onChange={handleImportPDF} className="hidden" />
          <Button variant="outline" disabled={importandoPDF} onClick={() => fileInputRef.current?.click()}><FileText className="size-4 mr-2" /> {importandoPDF ? "Importando..." : "Importar NF"}</Button>
          <Button onClick={abrirNovo}><Plus className="size-4" /> Novo</Button>
        </div>
      }/>

      <div className="mb-4 grid gap-2 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
        {cards.map((c) => (
          <div key={c.label} title={c.tip} className="glass lift relative overflow-hidden rounded-xl hover:scale-[1.02] cursor-help" style={{ padding: '6px 10px', height: '58px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '16px', height: '16px', borderRadius: '4px', backgroundColor: `${c.color}20`, color: c.color }}><c.icon size={10} /></div>
              <p style={{ fontSize: '9px', color: '#94a3b8', margin: 0, fontWeight: 500 }}>{c.label}</p>
            </div>
            <div>
              <p style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc', margin: 0, lineHeight: 1 }}>{c.valor}</p>
              {c.sub && <p style={{ fontSize: '8px', color: '#64748b', marginTop: '0px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.sub}</p>}
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
        <div className="grid w-48 gap-1.5"><Label>Motorista</Label><FieldSelect value={filtroMotorista} onChange={setFiltroMotorista} options={[{ value: TODOS, label: "Todos" }, ...(motoristas.data ?? []).map((m: any) => ({ value: m.id, label: m.nome }))]} /></div>
        <div className="grid w-48 gap-1.5"><Label>Posto</Label><Input value={filtroPosto} onChange={(e) => setFiltroPosto(e.target.value)} placeholder="Nome do posto..." className="h-9" /></div>
        <div className="grid w-40 gap-1.5"><Label>Nota Fiscal</Label><FieldSelect value={filtroNF} onChange={setFiltroNF} options={[{ value: TODOS, label: "Todas" }, { value: "com", label: "Com NF" }, { value: "sem", label: "Sem NF" }]} /></div>
        {(mes || filtroVeiculo !== TODOS || filtroMotorista !== TODOS || filtroPosto || filtroNF !== TODOS) && (
          <Button variant="ghost" onClick={() => { setMes(""); setFiltroVeiculo(TODOS); setFiltroMotorista(TODOS); setFiltroPosto(""); setFiltroNF(TODOS); }} className="mb-[2px]">Limpar Filtros</Button>
        )}
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table className="text-xs">
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {["Data", "Origem", "NF", "Cód.Trans", "Veículo", "Motorista", "Produto", "Litros", "R$/L", "Total", "Posto", "KM", "Rodados", "Média", "Ações"].map(h => (
                <TableHead key={h} className="text-[10px] uppercase text-slate-500 px-2 text-center">{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rowsFiltradas.length === 0 && (
              <TableRow>
                <TableCell colSpan={15} className="py-10 text-center text-slate-500">
                  Nenhum abastecimento encontrado.
                </TableCell>
              </TableRow>
            )}
            {rowsFiltradas.map((r: any) => (
              <TableRow key={r.id} className="border-slate-800/70">
                {/* Data */}
                <TableCell className="text-xs text-slate-400 px-2 text-center">{formatData(r.data)}</TableCell>
                {/* Origem */}
                <TableCell className="text-center px-2">
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold uppercase ${
                    r.origem === 'manual' ? 'bg-slate-800 text-slate-300' : 
                    r.origem === 'pdf' ? 'bg-red-500/20 text-red-400' : 
                    r.origem === 'bsoft' ? 'bg-orange-500/20 text-orange-400' : 
                    'bg-emerald-500/20 text-emerald-400'
                  }`}>
                    {r.origem === 'bsoft' ? 'Bsoft' : r.origem}
                  </span>
                </TableCell>
                {/* NF */}
                <TableCell className="text-center px-2">
                  {r.numero_nf ? <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded">{r.numero_nf}</span> : <span className="text-[10px] text-slate-500">—</span>}
                </TableCell>
                {/* Cód.Trans */}
                <TableCell className="text-center px-2 text-[10px] text-slate-400 font-mono">
                  {r.codigo_transacao || "—"}
                </TableCell>
                {/* Veículo */}
                <TableCell className="text-xs font-medium text-slate-200 px-2 text-center">
                  {r.veiculo_label?.split(" · ")[0] || "—"}
                </TableCell>
                {/* Motorista */}
                <TableCell className="text-slate-300 px-2 truncate max-w-[150px] text-center">
                  {r.motorista_label ?? "—"}
                </TableCell>
                {/* Produto */}
                <TableCell className="text-slate-300 px-2 truncate max-w-[150px] text-center">
                  {r.produto || "—"}
                </TableCell>
                {/* Litros */}
                <TableCell className="tabular-nums px-2 text-center">{num(r.litros, 3)}</TableCell>
                {/* R$/L */}
                <TableCell className="tabular-nums px-2 text-center">{brl(r.preco_litro)}</TableCell>
                {/* Total */}
                <TableCell className="tabular-nums px-2 text-center">{brl(r.valor_total)}</TableCell>
                {/* Posto (com estrelas) */}
                <TableCell className="text-slate-300 px-2 max-w-[150px] text-center align-middle">
                  <div className="flex flex-col items-center justify-center">
                    <span className="truncate w-full" title={r.fornecedor || r.posto}>{r.fornecedor || r.posto || "—"}</span>
                      {!r.cnpj && r.origem === 'excel' && (
                        <span className="text-red-500 animate-pulse font-bold text-[9px] flex items-center justify-center gap-1 mt-0.5">
                          <AlertTriangle className="size-3" /> CNPJ Pendente
                        </span>
                      )}
                    {(() => {
                      const docLimpo = (r.cnpj || "").replace(/\D/g, '');
                      const nomeLimpo = (r.fornecedor || r.posto || "").toUpperCase();
                      const forn = fornecedores?.find((f: any) => (f.documento && f.documento.replace(/\D/g, '') === docLimpo && docLimpo.length > 0) || (f.nome && f.nome.toUpperCase() === nomeLimpo));
                      if (!forn || !forn.avaliacao || forn.avaliacao === 0) return null;
                      return (
                        <div className="flex gap-0.5 mt-1 justify-center">
                          {[1, 2, 3, 4, 5].map(star => <Star key={star} className={`size-2.5 ${star <= forn.avaliacao ? 'fill-amber-400 text-amber-400' : 'text-slate-700'}`} />)}
                        </div>
                      );
                    })()}
                  </div>
                </TableCell>
                {/* KM */}
                <TableCell className="tabular-nums px-2 text-center">{num(r.km)}</TableCell>
                {/* Rodados */}
                <TableCell className="tabular-nums px-2 text-center">{r.km_rodados != null ? num(r.km_rodados) : "—"}</TableCell>
                {/* Média */}
                <TableCell className="tabular-nums px-2 text-center">{r.media_km_l != null ? num(r.media_km_l) : "—"}</TableCell>
                {/* Ações */}
                <TableCell className="text-center px-2">
                  <div className="flex items-center justify-center gap-1">
                    <Button size="icon-sm" variant="ghost" onClick={() => { 
                      setForm({ ...vazio(hoje), ...r, litros: String(r.litros || ""), preco_litro: String(r.preco_litro || ""), km: String(r.km || ""), origem: r.origem || "excel", fornecedor: (r as any).fornecedor || r.posto || "", cnpj: r.cnpj || "", cidade: (r as any).cidade || "", estado: (r as any).estado || "", codigo_transacao: (r as any).codigo_transacao || "" }); 
                      setOpen(true); setEditingId(r.id); 
                    }} title="Visualizar"><Eye className="size-4 text-emerald-400" /></Button>
                    <Button size="icon-sm" variant="ghost" onClick={() => {
                      if (r.origem === "pdf") toast.error("Proibido editar arquivo importado via PDF.");
                      else if (r.origem === "excel") toast.error("Proibido editar arquivo importado via Excel.");
                      else abrirEdicao(r);
                    }} title="Editar"><Pencil className="size-4 text-sky-400" /></Button>
                    <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(r.id)} title="Excluir"><Trash2 className="size-4 text-red-400" /></Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={(o) => { setOpen(o); if(!o) setEditingId(null); }}>
        <DialogContent className="sm:max-w-lg max-h-[95vh] overflow-y-auto overflow-x-hidden p-4 sm:p-6">
          <DialogHeader><DialogTitle>{editingId ? "Editar" : "Novo"} Abastecimento</DialogTitle></DialogHeader>
          <form className="grid grid-cols-2 gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            {/* Veículo */}
            <div className="col-span-2 grid gap-1.5 overflow-hidden">
              <Label>Veículo *</Label>
              <div className={`w-full ${form.origem !== "manual" ? "rounded-md border border-purple-800 bg-purple-950/20 px-3 py-2 pointer-events-none opacity-80" : ""}`}>
                <FieldSelect 
                  value={form.veiculo_id} 
                  onChange={handleVeiculoChange} 
                  options={veicOpts} 
                  placeholder="Selecione o veículo" 
                  disabled={form.origem !== "manual"} 
                />
              </div>
            </div>

            {/* Motorista */}
            <div className="col-span-2 grid gap-1.5 overflow-hidden">
              <Label>Motorista</Label>
              <div className={`w-full ${form.origem !== "manual" ? "rounded-md border border-purple-800 bg-purple-950/20 px-3 py-2 pointer-events-none opacity-80" : ""}`}>
                <FieldSelect 
                  value={form.motorista_id} 
                  onChange={set("motorista_id")} 
                  options={[{ value: NENHUM, label: "— Nenhum —" }, ...(motoristas.data ?? []).filter((m: any) => m.ativo).map((m: any) => ({ value: m.id, label: m.nome }))]} 
                  disabled={form.origem !== "manual"} 
                />
              </div>
            </div>
            
            {/* Data e Hodômetro */}
            <div className="grid gap-1.5 overflow-hidden">
              <Label>Data *</Label>
              <Input type="date" value={form.data} onChange={(e) => set("data")(e.target.value)} disabled={form.origem !== "manual"} className={form.origem !== "manual" ? "text-purple-400 border-purple-800 bg-purple-950/20 disabled:opacity-100 disabled:text-purple-400" : ""} required />
            </div>
            <div className="grid gap-1.5 overflow-hidden">
              <Label>Hodômetro *</Label>
              <Input type="number" value={form.km} onChange={(e) => set("km")(e.target.value)} disabled={form.origem !== "manual"} className={form.origem !== "manual" ? "text-purple-400 border-purple-800 bg-purple-950/20 disabled:opacity-100 disabled:text-purple-400" : ""} required />
            </div>
            
            {/* Litros e Preço */}
            <div className="grid gap-1.5 overflow-hidden">
              <Label>Litros *</Label>
              <Input inputMode="decimal" value={form.litros} onChange={(e) => set("litros")(e.target.value)} disabled={form.origem !== "manual"} className={form.origem !== "manual" ? "text-purple-400 border-purple-800 bg-purple-950/20 disabled:opacity-100 disabled:text-purple-400" : ""} required />
            </div>
            <div className="grid gap-1.5 overflow-hidden">
              <Label>Preço/L *</Label>
              <Input inputMode="decimal" value={form.preco_litro} onChange={(e) => set("preco_litro")(e.target.value)} disabled={form.origem !== "manual"} className={form.origem !== "manual" ? "text-purple-400 border-purple-800 bg-purple-950/20 disabled:opacity-100 disabled:text-purple-400" : ""} required />
            </div>

            {/* CNPJ, Fornecedor, Cidade e Estado */}
            <div className="col-span-2 border-t border-slate-800 pt-2 mt-1">
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-1.5 w-full overflow-hidden">
                  <Label>CNPJ Emitente</Label>
                  <div className="flex gap-2 w-full">
                    <Input value={form.cnpj} onChange={(e) => setForm(s => ({ ...s, cnpj: formatCnpj(e.target.value) }))} placeholder="00.000.000/0000-00" maxLength={18} disabled={form.origem !== "manual"} className={`w-full ${form.origem !== "manual" ? "text-purple-400 border-purple-800 bg-purple-950/20" : ""}`} />
                    <Button type="button" variant="default" onClick={buscarCnpj} disabled={cnpjLoading || form.cnpj.length < 18 || form.origem !== "manual"} className="bg-sky-600 hover:bg-sky-500 px-3 font-medium shrink-0">
                      {cnpjLoading ? <Loader2 className="size-4 animate-spin" /> : <><Search className="size-4 mr-1" /> Online</>}
                    </Button>
                  </div>
                </div>
                <div className="grid gap-1.5 w-full overflow-hidden">
                  <Label>Fornecedor *</Label>
                  <div className={`w-full ${form.origem !== "manual" ? "rounded-md border border-purple-800 bg-purple-950/20 px-3 py-2 pointer-events-none opacity-80" : ""}`}>
                    <FieldSelect 
                      value={form.fornecedor} 
                      onChange={(v) => {
                        const f = fornecedores.find((x:any) => x.nome === v);
                        setForm(s => ({ 
                          ...s, fornecedor: v, cnpj: f ? (f.documento || "") : s.cnpj, 
                          cidade: f ? (f.cidade || "") : s.cidade, estado: f ? (f.estado || "") : s.estado,
                          avaliacao: f ? (f.avaliacao || 0) : s.avaliacao
                        }));
                      }} 
                      options={fornecedores?.map((f: any) => ({ value: f.nome, label: f.nome })) || []} 
                      placeholder="Selecione o fornecedor" 
                      disabled={form.origem !== "manual"} 
                    />
                  </div>
                </div>
                <div className="grid gap-1.5 w-full overflow-hidden">
                  <Label>Cidade</Label>
                  <Input value={form.cidade} onChange={(e) => setForm(s => ({ ...s, cidade: e.target.value }))} disabled={form.origem !== "manual"} className={`w-full ${form.origem !== "manual" ? "text-purple-400 border-purple-800 bg-purple-950/20" : ""}`} />
                </div>
                <div className="grid gap-1.5 w-full overflow-hidden">
                  <Label>Estado (UF)</Label>
                  <Input value={form.estado} onChange={(e) => setForm(s => ({ ...s, estado: e.target.value }))} maxLength={2} disabled={form.origem !== "manual"} className={`w-full uppercase ${form.origem !== "manual" ? "text-purple-400 border-purple-800 bg-purple-950/20" : ""}`} />
                </div>
              </div>
            </div>

            {/* Avaliação */}
            <div className="col-span-2 flex items-center gap-3 bg-slate-900/30 p-2 rounded-lg border border-slate-800">
              <Label className="text-xs text-slate-400">Avaliação do Fornecedor:</Label>
              <div className={`flex gap-1 items-center ${form.origem !== "manual" ? "pointer-events-none" : ""}`}>
                {[1, 2, 3, 4, 5].map(star => (
                  <button type="button" key={star} onClick={() => setForm(s => ({ ...s, avaliacao: star }))} className="focus:outline-none hover:scale-110">
                    <Star className={`size-4 ${star <= form.avaliacao ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                  </button>
                ))}
                <span className="text-[10px] text-slate-500 ml-1">{form.avaliacao === 0 ? "" : `${form.avaliacao}/5`}</span>
              </div>
            </div>

            {/* NF, Hora e Chave */}
            <div className="grid gap-1.5 overflow-hidden">
              <Label>Código de Transação</Label>
              <Input value={form.codigo_transacao || ""} onChange={(e) => setForm(s => ({ ...s, codigo_transacao: e.target.value }))} disabled={form.origem !== "manual"} className={form.origem !== "manual" ? "text-purple-400 border-purple-800 bg-purple-950/20 disabled:opacity-100 disabled:text-purple-400" : ""} />
            </div>

            <div className="grid gap-1.5 overflow-hidden">
              <Label>Nº NF</Label>
              <Input value={form.numero_nf} onChange={(e) => setForm(s => ({ ...s, numero_nf: e.target.value }))} placeholder="Ex: 12550" disabled={form.origem !== "manual"} className={form.origem !== "manual" ? "text-purple-400 border-purple-800 bg-purple-950/20 disabled:opacity-100 disabled:text-purple-400" : ""} />
            </div>
            <div className="grid gap-1.5 overflow-hidden">
              <Label>Hora</Label>
              <Input type="time" value={form.hora} onChange={(e) => setForm(s => ({ ...s, hora: e.target.value }))} disabled={form.origem !== "manual"} className={form.origem !== "manual" ? "text-purple-400 border-purple-800 bg-purple-950/20 disabled:opacity-100 disabled:text-purple-400" : ""} />
            </div>
            <div className="col-span-2 grid gap-1.5 overflow-hidden">
              <Label>Chave NF-e</Label>
              <Input value={form.chave_nfe} onChange={(e) => setForm(s => ({ ...s, chave_nfe: e.target.value }))} placeholder="3126 1020..." disabled={form.origem !== "manual"} className={`w-full ${form.origem !== "manual" ? "text-purple-400 border-purple-800 bg-purple-950/20" : ""}`} />
            </div>

            {/* Valor Total */}
            <div className="col-span-2 rounded-xl bg-gradient-to-r from-slate-900 to-slate-800 border border-sky-500/30 p-4 flex justify-between items-center shadow-lg shadow-sky-500/10 mt-2">
              <span className="text-sm font-bold text-slate-300 uppercase tracking-wider">Valor Total</span>
              <span className="text-3xl font-bold text-emerald-400 drop-shadow-[0_0_8px_rgba(16,185,129,0.5)]">{Number.isFinite(total) ? brl(total) : "R$ 0,00"}</span>
            </div>

            <DialogFooter className="col-span-2 mt-2">
              <Button type="submit" disabled={salvar.isPending || !form.veiculo_id || (editingId && (form.origem !== "manual" || form.origem === "excel"))}>
                {editingId ? "Salvar" : "Registrar"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      
      
      
      <Dialog open={openFornecedoresModal} onOpenChange={(o) => { if (!o) { isImportingEdenredRef.current = false; setImportandoEdenred(false); } setOpenFornecedoresModal(o); }}>
        <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto overflow-x-hidden">
          <DialogHeader>
            <DialogTitle>Fornecedores Pendentes de Cadastro</DialogTitle>
            <DialogDescription>
              Os seguintes fornecedores da planilha não estão cadastrados. Selecione quem deseja cadastrar agora.
            </DialogDescription>
          </DialogHeader>
          <div className="py-2">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-10">
                    <input type="checkbox" className="size-4 rounded border-slate-700 bg-slate-900" 
                      checked={fornecedoresPendentes.length > 0 && fornecedoresPendentes.every(f => selectedFornecedores[f.nome])}
                      onChange={(e) => {
                        const newSelected: Record<string, boolean> = {};
                        fornecedoresPendentes.forEach(f => { newSelected[f.nome] = e.target.checked; });
                        setSelectedFornecedores(newSelected);
                      }} 
                    />
                  </TableHead>
                  <TableHead>Fornecedor</TableHead>
                  <TableHead>Cidade/UF</TableHead>
                  <TableHead>Avaliação</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {fornecedoresPendentes.map(f => (
                  <TableRow key={f.nome}>
                    <TableCell>
                      <input type="checkbox" className="size-4 rounded border-slate-700 bg-slate-900" 
                        checked={selectedFornecedores[f.nome] || false}
                        onChange={(e) => setSelectedFornecedores(s => ({ ...s, [f.nome]: e.target.checked }))} 
                      />
                    </TableCell>
                    <TableCell className="text-xs font-medium text-slate-200">{f.nome}</TableCell>
                    <TableCell className="text-xs text-slate-400">{f.cidade} / {f.estado}</TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        {[1, 2, 3, 4, 5].map(star => (
                          <button type="button" key={star} onClick={() => setAvaliacoesPendentes(s => ({ ...s, [f.nome]: star }))} className="focus:outline-none hover:scale-110">
                            <Star className={`size-4 ${star <= (avaliacoesPendentes[f.nome] || 0) ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                          </button>
                        ))}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setOpenFornecedoresModal(false)}>Cancelar</Button>
            <Button onClick={confirmarCadastroLote} disabled={fornecedoresPendentes.filter(f => selectedFornecedores[f.nome]).some(f => !avaliacoesPendentes[f.nome] || avaliacoesPendentes[f.nome] === 0)}>Cadastrar Selecionados e Importar</Button>
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

      <Dialog open={fornecedorPendente !== null} onOpenChange={(o) => {
          if (!o) {
            if (pdfPendenteData) {
              setForm(pdfPendenteData);
              setPdfPendenteData(null);
              setOpen(true);
            }
            setFornecedorPendente(null);
          }
        }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Fornecedor não encontrado</DialogTitle>
            <DialogDescription>O CNPJ {fornecedorPendente?.cnpj} não está cadastrado no sistema.</DialogDescription>
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
    
      {importandoEdenred && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-700 p-6 rounded-xl w-96 flex flex-col items-center gap-4 shadow-2xl">
            <Loader2 className="size-10 text-sky-500 animate-spin" />
            <h3 className="text-lg font-bold text-slate-100">Importando Edenred</h3>
            <p className="text-sm text-slate-400 text-center">
              Por favor, aguarde. Isso pode levar alguns minutos.
            </p>
            {importProgress && (
              <div className="w-full mt-2">
                <div className="flex justify-between text-xs text-slate-400 mb-1">
                  <span>Progresso</span>
                  <span>{importProgress.current} de {importProgress.total}</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
                  <div 
                    className="bg-sky-500 h-2.5 rounded-full transition-all duration-300" 
                    style={{ width: `${(importProgress.current / importProgress.total) * 100}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    
      <Dialog open={openEdenredConfirm} onOpenChange={(o) => { if (!importandoEdenred) { setOpenEdenredConfirm(o); } }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Importar planilha Edenred?</DialogTitle>
            <DialogDescription>
              Você será redirecionado para selecionar o arquivo. Aguarde o término da importação.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 flex flex-col items-center gap-4">
            {importandoEdenred ? (
              <>
                <Loader2 className="size-10 text-sky-500 animate-spin" />
                <p className="text-sm text-slate-300 font-medium">Importando...</p>
                {importProgress && (
                  <div className="w-full mt-2">
                    <div className="flex justify-between text-xs text-slate-400 mb-1">
                      <span>Progresso</span>
                      <span>{importProgress.current} de {importProgress.total}</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
                      <div className="bg-sky-500 h-2.5 rounded-full transition-all duration-300" style={{ width: `${(importProgress.current / importProgress.total) * 100}%` }}></div>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <p className="text-sm text-slate-400 text-center">
                Clique em "Selecionar Arquivo" para escolher a planilha do Edenred.
              </p>
            )}
          </div>
          <DialogFooter>
            {!importandoEdenred && (
              <>
                <Button variant="ghost" onClick={() => setOpenEdenredConfirm(false)}>Cancelar</Button>
                <Button onClick={() => { setOpenEdenredConfirm(false); edenredInputRef.current?.click(); }}>Selecionar Arquivo</Button>
              </>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    
      <Dialog open={openConfirmImport} onOpenChange={(o) => { if (!isImportingEdenredRef.current) setOpenConfirmImport(o); }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Confirmar Importação</DialogTitle>
            <DialogDescription>
              Deseja realmente importar {pendingEdenredRows.length} registros da planilha Edenred?
            </DialogDescription>
          </DialogHeader>
          
          <div className="my-4 p-3 bg-red-950/40 border border-red-800/50 rounded-lg">
            <p className="text-red-400 animate-pulse font-bold text-sm text-center flex items-center justify-center gap-2">
              <AlertTriangle className="size-5" /> 
              Atenção: O sistema importará apenas a PRIMEIRA leitura da planilha.
            </p>
          </div>

          <DialogFooter>
            <Button variant="ghost" onClick={() => { 
                setOpenConfirmImport(false); 
                setPendingEdenredRows([]);
              }}>Cancelar</Button>
            <Button 
              onClick={() => { 
                setOpenConfirmImport(false); setOpenEdenredConfirm(false); executarImportacaoEdenred(pendingEdenredRows); 
              }} 
              disabled={isImportingEdenredRef.current}
            >
              Sim, Importar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    
      
    
      
    
      
    
      
    
      
    
      
    
      
    
      <Dialog open={openPdfFornecedorConfirm} onOpenChange={(o) => { if (!o) { setOpenPdfFornecedorConfirm(false); setPdfPendingFornecedor(null); setAvaliacaoPdf(0); } }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Fornecedor não cadastrado (PDF)</DialogTitle>
            <DialogDescription>
              O fornecedor "{pdfPendingFornecedor?.nome}" não está cadastrado. Deseja cadastrá-lo com uma avaliação?
            </DialogDescription>
          </DialogHeader>
          
          <div className="py-4 flex flex-col items-center gap-3">
            <Label className="text-sm text-slate-400">Avaliação do Fornecedor</Label>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map(star => (
                <button type="button" key={star} onClick={() => setAvaliacaoPdf(star)} className="focus:outline-none hover:scale-110">
                  <Star className={`size-8 ${star <= avaliacaoPdf ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                </button>
              ))}
            </div>
            <span className="text-xs text-slate-500">
              {avaliacaoPdf === 0 ? "Selecione uma nota" : `${avaliacaoPdf} de 5 estrelas`}
            </span>
          </div>

          <DialogFooter className="flex-col sm:flex-row gap-2">
            <Button variant="ghost" onClick={() => { 
              setOpenPdfFornecedorConfirm(false); 
              setPdfPendingFornecedor(null); 
              setAvaliacaoPdf(0); 
            }}>Cancelar</Button>
            <Button variant="outline" onClick={() => confirmarFornecedorPdf(false)}>
              Apenas Importar
            </Button>
            <Button onClick={() => confirmarFornecedorPdf(true)} disabled={avaliacaoPdf === 0}>
              Cadastrar com Avaliação e Importar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
