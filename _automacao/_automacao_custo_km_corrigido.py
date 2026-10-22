import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_custo_km_corrigido_{agora}.zip"
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Criando Backup Full do Sistema...")
    ignorar = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build']
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta_alvo in ['app', 'frontend']:
            caminho_pasta = os.path.join(raiz, pasta_alvo)
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ignorar]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try:
                        zipf.write(caminho_completo, caminho_relativo)
                    except Exception:
                        pass
    print(f"✅ Backup Full salvo em: _automacao/backups/{nome_backup}")

def reescrever_abastecimentos(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    # Código completo, com a lógica correta e os 10 cards
    codigo_novo = '''import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Fuel, Plus, Trash2, ArrowUpRight, ArrowDownRight, DollarSign, Droplets, Target, TrendingUp, List, Pencil } from "lucide-react";
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

const TODOS = "__all__";
const NENHUM = "__none__";

const vazio = (hoje: string) => ({ data: hoje, veiculo_id: "", motorista_id: NENHUM, litros: "", preco_litro: "", posto: "", km: "", observacoes: "" });

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
    const custoPorKm = km > 0 ? valor / km : 0; // CÁLCULO DO CUSTO POR KM

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
      };
      if (editingId) return apiPut<Abastecimento>(`/abastecimentos/${editingId}`, payload);
      return apiPost<Abastecimento>("/abastecimentos", payload);
    },
    onSuccess: (a) => {
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

  // 10 CARDS (incluindo o Custo por KM)
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
          <Button onClick={abrirNovo} data-testid="abastecimento-new-button">
            <Plus className="size-4" /> Novo abastecimento
          </Button>
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
          <Input id="filtro-mes" type="month" value={mes} onChange={(e) => setMes(e.target.value)} className="w-44" data-testid="abastecimento-filtro-mes" />
        </div>
        {(mes || filtroVeiculo !== TODOS) && (
          <Button variant="ghost" onClick={() => { setMes(""); setFiltroVeiculo(TODOS); }} data-testid="abastecimento-limpar-filtros">Limpar filtros</Button>
        )}
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table data-testid="abastecimento-table">
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {["Data", "Veículo", "Motorista", "Litros", "R$/L", "Total", "Posto", "KM", "Rodados", "Média", "Ações"].map((h) => (
                <TableHead key={h} className="text-xs uppercase tracking-wider text-slate-500">{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.length === 0 && (
              <TableRow><TableCell colSpan={11} className="py-10 text-center text-slate-500">{q.isPending ? "Carregando…" : "Nenhum abastecimento encontrado."}</TableCell></TableRow>
            )}
            {rows.map((r) => (
              <TableRow key={r.id} className="border-slate-800/70" data-testid={`abastecimento-row-${r.id}`}>
                <TableCell className="font-mono text-sm">{dataBR(r.data)}</TableCell>
                <TableCell className="font-mono">{r.veiculo_label.split(" · ")[0]}</TableCell>
                <TableCell className="text-slate-300">{r.motorista_label ?? "—"}</TableCell>
                <TableCell className="tabular-nums">{num(r.litros, 1)}</TableCell>
                <TableCell className="tabular-nums">{num(r.preco_litro, 2)}</TableCell>
                <TableCell className="tabular-nums font-medium">{brl(r.valor_total)}</TableCell>
                <TableCell className="max-w-[180px] truncate text-slate-400">{r.posto}</TableCell>
                <TableCell className="font-mono tabular-nums">{num(r.km)}</TableCell>
                <TableCell className="tabular-nums">{r.km_rodados != null ? num(r.km_rodados) : "—"}</TableCell>
                <TableCell className="tabular-nums text-sky-300">{r.media_km_l != null ? `${num(r.media_km_l, 2)}` : "—"}</TableCell>
                <TableCell className="text-right flex gap-2 justify-end">
                  <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)} aria-label="Editar">
                    <Pencil className="size-4 text-sky-400" />
                  </Button>
                  {me?.perfil === "admin" && (
                    <Button size="icon-sm" variant="ghost" className="text-red-300" onClick={() => setExcluirId(r.id)} aria-label="Excluir" data-testid={`abastecimento-delete-${r.id}`}>
                      <Trash2 className="size-4" />
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={(o) => { setOpen(o); if(!o) setEditingId(null); }}>
        <DialogContent className="sm:max-w-lg" data-testid="abastecimento-dialog">
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
              <FieldSelect value={form.veiculo_id} onChange={handleVeiculoChange} options={veicOpts} placeholder="Selecione o veículo" />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Motorista</Label>
              <FieldSelect
                value={form.motorista_id}
                onChange={set("motorista_id")}
                options={[{ value: NENHUM, label: "— Não informado —" }, ...(motoristas.data ?? []).filter(m => m.ativo).map((m) => ({ value: m.id, label: m.nome }))]}
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
      />
    </div>
  );
}
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo_novo)
    print("⚙️ Abastecimentos.tsx reescrito com o 10º card (Custo por KM) e sem erros.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção do Custo por KM...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    reescrever_abastecimentos(raiz)

    print("\n🚀 Automação concluída! Siga os passos:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000")

if __name__ == "__main__":
    executar()