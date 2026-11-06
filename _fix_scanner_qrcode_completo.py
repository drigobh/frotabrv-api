import os

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "LeitorQRCode.tsx")

conteudo = r'''import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { QrCode, ArrowLeft, Search, CheckCircle2, AlertTriangle, Truck, Disc, MapPin } from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiGet, apiPost } from "@/lib/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export default function LeitorQRCode() {
  const navigate = useNavigate();
  const [codigo, setCodigo] = useState("");
  const [pneu, setPneu] = useState<any>(null);
  
  // Estados do Formulário
  const [sulco, setSulco] = useState("");
  const [odometro, setOdometro] = useState("");
  const [naoConformidade, setNaoConformidade] = useState(false);
  const [veiculo, setVeiculo] = useState<any>(null);
  const [ultimoKm, setUltimoKm] = useState<number | null>(null);

  // Buscar Pneu
  const buscarPneu = async () => {
    if (!codigo) return;
    try {
      const res = await apiGet<any>(`/pneus/qrcode/${codigo}`);
      setPneu(res);
      setSulco(String(res.profundidade_atual || ""));
      
      // Se o pneu tem veículo, busca os dados do veículo e o último abastecimento
      if (res.veiculo_id) {
        const v = await apiGet<any>(`/veiculos/${res.veiculo_id}`);
        setVeiculo(v);
        setOdometro(String(v.hodometro_km || ""));
        
        // Verifica o último KM do abastecimento
        const abast = await apiGet<any[]>(`/abastecimentos?veiculo_id=${res.veiculo_id}&limit=1`);
        if (abast && abast.length > 0) {
          setUltimoKm(abast[0].hodometro_km);
        }
      }
      toast.success("Pneu localizado!");
    } catch (e) {
      toast.error("Pneu não encontrado.");
      setPneu(null);
    }
  };

  // Salvar Alterações
  const salvar = async () => {
    if (!pneu) return;
    
    // Validação de Odômetro
    if (odometro && ultimoKm && Number(odometro) < ultimoKm) {
      return toast.error(`O odômetro não pode ser menor que o último abastecimento (${ultimoKm} km).`);
    }

    try {
      await apiPost(`/pneus/qrcode/${pneu.numero_fogo}/atualizar`, { 
        profundidade_atual: sulco,
        odometro_km: odometro,
        nao_conformidade: naoConformidade
      });
      toast.success(naoConformidade ? "Não conformidade registrada e alerta gerado!" : "Pneu atualizado com sucesso!");
      navigate("/operacao/pneus");
    } catch (e) {
      toast.error("Erro ao atualizar.");
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <PageHeader
        eyebrow="Mobilidade"
        title="Leitor de QR Code"
        description="Escaneie o QR Code do pneu para atualizar o sulco e o odômetro."
        actions={
          <Button variant="outline" onClick={() => navigate("/operacao/pneus")}>
            <ArrowLeft className="size-4 mr-2" /> Voltar
          </Button>
        }
      />

      {/* Barra de Busca */}
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
      </div>

      {/* Resultado */}
      {pneu && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Informações e Mini Mapa */}
          <div className="glass p-6 rounded-2xl border border-slate-800">
            <div className="flex items-center gap-3 mb-4">
              <QrCode className="size-8 text-emerald-400" />
              <div>
                <h2 className="text-xl font-bold text-slate-100">{pneu.numero_fogo}</h2>
                <p className="text-sm text-slate-400">{pneu.marca} - {pneu.medida}</p>
              </div>
            </div>

            <div className="space-y-3 text-sm border-t border-slate-800 pt-3">
              <div className="flex justify-between">
                <span className="text-slate-400">Posição:</span>
                <span className="text-slate-200 font-medium">{pneu.posicao || "Não informada"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Sulco Atual:</span>
                <span className={cn("font-bold", Number(pneu.profundidade_atual) <= 3 ? "text-rose-400" : "text-emerald-400")}>
                  {pneu.profundidade_atual} mm
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Veículo:</span>
                <span className="text-slate-200 font-medium">{veiculo ? veiculo.placa : "Não alocado"}</span>
              </div>
            </div>

            {/* Mini Mapa (Ilustrativo) */}
            {veiculo && (
              <div className="mt-4 p-3 bg-slate-900 rounded-lg border border-slate-800 flex flex-col items-center">
                <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-2">Mapa do Chassi</p>
                <div className="flex gap-2">
                  <Truck className="size-6 text-sky-400" />
                  <span className="text-xs text-slate-400">Posição: {pneu.posicao?.split(' ')[0] || "—"}</span>
                </div>
              </div>
            )}
          </div>

          {/* Formulário de Atualização */}
          <div className="glass p-6 rounded-2xl border border-slate-800">
            <h3 className="text-sm font-bold text-slate-100 mb-4 border-b border-slate-800 pb-2">Atualizar Dados</h3>
            
            <div className="space-y-4">
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Profundidade do Sulco (mm)</Label>
                <Input value={sulco} onChange={(e) => setSulco(e.target.value)} type="number" className="h-10 bg-slate-950 border-slate-700" />
              </div>
              
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Odômetro do Veículo (KM)</Label>
                <Input value={odometro} onChange={(e) => setOdometro(e.target.value)} type="number" className="h-10 bg-slate-950 border-slate-700" />
                {ultimoKm && <p className="text-[10px] text-slate-500">Último abastecimento: {ultimoKm} km</p>}
              </div>

              <div className={cn("p-3 rounded-lg border flex items-start gap-3", naoConformidade ? "bg-rose-500/10 border-rose-500/30" : "bg-slate-900/50 border-slate-800")}>
                <input 
                  type="checkbox" 
                  checked={naoConformidade} 
                  onChange={(e) => setNaoConformidade(e.target.checked)}
                  className="mt-1 size-4 rounded border-slate-600 text-rose-500" 
                />
                <div>
                  <p className="text-sm font-medium text-slate-200">Pneu em Não Conformidade</p>
                  <p className="text-[10px] text-slate-500">Marque se o pneu não pertence a este veículo ou está na posição errada. Um alerta será gerado.</p>
                </div>
              </div>

              <Button onClick={salvar} className="w-full h-12 bg-emerald-600 hover:bg-emerald-500 text-lg">
                <CheckCircle2 className="size-5 mr-2" /> Salvar Alterações
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
'''

with open(path, "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✅ Tela de Leitor QR Code reescrita com validações e mini mapa.")