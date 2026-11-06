import { useState } from "react";
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
