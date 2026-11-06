import os

# 1. CRIAR A PÁGINA DE SCANNER QR CODE
path_scanner = os.path.join(os.getcwd(), "frontend", "src", "pages", "LeitorQRCode.tsx")
conteudo_scanner = r'''import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { QrCode, ArrowLeft, Search, CheckCircle2 } from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiGet, apiPost } from "@/lib/api";
import { toast } from "sonner";

export default function LeitorQRCode() {
  const navigate = useNavigate();
  const [codigo, setCodigo] = useState("");
  const [pneu, setPneu] = useState<any>(null);
  const [sulco, setSulco] = useState("");
  const [posicao, setPosicao] = useState("");

  const buscarPneu = async () => {
    if (!codigo) return;
    try {
      const res = await apiGet<any>(`/pneus/qrcode/${codigo}`);
      setPneu(res);
      setSulco(String(res.profundidade_atual || ""));
      setPosicao(res.posicao || "");
      toast.success("Pneu localizado!");
    } catch (e: any) {
      toast.error("Pneu não encontrado.");
      setPneu(null);
    }
  };

  const salvar = async () => {
    try {
      await apiPost(`/pneus/qrcode/${codigo}/atualizar`, { 
        profundidade_atual: sulco, 
        posicao 
      });
      toast.success("Pneu atualizado com sucesso!");
      navigate("/operacao/pneus");
    } catch (e: any) {
      toast.error("Erro ao atualizar.");
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <PageHeader
        eyebrow="Mobilidade"
        title="Leitor de QR Code"
        description="Escaneie o QR Code do pneu para atualizar o sulco e a posição."
        actions={
          <Button variant="outline" onClick={() => navigate("/operacao/pneus")}>
            <ArrowLeft className="size-4 mr-2" /> Voltar
          </Button>
        }
      />

      <div className="glass p-6 rounded-2xl border border-slate-800 mb-6">
        <div className="flex gap-2">
          <Input 
            placeholder="Digite ou cole o Nº Fogo..." 
            value={codigo} 
            onChange={(e) => setCodigo(e.target.value.toUpperCase())}
            className="h-12 text-lg bg-slate-950 border-slate-700"
          />
          <Button onClick={buscarPneu} className="h-12 bg-sky-600 hover:bg-sky-500 px-6">
            <Search className="size-5 mr-2" /> Buscar
          </Button>
        </div>
        <p className="text-xs text-slate-500 mt-2 text-center">
          (Em breve, a câmera abrirá automaticamente para leitura do QR Code)
        </p>
      </div>

      {pneu && (
        <div className="glass p-6 rounded-2xl border border-emerald-500/30 bg-emerald-950/10">
          <div className="flex items-center gap-3 mb-4">
            <QrCode className="size-8 text-emerald-400" />
            <div>
              <h2 className="text-xl font-bold text-slate-100">{pneu.numero_fogo}</h2>
              <p className="text-sm text-slate-400">{pneu.marca} - {pneu.medida}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-1.5">
              <Label className="text-xs text-slate-400">Profundidade (mm)</Label>
              <Input value={sulco} onChange={(e) => setSulco(e.target.value)} type="number" className="h-10 bg-slate-950 border-slate-700" />
            </div>
            <div className="grid gap-1.5">
              <Label className="text-xs text-slate-400">Posição no Veículo</Label>
              <Input value={posicao} onChange={(e) => setPosicao(e.target.value)} className="h-10 bg-slate-950 border-slate-700" />
            </div>
          </div>

          <Button onClick={salvar} className="w-full mt-6 h-12 bg-emerald-600 hover:bg-emerald-500 text-lg">
            <CheckCircle2 className="size-5 mr-2" /> Salvar Alterações
          </Button>
        </div>
      )}
    </div>
  );
}
'''
with open(path_scanner, "w", encoding="utf-8") as f:
    f.write(conteudo_scanner)
print("✅ Página LeitorQRCode.tsx criada.")

