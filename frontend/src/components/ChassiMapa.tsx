import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Disc, AlertTriangle, Plus } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface Pneu {
  id: string;
  numero_fogo: string;
  marca: string;
  medida: string;
  status: string;
  veiculo_id?: string;
  carreta_id?: string;
  posicao?: string;
  sulco_atual?: number;
  pressao_atual?: number;
}

interface ChassiMapaProps {
  pneus: Pneu[];
  veiculoId: string;
  tipo: "cavalo" | "carreta";
  templateChassiId?: string | null;
}

export function ChassiMapa({ pneus, veiculoId, tipo, templateChassiId }: ChassiMapaProps) {
  const qc = useQueryClient();

  // Buscar template de chassi
  const { data: template } = useQuery({
    queryKey: ["chassi-template", templateChassiId],
    queryFn: () => apiGet<any>(`/chassi-templates/${templateChassiId}`),
    enabled: !!templateChassiId,
  });

  // Buscar motivos de descarte
  const { data: pneusEstoque = [] } = useQuery({ 
    queryKey: ["pneus-estoque"], 
    queryFn: () => apiGet<any[]>("/pneus") 
  });

  const { data: motivosDescarte = [] } = useQuery({
    queryKey: ["motivos-descarte"],
    queryFn: () => apiGet<any[]>("/pneu-movimentacoes/motivos-descarte"),
  });

  // Estados do modal
  const [movimentacaoOpen, setMovimentacaoOpen] = useState(false);
  const [posicaoVazia, setPosicaoVazia] = useState<string | null>(null);
  const [pneuEstoqueSelecionado, setPneuEstoqueSelecionado] = useState<string>("");
  const [pneuSelecionado, setPneuSelecionado] = useState<Pneu | null>(null);
  const [tipoMovimentacao, setTipoMovimentacao] = useState("RODIZIO");
  const [posicaoDestino, setPosicaoDestino] = useState("");
  const [motivoDescarte, setMotivoDescarte] = useState("");
  const [observacoes, setObservacoes] = useState("");

  const pneusDoVeiculo = pneus.filter(p => 
    tipo === "cavalo" ? p.veiculo_id === veiculoId : p.carreta_id === veiculoId
  );

  const getPneu = (posicao: string) => {
    return pneusDoVeiculo.find(p => p.posicao === posicao);
  };

  const getCorSulco = (sulco?: number) => {
    if (!sulco) return "bg-slate-800 border-slate-700 text-slate-500";
    if (sulco <= 1.6) return "bg-black border-black text-white";
    if (sulco <= 3.0) return "bg-rose-500/20 border-rose-500 text-rose-400";
    if (sulco <= 5.9) return "bg-amber-500/20 border-amber-500 text-amber-400";
    return "bg-emerald-500/20 border-emerald-500 text-emerald-400";
  };

  const abrirMovimentacao = (pneu: Pneu) => {
    setPneuSelecionado(pneu);
    setTipoMovimentacao("RODIZIO");
    setPosicaoDestino("");
    setMotivoDescarte("");
    setObservacoes("");
    setMovimentacaoOpen(true);
  };

  const aplicarPneu = useMutation({
    mutationFn: () => apiPost("/pneu-movimentacoes", {
      pneu_id: pneuEstoqueSelecionado,
      tipo: "APLICACAO",
      veiculo_id: tipo === "cavalo" ? veiculoId : null,
      carreta_id: tipo === "carreta" ? veiculoId : null,
      posicao_destino: posicaoVazia,
    }),
    onSuccess: () => {
      toast.success("Pneu aplicado com sucesso!");
      setPosicaoVazia(null);
      setPneuEstoqueSelecionado("");
      qc.invalidateQueries({ queryKey: ["pneus"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro ao aplicar pneu.")
  });

  const movimentar = useMutation({
    mutationFn: () => {
      // Validações básicas
      if (tipoMovimentacao === "RODIZIO" && !posicaoDestino) {
        throw new Error("Informe a nova posição para o rodízio.");
      }
      if (tipoMovimentacao === "DESCARTE" && !motivoDescarte) {
        throw new Error("Selecione o motivo do descarte.");
      }
      
      return apiPost("/pneu-movimentacoes", {
        pneu_id: pneuSelecionado?.id,
        tipo: tipoMovimentacao,
        veiculo_id: tipo === "cavalo" ? veiculoId : null,
        carreta_id: tipo === "carreta" ? veiculoId : null,
        posicao_origem: pneuSelecionado?.posicao,
        posicao_destino: posicaoDestino || null,
        motivo: motivoDescarte || null,
        observacoes: observacoes || null,
      });
    },
    onSuccess: () => {
      toast.success("Movimentação registrada com sucesso!");
      setMovimentacaoOpen(false);
      setPneuSelecionado(null);
      qc.invalidateQueries({ queryKey: ["pneus"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro ao registrar movimentação.")
  });

  const renderCardPneu = (posicao: string, label: string) => {
    const pneu = getPneu(posicao);
    
    if (!pneu) {
      return (
        <div className="flex flex-col items-center gap-1 group relative">
          <div 
            className="size-12 rounded-lg border-2 border-dashed border-slate-700 flex items-center justify-center text-slate-600 cursor-pointer hover:border-sky-500 hover:text-sky-400 transition-colors"
            onClick={() => setPosicaoVazia(posicao)}
          >
            <Plus className="size-5" />
          </div>
          <span className="text-[9px] text-slate-600">{label}</span>
        </div>
      );
    }

    return (
      <div className="flex flex-col items-center gap-1 group relative">
        <div 
          className={`size-12 rounded-lg border-2 flex flex-col items-center justify-center transition-all cursor-pointer ${getCorSulco(pneu.sulco_atual)} hover:scale-110`}
          onClick={() => abrirMovimentacao(pneu)}
        >
          <span className="text-[10px] font-bold">{pneu.numero_fogo.slice(0, 6)}</span>
          <span className="text-[8px] opacity-70">{pneu.sulco_atual ? `${pneu.sulco_atual}mm` : "—"}</span>
        </div>
        <span className="text-[9px] text-slate-500">{label}</span>
        
        {/* Tooltip */}
        <div className="absolute bottom-full mb-2 hidden group-hover:block w-40 bg-slate-800 border border-slate-700 rounded-lg p-2 text-xs z-50 shadow-xl">
          <p className="font-bold text-slate-200">{pneu.numero_fogo}</p>
          <p className="text-slate-400">{pneu.marca} - {pneu.medida}</p>
          <p className="text-slate-400">Sulco: {pneu.sulco_atual || "—"} mm</p>
          <p className="text-slate-400">Pressão: {pneu.pressao_atual || "—"} psi</p>
          <p className="text-[10px] text-sky-400 mt-1">Clique para movimentar</p>
        </div>
      </div>
    );
  };

  // Se não houver template, exibe mensagem
  if (!templateChassiId || !template) {
    return (
      <div className="glass p-6 rounded-2xl text-center text-slate-500">
        <AlertTriangle className="size-8 mx-auto mb-2" />
        <p className="text-sm">Nenhum template de chassi vinculado a este {tipo}. Edite o cadastro para vincular.</p>
      </div>
    );
  }

  const eixos = template.eixos || [];
  const estepes = template.qtd_estepes || 0;

  return (
    <div className="glass p-6 rounded-2xl">
      <h3 className="text-sm font-bold text-slate-300 mb-4 flex items-center gap-2">
        <Disc className="size-4 text-sky-400" /> Chassi do {tipo === "cavalo" ? "Cavalo" : "Carreta"} ({template.nome})
      </h3>
      
      <div className="flex flex-col gap-4">
        {eixos.map((eixo: any, idx: number) => {
          const eixoNum = idx + 1;
          const isDupla = eixo.tipo_rodagem === "DUPLA";
          
          return (
            <div key={idx} className={`flex justify-between items-center px-8 ${idx > 0 ? 'border-t border-slate-800 pt-4' : ''}`}>
              <div className="flex gap-1">
                {isDupla ? (
                  <>
                    {renderCardPneu(`${eixoNum}-EI`, `${eixoNum}-EI`)}
                    {renderCardPneu(`${eixoNum}-EE`, `${eixoNum}-EE`)}
                  </>
                ) : (
                  renderCardPneu(`${eixoNum}-E`, `${eixoNum}-E`)
                )}
              </div>
              <div className="text-[10px] text-slate-500 font-bold uppercase text-center">
                Eixo {eixoNum} ({eixo.funcao_mecanica})
                {eixo.tem_suspensor && <span className="block text-[8px] text-emerald-400">Suspensor</span>}
              </div>
              <div className="flex gap-1">
                {isDupla ? (
                  <>
                    {renderCardPneu(`${eixoNum}-DI`, `${eixoNum}-DI`)}
                    {renderCardPneu(`${eixoNum}-DE`, `${eixoNum}-DE`)}
                  </>
                ) : (
                  renderCardPneu(`${eixoNum}-D`, `${eixoNum}-D`)
                )}
              </div>
            </div>
          );
        })}

        {estepes > 0 && (
          <div className="border-t border-slate-800 pt-4 mt-2">
            <div className="flex justify-center gap-4">
              {Array.from({ length: estepes }).map((_, idx) => (
                <div key={idx} className="flex flex-col items-center">
                  {renderCardPneu(`EST-${idx + 1}`, `EST-${idx + 1}`)}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      
      {/* Modal de Aplicação de Pneu */}
      {posicaoVazia && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">Aplicar Pneu na Posição {posicaoVazia}</h2>
            
            <div className="grid gap-4">
              <div className="grid gap-1.5">
                <label className="text-xs text-slate-400">Selecione um pneu do Estoque</label>
                <select 
                  value={pneuEstoqueSelecionado} 
                  onChange={(e) => setPneuEstoqueSelecionado(e.target.value)} 
                  className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2"
                >
                  <option value="">Selecione...</option>
                  {pneusEstoque.filter((p: any) => p.status === "Estoque" || p.status === "Conserto").map((p: any) => (
                    <option key={p.id} value={p.id}>{p.numero_fogo} - {p.marca} ({p.medida})</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setPosicaoVazia(null)}>Cancelar</Button>
              <Button onClick={() => aplicarPneu.mutate()} disabled={aplicarPneu.isPending || !pneuEstoqueSelecionado}>
                {aplicarPneu.isPending ? "Aplicando..." : "Confirmar Aplicação"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Movimentação */}
      {movimentacaoOpen && pneuSelecionado && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">Movimentar Pneu: {pneuSelecionado.numero_fogo}</h2>
            
            <div className="grid gap-4">
              <div className="grid gap-1.5">
                <label className="text-xs text-slate-400">Tipo de Movimentação</label>
                <select 
                  value={tipoMovimentacao} 
                  onChange={(e) => setTipoMovimentacao(e.target.value)} 
                  className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2"
                >
                  <option value="RODIZIO">Rodízio (Trocar de Posição)</option>
                  <option value="RECAPAGEM">Enviar para Recapagem</option>
                  <option value="CONSERTO">Enviar para Conserto</option>
                  <option value="DESCARTE">Descartar (Sucata)</option>
                </select>
              </div>

              {tipoMovimentacao === "RODIZIO" && (
                <div className="grid gap-1.5">
                  <label className="text-xs text-slate-400">Nova Posição *</label>
                  <Input 
                    value={posicaoDestino} 
                    onChange={(e) => setPosicaoDestino(e.target.value)} 
                    placeholder="Ex: 3-DE" 
                    className="h-9"
                  />
                  <p className="text-[10px] text-slate-500">Posição atual: {pneuSelecionado.posicao || "—"}</p>
                </div>
              )}

              {tipoMovimentacao === "DESCARTE" && (
                <div className="grid gap-1.5">
                  <label className="text-xs text-slate-400">Motivo do Descarte *</label>
                  <select 
                    value={motivoDescarte} 
                    onChange={(e) => setMotivoDescarte(e.target.value)} 
                    className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2"
                  >
                    <option value="">Selecione o motivo...</option>
                    {motivosDescarte.map((m: any) => (
                      <option key={m.codigo} value={m.codigo}>{m.codigo} - {m.descricao}</option>
                    ))}
                  </select>
                </div>
              )}

              <div className="grid gap-1.5">
                <label className="text-xs text-slate-400">Observações</label>
                <Input 
                  value={observacoes} 
                  onChange={(e) => setObservacoes(e.target.value)} 
                  placeholder="Informações adicionais..." 
                  className="h-9"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setMovimentacaoOpen(false)}>Cancelar</Button>
              <Button onClick={() => movimentar.mutate()} disabled={movimentar.isPending}>
                {movimentar.isPending ? "Registrando..." : "Confirmar Movimentação"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
