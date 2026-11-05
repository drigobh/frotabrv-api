import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Search, Truck, ChevronRight, Eye } from "lucide-react";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

export default function BuscaVeiculo360() {
  const navigate = useNavigate();
  const [termo, setTermo] = useState("");
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos-360"], queryFn: () => apiGet<any[]>("/veiculos") });

  const filtrados = veiculos.filter((v: any) => 
    v.placa.toLowerCase().includes(termo.toLowerCase()) || 
    v.modelo.toLowerCase().includes(termo.toLowerCase())
  );

  return (
    <div>
      <PageHeader
        eyebrow="Gestão"
        title="Ficha 360º do Veículo"
        description="Selecione um veículo para ver o histórico completo de custos, abastecimentos e manutenções."
      />

      <div className="glass rounded-2xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800 bg-slate-900/50">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
            <Input 
              placeholder="Buscar por placa ou modelo..." 
              value={termo}
              onChange={(e) => setTermo(e.target.value)}
              className="pl-9 h-10 bg-slate-950 border-slate-700"
            />
          </div>
        </div>

        <div className="divide-y divide-slate-800">
          {filtrados.map((v: any) => (
            <div key={v.id} className="flex items-center justify-between p-4 hover:bg-slate-800/30 transition-colors">
              <div className="flex items-center gap-3">
                <span className="grid size-10 place-items-center rounded-lg bg-slate-800 text-sky-400">
                  <Truck className="size-5" />
                </span>
                <div>
                  <p className="font-mono text-sm font-bold text-slate-100">{v.placa}</p>
                  <p className="text-xs text-slate-400">{v.modelo}</p>
                </div>
              </div>
              <Button 
                size="sm" 
                variant="outline" 
                className="border-sky-500/30 text-sky-400 hover:bg-sky-500/10"
                onClick={() => navigate(`/cadastros/veiculos/${v.id}`)}
              >
                <Eye className="size-3.5 mr-1.5" /> Ver Ficha 360º
              </Button>
            </div>
          ))}
          {filtrados.length === 0 && (
            <div className="p-8 text-center text-slate-500">
              <Truck className="size-10 mx-auto mb-3 opacity-20" />
              <p>Nenhum veículo encontrado.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