# 2. REESCREVER A TELA DE RELATÓRIOS COM PARETO E MARCAS
path_relatorios = os.path.join(os.getcwd(), "frontend", "src", "pages", "RelatoriosPneus.tsx")
conteudo_relatorios = r'''import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { BarChart3, AlertTriangle, TrendingUp, DollarSign, Disc, ArrowRightLeft, PieChart } from "lucide-react";
import { brl } from "@/lib/format";

export default function RelatoriosPneus() {
  const { data: marcas = [] } = useQuery({ queryKey: ["relatorio-marcas"], queryFn: () => apiGet<any[]>("/pneus/relatorios/desempenho-marcas") });
  const { data: pareto = [] } = useQuery({ queryKey: ["relatorio-pareto"], queryFn: () => apiGet<any[]>("/pneus/relatorios/pareto") });
  const { data: alertas = { sulco_critico: [], na_oficina: [] } } = useQuery({ queryKey: ["relatorio-alertas"], queryFn: () => apiGet<any>("/pneus/relatorios/alertas") });
  const { data: financeiro = [] } = useQuery({ queryKey: ["relatorio-financeiro"], queryFn: () => apiGet<any[]>("/pneus/relatorios/financeiro") });

  const totalSucateados = pareto.reduce((acc: number, p: any) => acc + p.quantidade, 0);

  return (
    <div>
      <PageHeader
        eyebrow="Inteligência"
        title="Relatórios de Pneus"
        description="Análise de vida útil, custos e motivos de descarte."
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-xs uppercase text-slate-400">Sulco Crítico</p>
          <p className="text-2xl font-bold text-rose-400 mt-1">{alertas.sulco_critico.length}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-xs uppercase text-slate-400">Na Borracharia</p>
          <p className="text-2xl font-bold text-amber-400 mt-1">{alertas.na_oficina.length}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-xs uppercase text-slate-400">Total Sucateados</p>
          <p className="text-2xl font-bold text-purple-400 mt-1">{totalSucateados}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-xs uppercase text-slate-400">Investimento Total</p>
          <p className="text-xl font-bold text-emerald-400 mt-1">
            {brl(financeiro.reduce((acc: number, f: any) => acc + (f.custo_total || 0), 0))}
          </p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Desempenho por Marca */}
        <div className="glass p-6 rounded-2xl border border-slate-800">
          <h3 className="text-lg font-bold text-slate-100 mb-6 flex items-center gap-2">
            <TrendingUp className="size-5 text-emerald-400" /> Vida Útil Média por Marca (KM)
          </h3>
          <div className="space-y-4">
            {marcas.length === 0 ? (
              <p className="text-sm text-slate-500">Sem dados suficientes de pneus sucateados.</p>
            ) : (
              marcas.map((m: any, i: number) => {
                const maxKm = marcas[0].km_medio;
                const pct = (m.km_medio / maxKm) * 100;
                return (
                  <div key={i}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-slate-300 font-medium">{m.marca} ({m.total_pneus} pneus)</span>
                      <span className="text-emerald-400 font-bold">{Math.round(m.km_medio).toLocaleString('pt-BR')} km</span>
                    </div>
                    <div className="h-2.5 w-full bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-emerald-500 to-emerald-300 rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Pareto de Descarte */}
        <div className="glass p-6 rounded-2xl border border-slate-800">
          <h3 className="text-lg font-bold text-slate-100 mb-6 flex items-center gap-2">
            <PieChart className="size-5 text-amber-400" /> Motivos de Sucateamento (Pareto)
          </h3>
          <div className="space-y-3">
            {pareto.length === 0 ? (
              <p className="text-sm text-slate-500">Nenhum pneu sucateado ainda.</p>
            ) : (
              pareto.map((p: any, i: number) => {
                const pct = (p.quantidade / totalSucateados) * 100;
                return (
                  <div key={i}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-300">{p.motivo}</span>
                      <span className="text-amber-400 font-bold">{p.quantidade} un ({Math.round(pct)}%)</span>
                    </div>
                    <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-amber-500 rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
'''
with open(path_relatorios, "w", encoding="utf-8") as f:
    f.write(conteudo_relatorios)
print("✅ Página RelatoriosPneus.tsx atualizada com Pareto e Marcas.")

# 3. ADICIONAR ROTA E LINK NO MENU
app_path = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")
with open(app_path, "r", encoding="utf-8") as f:
    app_c = f.read()

if "LeitorQRCode" not in app_c:
    app_c = app_c.replace(
        'import RelatoriosPneus from "@/pages/RelatoriosPneus";',
        'import RelatoriosPneus from "@/pages/RelatoriosPneus";\nimport LeitorQRCode from "@/pages/LeitorQRCode";'
    )
    app_c = app_c.replace(
        '<Route path="/operacao/relatorios-pneus"',
        '<Route path="/operacao/pneus/scanner" element={<LeitorQRCode />} />\n              <Route path="/operacao/relatorios-pneus"'
    )
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_c)
    print("✅ Rota /operacao/pneus/scanner adicionada.")

# 4. ADICIONAR BOTÃO NO CABEÇALHO DE PNEUS
path_pneus = os.path.join(os.getcwd(), "frontend", "src", "pages", "Pneus.tsx")
with open(path_pneus, "r", encoding="utf-8") as f:
    pneus_c = f.read()

if "Scanner QR Code" not in pneus_c:
    pneus_c = pneus_c.replace(
        '<Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9">',
        '<a href="/operacao/pneus/scanner"><Button variant="outline" className="border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10 h-9 mr-2"><QrCode className="size-4 mr-2" /> Scanner QR Code</Button></a>\n            <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9">'
    )
    if "QrCode" not in pneus_c.split("from \"lucide-react\"")[0]:
        pneus_c = pneus_c.replace("import {", "import { QrCode,")
    with open(path_pneus, "w", encoding="utf-8") as f:
        f.write(pneus_c)
    print("✅ Botão 'Scanner QR Code' adicionado à tela de Pneus.")

print("✅ Tudo pronto! Faça o git push.")