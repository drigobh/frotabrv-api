import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PNEUS_ABAS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Pneus.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def recriar(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    
    codigo = '''import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, Disc, Search, AlertTriangle, RefreshCw, ArrowRightLeft, ShieldAlert } from "lucide-react";
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
import { useVeiculos } from "@/hooks/useCadastros";

const STATUS_PNEU = ["Estoque", "Aplicado", "Recapagem", "Conserto", "Sucateado"];
const TIPOS_PNEU = ["Direcional", "Tração", "Misto"];

export default function Pneus() {
  const qc = useQueryClient();
  const veiculos = useVeiculos();
  const [abaAtiva, setAbaAtiva] = useState("cadastrados");
  
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const [filtro, setFiltro] = useState("");

  // Estados do Mapa
  const [tipoAtivo, setTipoAtivo] = useState<"cavalo" | "carreta">("cavalo");
  const [veiculoMapa, setVeiculoMapa] = useState<string>("");
  const [buscaPlaca, setBuscaPlaca] = useState("");

  const { data: pneus = [] } = useQuery({ queryKey: ["pneus"], queryFn: () => apiGet<any[]>("/pneus") });
  const { data: carretas = [] } = useQuery({ queryKey: ["carretas"], queryFn: () => apiGet<any[]>("/carretas") });

  const [form, setForm] = useState({
    numero_fogo: "", marca: "", modelo: "", medida: "", dot: "", tipo: "Tração", status: "Estoque", custo_aquisicao: "", observacoes: ""
  });

  // Estatísticas para os Cards
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

    return { total, sucateados, emManutencao, topMarcas, emEstoque };
  }, [pneus]);

  // Filtro de veículos para o mapa
  const veiculosFiltrados = useMemo(() => {
    const lista = tipoAtivo === "cavalo" 
      ? (veiculos.data ?? []).map((v: any) => ({ id: v.id, label: `${v.placa} - ${v.modelo}`, template_chassi_id: v.template_chassi_id }))
      : carretas.map((c: any) => ({ id: c.id, label: `${c.codigo} - ${c.tipo}`, template_chassi_id: c.template_chassi_id }));

    if (!buscaPlaca) return lista;
    return lista.filter((v: any) => v.label.toLowerCase().includes(buscaPlaca.toLowerCase()));
  }, [veiculos.data, carretas, tipoAtivo, buscaPlaca]);

  // Veículo selecionado (busca na lista completa)
  const veiculoSelecionado = 
    tipoAtivo === "cavalo" 
      ? veiculos.data?.find((v: any) => v.id === veiculoMapa)
      : carretas.find((c: any) => c.id === veiculoMapa);

  // Mutations
  const salvar = useMutation({
    mutationFn: () => {
      const payload = { ...form, custo_aquisicao: Number(String(form.custo_aquisicao).replace(",", ".")) || 0 };
      return editingId ? apiPut(`/pneus/${editingId}`, payload) : apiPost("/pneus", payload);
    },
    onSuccess: () => { toast.success("Pneu salvo!"); setOpen(false); qc.invalidateQueries({ queryKey: ["pneus"] }); },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/pneus/${id}`),
    onSuccess: () => { toast.success("Pneu excluído."); setExcluirId(null); qc.invalidateQueries({ queryKey: ["pneus"] }); }
  });

  const movimentar = useMutation({
    mutationFn: ({ pneu_id, tipo }: { pneu_id: string, tipo: string }) => {
      return apiPost("/pneu-movimentacoes", {
        pneu_id,
        tipo,
        motivo: tipo === "DESCARTE" ? "Descarte via Estoque" : null,
      });
    },
    onSuccess: () => {
      toast.success("Movimentação registrada!");
      qc.invalidateQueries({ queryKey: ["pneus"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const abrirNovo = () => { setEditingId(null); setForm({ numero_fogo: "", marca: "", modelo: "", medida: "", dot: "", tipo: "Tração", status: "Estoque", custo_aquisicao: "", observacoes: "" }); setOpen(true); };
  const abrirEdicao = (r: any) => { setEditingId(r.id); setForm({ ...r, custo_aquisicao: String(r.custo_aquisicao || "") }); setOpen(true); };

  const pneusFiltrados = pneus.filter((p: any) => {
    if (!filtro) return true;
    return p.numero_fogo.toLowerCase().includes(filtro.toLowerCase()) || p.marca.toLowerCase().includes(filtro.toLowerCase());
  });

  const statusColor = (status: string) => {
    if (status === "Estoque") return "bg-sky-500/20 text-sky-400";
    if (status === "Aplicado") return "bg-emerald-500/20 text-emerald-400";
    if (status === "Recapagem") return "bg-amber-500/20 text-amber-400";
    if (status === "Sucateado") return "bg-rose-500/20 text-rose-400";
    return "bg-slate-800 text-slate-400";
  };

  return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Controle de Pneus"
        description="Gestão de pneus por número de fogo, marca, DOT e status."
        actions={<Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Novo Pneu</Button>}
      />

      {/* Cards de KPI */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 mb-6">
        <div className="glass p-4 rounded-xl flex justify-between items-center">
          <div><p className="text-xs uppercase text-slate-400">Total de Pneus</p><p className="text-2xl font-bold text-slate-100">{stats.total}</p></div>
          <div className="p-2 bg-sky-500/10 rounded-lg"><Disc className="size-5 text-sky-400" /></div>
        </div>
        <div className="glass p-4 rounded-xl flex justify-between items-center">
          <div><p className="text-xs uppercase text-slate-400">Sucateados</p><p className="text-2xl font-bold text-rose-400">{stats.sucateados}</p></div>
          <div className="p-2 bg-rose-500/10 rounded-lg"><Trash2 className="size-5 text-rose-400" /></div>
        </div>
        <div className="glass p-4 rounded-xl flex justify-between items-center">
          <div><p className="text-xs uppercase text-slate-400">Em Manutenção</p><p className="text-2xl font-bold text-amber-400">{stats.emManutencao}</p></div>
          <div className="p-2 bg-amber-500/10 rounded-lg"><AlertTriangle className="size-5 text-amber-400" /></div>
        </div>
        <div className="glass p-4 rounded-xl flex flex-col justify-center">
          <p className="text-xs uppercase text-slate-400 mb-2">Top Marcas</p>
          <div className="space-y-1">
            {stats.topMarcas.map(([marca, qtd]: any, i: number) => (
              <div key={i} className="flex justify-between text-xs">
                <span className="text-slate-300 truncate">{marca}</span>
                <span className="text-sky-400 font-bold">{qtd}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Navegação por Abas */}
      <div className="flex gap-2 mb-4 border-b border-slate-800 pb-2">
        <button 
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${abaAtiva === 'cadastrados' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`}
          onClick={() => setAbaAtiva('cadastrados')}
        >
          <Disc className="size-4 inline mr-2" /> Pneus Cadastrados
        </button>
        <button 
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${abaAtiva === 'movimentacao' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`}
          onClick={() => setAbaAtiva('movimentacao')}
        >
          <ArrowRightLeft className="size-4 inline mr-2" /> Movimentação (Chassi)
        </button>
        <button 
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${abaAtiva === 'estoque' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`}
          onClick={() => setAbaAtiva('estoque')}
        >
          <RefreshCw className="size-4 inline mr-2" /> Estoque / Sucata
        </button>
      </div>

      {/* Aba 1: Pneus Cadastrados */}
      {abaAtiva === "cadastrados" && (
        <div>
          <div className="mb-4 flex gap-2">
            <div className="relative w-72">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
              <Input placeholder="Buscar por número de fogo ou marca..." value={filtro} onChange={(e) => setFiltro(e.target.value)} className="pl-9 h-9" />
            </div>
          </div>

          <div className="glass overflow-hidden rounded-2xl">
            <Table>
              <TableHeader>
                <TableRow className="border-slate-800">
                  <TableHead className="text-xs uppercase text-slate-500">Nº Fogo</TableHead>
                  <TableHead className="text-xs uppercase text-slate-500">Marca / Modelo</TableHead>
                  <TableHead className="text-xs uppercase text-slate-500">Medida</TableHead>
                  <TableHead className="text-xs uppercase text-slate-500">DOT</TableHead>
                  <TableHead className="text-xs uppercase text-slate-500">Tipo</TableHead>
                  <TableHead className="text-xs uppercase text-slate-500">Status</TableHead>
                  <TableHead className="text-xs uppercase text-slate-500">Custo</TableHead>
                  <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pneusFiltrados.length === 0 ? (
                  <TableRow><TableCell colSpan={8} className="text-center py-8 text-slate-500">Nenhum pneu cadastrado.</TableCell></TableRow>
                ) : (
                  pneusFiltrados.map((p: any) => (
                    <TableRow key={p.id} className="border-slate-800 hover:bg-slate-800/30">
                      <TableCell className="font-bold text-slate-100">{p.numero_fogo}</TableCell>
                      <TableCell className="text-slate-300">{p.marca} {p.modelo && `/ ${p.modelo}`}</TableCell>
                      <TableCell className="text-slate-400 font-mono">{p.medida}</TableCell>
                      <TableCell className="text-slate-400">{p.dot || "—"}</TableCell>
                      <TableCell className="text-slate-400">{p.tipo}</TableCell>
                      <TableCell><span className={`px-2 py-0.5 rounded text-[10px] font-bold ${statusColor(p.status)}`}>{p.status}</span></TableCell>
                      <TableCell className="text-amber-400 font-mono">{brl(p.custo_aquisicao)}</TableCell>
                      <TableCell className="text-center">
                        <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(p)}><Pencil className="size-4 text-sky-400" /></Button>
                        <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(p.id)}><Trash2 className="size-4 text-red-300" /></Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </div>
      )}

      {/* Aba 2: Movimentação (Chassi) */}
      {abaAtiva === "movimentacao" && (
        <div>
          <div className="flex items-center gap-4 mb-4 flex-wrap">
            <h3 className="text-lg font-bold text-slate-100">Chassi do Veículo</h3>
            
            <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-700">
              <button className={`px-3 py-1 text-sm rounded-md font-medium ${tipoAtivo === 'cavalo' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => { setTipoAtivo('cavalo'); setVeiculoMapa(''); }}>Cavalo</button>
              <button className={`px-3 py-1 text-sm rounded-md font-medium ${tipoAtivo === 'carreta' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => { setTipoAtivo('carreta'); setVeiculoMapa(''); }}>Carreta</button>
            </div>

            <div className="relative w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
              <Input placeholder={tipoAtivo === 'cavalo' ? "Buscar por placa..." : "Buscar por código..."} value={buscaPlaca} onChange={(e) => setBuscaPlaca(e.target.value)} className="pl-9 h-9" />
            </div>

            <select value={veiculoMapa} onChange={(e) => setVeiculoMapa(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3 min-w-[200px]">
              <option value="">Selecione...</option>
              {veiculosFiltrados.map((v: any) => (
                <option key={v.id} value={v.id}>{v.label}</option>
              ))}
            </select>
          </div>

          {veiculoMapa ? (
            <ChassiMapa 
              pneus={pneus} 
              veiculoId={veiculoMapa} 
              tipo={tipoAtivo} 
              templateChassiId={veiculoSelecionado?.template_chassi_id} 
            />
          ) : (
            <div className="glass p-6 rounded-2xl text-center text-slate-500">
              <p className="text-sm">Selecione um veículo acima para visualizar o chassi.</p>
            </div>
          )}
        </div>
      )}

      {/* Aba 3: Estoque / Sucata */}
      {abaAtiva === "estoque" && (
        <div>
          <div className="glass p-6 rounded-2xl">
            <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
              <RefreshCw className="size-5 text-sky-400" /> Pneus em Estoque para Recapagem / Sucata
            </h3>
            
            {stats.emEstoque.length === 0 ? (
              <div className="text-center py-8 text-slate-500">Nenhum pneu em estoque no momento.</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {stats.emEstoque.map((p: any) => (
                  <div key={p.id} className="glass p-4 rounded-xl border border-sky-500/30">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm font-bold text-sky-400">{p.numero_fogo}</p>
                        <p className="text-xs text-slate-300">{p.marca} - {p.medida}</p>
                        <p className="text-[10px] text-slate-500">DOT: {p.dot || "—"} | Sulco: {p.sulco_atual || "—"} mm</p>
                      </div>
                      <span className="text-xs font-mono text-amber-400">{brl(p.custo_aquisicao)}</span>
                    </div>
                    <div className="mt-3 flex gap-2">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="flex-1 text-xs border-amber-500/40 text-amber-400 hover:bg-amber-500/10"
                        onClick={() => movimentar.mutate({ pneu_id: p.id, tipo: "RECAPAGEM" })}
                        disabled={movimentar.isPending}
                      >
                        <RefreshCw className="size-3 mr-1" /> Recapagem
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="flex-1 text-xs border-rose-500/40 text-rose-400 hover:bg-rose-500/10"
                        onClick={() => {
                          if (confirm("Descartar este pneu como sucata?")) {
                            movimentar.mutate({ pneu_id: p.id, tipo: "DESCARTE" });
                          }
                        }}
                        disabled={movimentar.isPending}
                      >
                        <ShieldAlert className="size-3 mr-1" /> Sucatear
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modal de Cadastro/Edição */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-2xl p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">{editingId ? "Editar Pneu" : "Novo Pneu"}</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Número de Fogo *</Label><Input value={form.numero_fogo} onChange={(e) => setForm(s => ({ ...s, numero_fogo: e.target.value }))} placeholder="Ex: FOG-10492" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Marca *</Label><Input value={form.marca} onChange={(e) => setForm(s => ({ ...s, marca: e.target.value }))} placeholder="Ex: Michelin" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Modelo</Label><Input value={form.modelo} onChange={(e) => setForm(s => ({ ...s, modelo: e.target.value }))} placeholder="Ex: X Multi Z" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Medida *</Label><Input value={form.medida} onChange={(e) => setForm(s => ({ ...s, medida: e.target.value }))} placeholder="Ex: 295/80 R22.5" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">DOT (Semana/Ano)</Label><Input value={form.dot} onChange={(e) => setForm(s => ({ ...s, dot: e.target.value }))} placeholder="Ex: 4523" maxLength={4} /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Tipo</Label><FieldSelect value={form.tipo} onChange={(v) => setForm(s => ({ ...s, tipo: v }))} options={TIPOS_PNEU.map(t => ({ value: t, label: t }))} /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Status</Label><FieldSelect value={form.status} onChange={(v) => setForm(s => ({ ...s, status: v }))} options={STATUS_PNEU.map(s => ({ value: s, label: s }))} /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Custo de Aquisição (R$)</Label><Input value={form.custo_aquisicao} onChange={(e) => setForm(s => ({ ...s, custo_aquisicao: e.target.value }))} placeholder="0,00" /></div>
              <div className="col-span-2 grid gap-1.5"><Label className="text-xs text-slate-400">Observações</Label><Input value={form.observacoes} onChange={(e) => setForm(s => ({ ...s, observacoes: e.target.value }))} placeholder="Ex: Comprado na loja X" /></div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
              <Button onClick={() => salvar.mutate()} disabled={salvar.isPending}>{salvar.isPending ? "Salvando..." : "Salvar"}</Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Exclusão */}
      {excluirId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-sm p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-2">Excluir Pneu?</h2>
            <div className="flex justify-end gap-3 mt-4">
              <Button variant="outline" onClick={() => setExcluirId(null)}>Cancelar</Button>
              <Button variant="destructive" onClick={() => excluirId && excluir.mutate(excluirId)}>Excluir</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Pneus.tsx recriado com as 3 abas.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    recriar(raiz)
    print("\n✅ Script aplicado com sucesso!")