import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PNEUS_FASEC2_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_chassi_mapa(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "ChassiMapa.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar imports necessários
    if 'useMutation' not in c:
        c = c.replace(
            'import { useQuery } from "@tanstack/react-query";',
            'import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";'
        )
        c = c.replace(
            'import { Disc, AlertTriangle } from "lucide-react";',
            'import { Disc, AlertTriangle, ArrowRightLeft, Trash2, RotateCcw, CheckCircle2 } from "lucide-react";'
        )

    # 2. Adicionar o estado do modal de movimentação
    if 'const [movimentacaoOpen, setMovimentacaoOpen]' not in c:
        c = c.replace(
            'const pneusDoVeiculo = pneus.filter(p =>',
            '''const qc = useQueryClient();
  const [movimentacaoOpen, setMovimentacaoOpen] = useState(false);
  const [pneuSelecionado, setPneuSelecionado] = useState<Pneu | null>(null);
  const [tipoMovimentacao, setTipoMovimentacao] = useState("RODIZIO");
  const [posicaoDestino, setPosicaoDestino] = useState("");
  const [motivo, setMotivo] = useState("");

  const movimentar = useMutation({
    mutationFn: () => apiPost("/pneu-movimentacoes", {
      pneu_id: pneuSelecionado?.id,
      tipo: tipoMovimentacao,
      veiculo_id: tipo === "cavalo" ? veiculoId : null,
      carreta_id: tipo === "carreta" ? veiculoId : null,
      posicao_origem: pneuSelecionado?.posicao,
      posicao_destino: posicaoDestino,
      motivo: motivo,
    }),
    onSuccess: () => {
      toast.success("Movimentação registrada!");
      setMovimentacaoOpen(false);
      setPneuSelecionado(null);
      qc.invalidateQueries({ queryKey: ["pneus"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const abrirMovimentacao = (pneu: Pneu) => {
    setPneuSelecionado(pneu);
    setTipoMovimentacao("RODIZIO");
    setPosicaoDestino("");
    setMotivo("");
    setMovimentacaoOpen(true);
  };

  const pneusDoVeiculo = pneus.filter(p =>''')
        print("✅ Estado e mutation de movimentação adicionados.")

    # 3. Adicionar o modal de movimentação (antes do fechamento do return)
    if 'Modal de Movimentação' not in c:
        idx = c.rfind('    </div>\n  );\n}')
        if idx != -1:
            modal = '''
      {/* Modal de Movimentação */}
      {movimentacaoOpen && pneuSelecionado && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">Movimentar Pneu: {pneuSelecionado.numero_fogo}</h2>
            
            <div className="grid gap-4">
              <div className="grid gap-1.5">
                <label className="text-xs text-slate-400">Tipo de Movimentação</label>
                <select value={tipoMovimentacao} onChange={(e) => setTipoMovimentacao(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                  <option value="RODIZIO">Rodízio (Trocar de Posição)</option>
                  <option value="RECAPAGEM">Enviar para Recapagem</option>
                  <option value="CONSERTO">Enviar para Conserto</option>
                  <option value="DESCARTE">Descartar (Sucata)</option>
                </select>
              </div>

              {tipoMovimentacao === "RODIZIO" && (
                <div className="grid gap-1.5">
                  <label className="text-xs text-slate-400">Nova Posição</label>
                  <Input value={posicaoDestino} onChange={(e) => setPosicaoDestino(e.target.value)} placeholder="Ex: 3-DE" />
                </div>
              )}

              {tipoMovimentacao === "DESCARTE" && (
                <div className="grid gap-1.5">
                  <label className="text-xs text-slate-400">Motivo do Descarte</label>
                  <Input value={motivo} onChange={(e) => setMotivo(e.target.value)} placeholder="Ex: Bolha lateral, desgaste irregular..." />
                </div>
              )}
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setMovimentacaoOpen(false)}>Cancelar</Button>
              <Button onClick={() => movimentar.mutate()} disabled={movimentar.isPending}>
                {movimentar.isPending ? "Registrando..." : "Confirmar"}
              </Button>
            </div>
          </div>
        </div>
      )}
'''
            c = c[:idx] + modal + c[idx:]
            print("✅ Modal de Movimentação adicionado.")

    # 4. Adicionar o botão de ação rápida no card do pneu (ao clicar no pneu)
    if 'onClick={() => abrirMovimentacao(pneu)}' not in c:
        c = c.replace(
            'className={`size-12 rounded-lg border-2 flex flex-col items-center justify-center transition-all cursor-pointer ${getCorSulco(pneu.sulco_atual)} hover:scale-110`}',
            'className={`size-12 rounded-lg border-2 flex flex-col items-center justify-center transition-all cursor-pointer ${getCorSulco(pneu.sulco_atual)} hover:scale-110`} onClick={() => abrirMovimentacao(pneu)}'
        )
        print("✅ Botão de ação rápida adicionado ao card do pneu.")

    # 5. Garantir imports de useState, toast, apiPost, Input, Button
    if 'useState' not in c:
        c = 'import { useState } from "react";\n' + c
    if 'toast' not in c:
        c = 'import { toast } from "sonner";\n' + c
    if 'apiPost' not in c:
        c = 'import { apiPost } from "@/lib/api";\n' + c
    if 'Input' not in c:
        c = 'import { Input } from "@/components/ui/input";\n' + c
    if 'Button' not in c:
        c = 'import { Button } from "@/components/ui/button";\n' + c

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ ChassiMapa.tsx atualizado com o modal de movimentação.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_chassi_mapa(raiz)
    print("\n✅ Fase C.2 (Modal de Movimentação) aplicada com sucesso!")