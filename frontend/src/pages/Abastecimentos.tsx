import { useMemo, useState, useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Fuel, Plus, Trash2, ArrowUpRight, ArrowDownRight, DollarSign, Droplets, Target, TrendingUp, List, Pencil, FileText, Upload } from "lucide-react";
import * as pdfjsLib from "pdfjs-dist";
import pdfWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";
import * as XLSX from "xlsx";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPost, apiPut } from "@/lib/api";
import { brl, dataBR, errMsg, num } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
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

const vazio = (hoje: string) => ({ 
  data: hoje, veiculo_id: "", motorista_id: NENHUM, litros: "", preco_litro: "", posto: "", km: "", observacoes: "",
  numero_nf: "", chave_nfe: "", hora: "", cnpj: "", fornecedor: "", origem: "manual"
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

  const params = new URLSearchParams();
  if (filtroVeiculo !== TODOS) params.set("veiculo_id", filtroVeiculo);
  if (mes) params.set("mes", mes);
  const q = useQuery({
    queryKey: ["abastecimentos", filtroVeiculo, mes],
    queryFn: () => apiGet<Abastecimento[]>(`/abastecimentos?${params.toString()}`),
  });
  const rows = q.isError ? [] : (q.data ?? []);

  const resumo = useMemo(() => {
    const litros = rows.reduce((s, r) => s + r.litros, 0);
    const valor = rows.reduce((s, r) => s + r.valor_total, 0);
    const comKm = rows.filter((r) => r.km_rodados != null);
    const km = comKm.reduce((s, r) => s + (r.km_rodados ?? 0), 0);
    const litrosKm = comKm.reduce((s, r) => s + r.litros, 0);
    
    const maior = rows.reduce((max, r) => r.valor_total > (max?.valor_total || 0) ? r : max, null as Abastecimento | null);
    const menor = rows.reduce((min, r) => r.valor_total < (min?.valor_total || Infinity) ? r : min, null as Abastecimento | null);
    const mediaValor = rows.length ? valor / rows.length : 0;
    const mediaKm = comKm.length ? km / comKm.length : 0;
    const custoPorKm = km > 0 ? valor / km : 0;

    return { 
      litros, valor, km, media: litrosKm ? km / litrosKm : 0, preco: litros ? valor / litros : 0,
      total: rows.length, maior, menor, mediaValor, mediaKm, custoPorKm
    };
  }, [rows]);

  const ranking = useMemo(() => {
    const porVeiculo: Record<string, { label: string, litros: number, km: number }> = {};
    rows.forEach(r => {
      if (r.km_rodados != null) {
        if (!porVeiculo[r.veiculo_id]) porVeiculo[r.veiculo_id] = { label: r.veiculo_label.split(" · ")[0], litros: 0, km: 0 };
        porVeiculo[r.veiculo_id].litros += r.litros;
        porVeiculo[r.veiculo_id].km += r.km_rodados;
      }
    });
    
    return Object.values(porVeiculo)
      .map(v => ({ label: v.label, media: v.litros > 0 ? v.km / v.litros : 0 }))
      .sort((a, b) => b.media - a.media)
      .slice(0, 5);
  }, [rows]);

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

      const placaMatch = text.match(/PLACA[:\s]*([A-Z]{3}[0-9][A-Z0-9][0-9]{2})/i) || text.match(/PLACA[:\s]*([A-Z0-9]{7})/i);
      const kmMatch = text.match(/KM[:\s]*(\d+)/i);
      const litrosMatch = text.match(/L\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)/i) || text.match(/L\s+([\d.,]+)\s+([\d.,]+)/i);
      const nfMatch = text.match(/Nº\s*(\d+)/);
      const chaveMatch = text.match(/CHAVE DE ACESSO DA NF-E\s*([\d\s]+)/i);
      const cnpjMatch = text.match(/C\.N\.P\.J\.\s*([\d\.\/\-]+)/i);
      const fornecedorMatch = text.match(/RECEBEMOS DE\s*(.*?)\s*OS PRODUTOS/i);

      const parseNum = (val: string) => Number(val.replace(/\./g, "").replace(",", "."));

      const payload = {
        data: new Date().toISOString().split('T')[0],
        hora: null,
        numero_nf: nfMatch ? nfMatch[1] : null,
        chave_nfe: chaveMatch ? chaveMatch[1].replace(/\s/g, "") : null,
        cnpj: cnpjMatch ? cnpjMatch[1] : null,
        fornecedor: fornecedorMatch ? fornecedorMatch[1].trim() : null,
        placa: placaMatch ? placaMatch[1].toUpperCase() : null,
        litros: litrosMatch ? parseNum(litrosMatch[1]) : 0,
        preco_litro: litrosMatch ? parseNum(litrosMatch[2]) : 0,
        km: kmMatch ? Number(kmMatch[1]) : 0,
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
      const text = await file.text();
      const rowRegex = /<tr[^>]*>([\s\S]*?)<\/tr>/gi;
      const rows: string[][] = [];
      let rowMatch;

      while ((rowMatch = rowRegex.exec(text)) !== null) {
        const cells: string[] = [];
        let cellMatch;
        const cellRegexLocal = /<td[^>]*>([\s\S]*?)<\/td>/gi;
        while ((cellMatch = cellRegexLocal.exec(rowMatch[1])) !== null) {
          let cellText = cellMatch[1];
          cellText = cellText.replace(/<[^>]+>/g, "").trim();
          cellText = cellText.replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
          cells.push(cellText);
        }
        if (cells.length > 0) rows.push(cells);
      }

      if (rows.length === 0) {
        toast.error("Nenhuma linha encontrada no arquivo HTML.");
        return;
      }

      let startRow = -1;
      for (let i = 0; i < rows.length; i++) {
        const rowStr = rows[i].join(" ").toLowerCase();
        if (rowStr.includes("data") && rowStr.includes("placa") && rowStr.includes("litros")) {
          startRow = i + 1;
          break;
        }
      }

      if (startRow === -1) {
        toast.error("Cabeçalho da planilha não encontrado. Verifique se as colunas 'Data', 'Placa' e 'Litros' estão na planilha.");
        return;
      }

      const headerRow = rows[startRow - 1];
      const colIndex = (name: string) => headerRow.findIndex(h => h.toLowerCase().includes(name.toLowerCase()));

      const idxData = colIndex("data");
      const idxPlaca = colIndex("placa");
      const idxKm = colIndex("leitura");
      const idxPosto = colIndex("posto");
      const idxLitros = colIndex("litros");
      const idxPreco = colIndex("v. litro");

      if (idxData === -1 || idxPlaca === -1 || idxLitros === -1 || idxPreco === -1) {
        toast.error("Colunas essenciais não encontradas (Data, Placa, Litros, V. Litro).");
        return;
      }

      let importados = 0;

      for (let i = startRow; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || row[idxData].toLowerCase().includes("total") || row[idxData].includes("Bsoft")) continue;

        let dataStr = row[idxData];
        if (dataStr.includes("/")) {
           const [d, m, y] = dataStr.split("/");
           dataStr = `${y}-${m}-${d}`;
        }

        const placaRaw = row[idxPlaca] || "";
        const placa = placaRaw.split("/")[0].replace("-", "").toUpperCase();

        const litrosRaw = Number(row[idxLitros].replace(/\./g, "").replace(",", ".")) / 1000;
        const valorLitroRaw = Number(row[idxPreco].replace(/\./g, "").replace(",", ".")) / 100;
        
        const payload = {
          data: dataStr,
          placa: placa,
          km: Number((row[idxKm] || "0").replace(/\./g, "").replace(",", ".")),
          fornecedor: row[idxPosto] || "",
          litros: litrosRaw,
          preco_litro: valorLitroRaw,
          hora: null,
          numero_nf: null,
          chave_nfe: null,
          cnpj: null
        };

        try {
          await apiPost("/abastecimentos/importar", payload);
          importados++;
        } catch (err) {
          console.error(`Erro na linha ${i + 1}:`, err);
        }
      }

      toast.success(`${importados} abastecimentos importados com sucesso!`);
      invalidate();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao ler o arquivo.");
    }
  };
    const salvar = useMutation({
    mutationFn: () => {
      const payload = {
        data: form.data,
        veiculo_id: form.veiculo_id,
        motorista_id: form.motorista_id === NENHUM ? null : form.motorista_id,
        litros: Number(form.litros.replace(",", ".")),
        preco_litro: Number(form.preco_litro.replace(",", ".")),
        posto: form.posto,
        km: Number(form.km),
        observacoes: form.observacoes,
        numero_nf: form.numero_nf || null,
        chave_nfe: form.chave_nfe || null,
        hora: form.hora || null,
        cnpj: form.cnpj || null,
        fornecedor: form.fornecedor || null,
        origem: form.origem,
      };
      if (editingId) return apiPut<Abastecimento>(`/abastecimentos/${editingId}`, payload);
      return apiPost<Abastecimento>("/abastecimentos", payload);
    },
    onSuccess: () => {
      toast.success(editingId ? "Abastecimento atualizado" : "Abastecimento registrado");
      setOpen(false);
      setEditingId(null);
      invalidate();
    },
    onError: (e) => toast.error(errMsg(e)),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete<void>(`/abastecimentos/${id}`),
    onSuccess: () => { toast.success("Abastecimento excluído"); setExcluirId(null); invalidate(); },
    onError: (e) => toast.error(errMsg(e)),
  });

  const total = Number(form.litros.replace(",", ".")) * Number(form.preco_litro.replace(",", "."));
  const set = (k: keyof ReturnType<typeof vazio>) => (v: string) => setForm((s) => ({ ...s, [k]: v }));
  const veicOpts = (veiculos.data ?? []).filter(v => v.ativo).map((v) => ({ value: v.id, label: `${v.placa} · ${v.modelo}` }));

  const abrirNovo = () => {
    setEditingId(null);
    setForm(vazio(hoje));
    setOpen(true);
  };

  const abrirEdicao = (r: Abastecimento) => {
    setEditingId(r.id);
    setForm({
      data: r.data,
      veiculo_id: r.veiculo_id,
      motorista_id: r.motorista_id || NENHUM,
      litros: String(r.litros),
      preco_litro: String(r.preco_litro),
      posto: r.posto,
      km: String(r.km),
      observacoes: r.observacoes || "",
      numero_nf: r.numero_nf || "",
      chave_nfe: r.chave_nfe || "",
      hora: r.hora || "",
      cnpj: r.cnpj || "",
      fornecedor: r.fornecedor || "",
      origem: r.origem || "manual",
    });
    setOpen(true);
  };

  const handleVeiculoChange = async (veiculoId: string) => {
    set("veiculo_id")(veiculoId);
    if (!veiculoId) return;

    try {
      if (!editingId) {
        const kmData = await apiGet<{ ultimo_km: number }>(`/abastecimentos/ultimo-km/${veiculoId}`);
        setForm(s => ({ ...s, km: String(kmData.ultimo_km) }));
      }

      const acoplamentos = await apiGet<any[]>("/acoplamentos");
      const acoplamentoAtivo = acoplamentos.find(a => a.veiculo_id === veiculoId);
      
      if (acoplamentoAtivo && acoplamentoAtivo.motorista_id && !editingId) {
        setForm(s => ({ ...s, motorista_id: acoplamentoAtivo.motorista_id }));
      }
    } catch (error) {
      console.error("Erro ao buscar dados:", error);
    }
  };

  const cards = [
    { label: "Abastecimentos", valor: resumo.total, icon: List, color: "#38bdf8", sub: "registros no período" },
    { label: "Total Abastecido", valor: `${num(resumo.litros, 1)} L`, icon: Droplets, color: "#2dd4bf", sub: "volume total" },
    { label: "Valor Total", valor: brl(resumo.valor), icon: DollarSign, color: "#fbbf24", sub: "custo total" },
    { label: "Média Geral", valor: `${num(resumo.media, 2)} km/L`, icon: TrendingUp, color: "#a78bfa", sub: "eficiência da frota" },
    { label: "Preço Médio", valor: `${brl(resumo.preco)}/L`, icon: Target, color: "#f87171", sub: "por litro" },
    { label: "Maior Abastecimento", valor: resumo.maior ? brl(resumo.maior.valor_total) : "—", icon: ArrowUpRight, color: "#4ade80", sub: resumo.maior?.veiculo_label.split(" · ")[0] },
    { label: "Menor Abastecimento", valor: resumo.menor ? brl(resumo.menor.valor_total) : "—", icon: ArrowDownRight, color: "#f87171", sub: resumo.menor?.motorista_label || resumo.menor?.veiculo_label.split(" · ")[0] },
    { label: "Média por Abast.", valor: brl(resumo.mediaValor), icon: DollarSign, color: "#fb923c", sub: "R$ por registro" },
    { label: "Média de KM", valor: `${num(resumo.mediaKm, 0)} km`, icon: TrendingUp, color: "#60a5fa", sub: "por abastecimento" },
    { label: "Custo por KM", valor: brl(resumo.custoPorKm), icon: DollarSign, color: "#34d399", sub: "combustível por km" },
  ];
    return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Abastecimentos"
        description="Registro detalhado com cálculo automático de KM rodados e média KM/L a partir do hodômetro."
        actions={
          <div className="flex gap-2">
            <label className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2 cursor-pointer">
              <input type="file" accept=".xls,.xlsx" onChange={handleImportXLS} className="hidden" />
              <Upload className="size-4 mr-2" /> Importar XLS
            </label>
            <label className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2 cursor-pointer">
              <input type="file" accept=".pdf" onChange={handleImportPDF} className="hidden" />
              <FileText className="size-4 mr-2" /> Importar NF
            </label>
            <Button onClick={abrirNovo}>
              <Plus className="size-4" /> Novo abastecimento
            </Button>
          </div>
        }
      />

      <div className="mb-5 grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
        {cards.map((c) => (
          <div key={c.label} className="glass lift relative overflow-hidden rounded-xl transition-all hover:scale-[1.02]" style={{ padding: '12px 16px', height: '90px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '28px', height: '28px', borderRadius: '8px', backgroundColor: `${c.color}20`, color: c.color }}>
                <c.icon size={16} />
              </div>
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
        <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
          <TrendingUp className="size-4 text-emerald-400" />
          Termômetro de Eficiência (Top 5 KM/L)
        </h3>
        <div className="space-y-2 w-full">
          {ranking.length === 0 ? (
            <p className="text-sm text-slate-500">Sem dados suficientes para calcular o ranking.</p>
          ) : (
            ranking.map((r, i) => {
              const placa = r.label.split(" ")[0];
              const percent = Math.min((r.media / 5) * 100, 100);
              const isGood = r.media >= 2.5;
              return (
                <div key={r.label} className="flex items-center gap-3 w-full">
                  <span className="w-6 text-xs text-slate-500 font-mono">{i + 1}º</span>
                  <span className="w-20 text-sm font-medium text-slate-300 font-mono" title={r.label}>{placa}</span>
                  <div className="flex-1 h-3 bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full ${isGood ? 'bg-emerald-500' : 'bg-red-500'}`} 
                      style={{ width: `${percent}%` }}
                    />
                  </div>
                  <span className="w-12 text-right text-sm font-bold text-slate-200">{num(r.media, 2)}</span>
                </div>
              );
            })
          )}
        </div>
      </div>

      <div className="mb-4 flex flex-wrap items-end gap-3">
        <div className="grid w-64 gap-1.5">
          <Label>Veículo</Label>
          <FieldSelect value={filtroVeiculo} onChange={setFiltroVeiculo} options={[{ value: TODOS, label: "Todos os veículos" }, ...veicOpts]} testId="abastecimento-filtro-veiculo" />
        </div>
        <div className="grid gap-1.5">
          <Label htmlFor="filtro-mes">Mês</Label>
          <Input id="filtro-mes" type="month" value={mes} onChange={(e) => setMes(e.target.value)} className="w-44" />
        </div>
        {(mes || filtroVeiculo !== TODOS) && (
          <Button variant="ghost" onClick={() => { setMes(""); setFiltroVeiculo(TODOS); }}>Limpar filtros</Button>
        )}
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table className="text-xs">
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {["Data", "Origem", "Veículo", "Motorista", "Litros", "R$/L", "Total", "Posto", "KM", "Rodados", "Média", "Ações"].map((h) => (
                <TableHead key={h} className="text-[10px] uppercase tracking-wider text-slate-500 whitespace-nowrap px-2 text-left">{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.length === 0 && (
              <TableRow><TableCell colSpan={12} className="py-10 text-center text-slate-500">{q.isPending ? "Carregando…" : "Nenhum abastecimento encontrado."}</TableCell></TableRow>
            )}
            {rows.map((r) => (
              <TableRow key={r.id} className="border-slate-800/70">
                <TableCell className="font-mono text-xs whitespace-nowrap px-2 text-left">{dataBR(r.data)}</TableCell>
                <TableCell className="text-center px-2">
                  {r.origem === "pdf" ? (
                    <span className="inline-flex items-center justify-center rounded bg-red-500/20 px-2 py-0.5 text-xs font-bold text-red-400" title="Importado via PDF">PDF</span>
                  ) : (
                    <span className="inline-flex items-center justify-center rounded bg-slate-500/20 px-2 py-0.5 text-xs font-bold text-slate-400" title="Inserido Manualmente">M</span>
                  )}
                </TableCell>
                <TableCell className="font-mono text-xs whitespace-nowrap px-2 text-left">{r.veiculo_label.split(" · ")[0]}</TableCell>
                <TableCell className="text-slate-300 text-xs whitespace-nowrap px-2 truncate max-w-[150px] text-left">{r.motorista_label ?? "—"}</TableCell>
                <TableCell className="tabular-nums text-xs whitespace-nowrap px-2 text-right">{num(r.litros, 1)}</TableCell>
                <TableCell className="tabular-nums text-xs whitespace-nowrap px-2 text-right">{num(r.preco_litro, 2)}</TableCell>
                <TableCell className="tabular-nums font-medium text-xs whitespace-nowrap px-2 text-right">{brl(r.valor_total)}</TableCell>
                <TableCell className="text-xs whitespace-nowrap px-2 truncate max-w-[100px] text-slate-400 text-left">{r.posto}</TableCell>
                <TableCell className="font-mono tabular-nums text-xs whitespace-nowrap px-2 text-right">{num(r.km)}</TableCell>
                <TableCell className="tabular-nums text-xs whitespace-nowrap px-2 text-right">{r.km_rodados != null ? num(r.km_rodados) : "—"}</TableCell>
                <TableCell className="tabular-nums text-xs whitespace-nowrap px-2 text-right text-sky-300">{r.media_km_l != null ? `${num(r.media_km_l, 2)}` : "—"}</TableCell>
                <TableCell className="text-center px-2">
                  <div className="flex gap-1 justify-center">
                    <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)} aria-label="Editar">
                      <Pencil className="size-4 text-sky-400" />
                    </Button>
                    {me?.perfil === "admin" && (
                      <Button size="icon-sm" variant="ghost" className="text-red-300" onClick={() => setExcluirId(r.id)} aria-label="Excluir">
                        <Trash2 className="size-4" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={(o) => { setOpen(o); if(!o) setEditingId(null); }}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Fuel className="size-5 text-sky-400" /> 
              {editingId ? "Editar abastecimento" : "Novo abastecimento"}
            </DialogTitle>
          </DialogHeader>
          <form className="grid grid-cols-2 gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            <div className="grid gap-1.5">
              <Label htmlFor="ab-data">Data *</Label>
              <Input id="ab-data" type="date" value={form.data} onChange={(e) => set("data")(e.target.value)} required />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="ab-km">Hodômetro (KM) *</Label>
              <Input id="ab-km" type="number" value={form.km} onChange={(e) => set("km")(e.target.value)} required />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Veículo *</Label>
              <FieldSelect value={form.veiculo_id} onChange={handleVeiculoChange} options={veicOpts} placeholder="Selecione o veículo" testId="abastecimento-form-veiculo" />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Motorista</Label>
              <FieldSelect
                value={form.motorista_id}
                onChange={set("motorista_id")}
                options={[{ value: NENHUM, label: "— Não informado —" }, ...(motoristas.data ?? []).filter((m: any) => m.ativo).map((m: any) => ({ value: m.id, label: m.nome }))]}
                testId="abastecimento-form-motorista"
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="ab-litros">Litros *</Label>
              <Input id="ab-litros" inputMode="decimal" value={form.litros} onChange={(e) => set("litros")(e.target.value)} required />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="ab-preco">Preço por litro (R$) *</Label>
              <Input id="ab-preco" inputMode="decimal" value={form.preco_litro} onChange={(e) => set("preco_litro")(e.target.value)} required />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor="ab-posto">Posto *</Label>
              <Input id="ab-posto" value={form.posto} onChange={(e) => set("posto")(e.target.value)} required />
            </div>
            <div className="grid gap-1.5">
              <Label>Nº NF</Label>
              <Input value={form.numero_nf} onChange={(e) => setForm(s => ({ ...s, numero_nf: e.target.value }))} placeholder="12550" />
            </div>
            <div className="grid gap-1.5">
              <Label>Hora</Label>
              <Input type="time" value={form.hora} onChange={(e) => setForm(s => ({ ...s, hora: e.target.value }))} />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Chave NF-e</Label>
              <Input value={form.chave_nfe} onChange={(e) => setForm(s => ({ ...s, chave_nfe: e.target.value }))} placeholder="3126 1020..." />
            </div>
            <div className="grid gap-1.5">
              <Label>CNPJ Emitente</Label>
              <Input value={form.cnpj} onChange={(e) => setForm(s => ({ ...s, cnpj: e.target.value }))} placeholder="00.000.000/0000-00" />
            </div>
            <div className="grid gap-1.5">
              <Label>Fornecedor</Label>
              <Input value={form.fornecedor} onChange={(e) => setForm(s => ({ ...s, fornecedor: e.target.value }))} placeholder="Posto..." />
            </div>
            <p className="col-span-2 rounded-lg bg-slate-950/60 px-3 py-2 text-sm text-slate-300">
              Valor total: <span className="font-semibold text-slate-50">{Number.isFinite(total) ? brl(total) : "—"}</span>
            </p>
            <DialogFooter className="col-span-2">
              <Button type="submit" disabled={salvar.isPending || !form.veiculo_id}>{editingId ? "Salvar Alterações" : "Registrar"}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={excluirId !== null}
        onOpenChange={(o) => !o && setExcluirId(null)}
        title="Excluir abastecimento?"
        description="Esta ação é registrada na auditoria e não pode ser desfeita."
        confirmLabel="Excluir"
        destructive
        pending={excluir.isPending}
        onConfirm={() => excluirId && excluir.mutate(excluirId)}
        testId="abastecimento-excluir"
      />
    </div>
  );
}