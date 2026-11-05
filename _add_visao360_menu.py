import os
import re

# ==========================================
# 1. CRIAR UMA PÁGINA DE BUSCA DE VEÍCULO (PARA O MENU)
# ==========================================
path_busca = os.path.join(os.getcwd(), "frontend", "src", "pages", "BuscaVeiculo360.tsx")

conteudo_busca = r'''import { useState } from "react";
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
'''
with open(path_busca, "w", encoding="utf-8") as f:
    f.write(conteudo_busca)
print("✅ Página BuscaVeiculo360.tsx criada.")

# ==========================================
# 2. INJETAR ROTA NO APP.TSX
# ==========================================
app_path = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")
with open(app_path, "r", encoding="utf-8") as f:
    app_c = f.read()

if "BuscaVeiculo360" not in app_c:
    # Import
    app_c = app_c.replace(
        'import VeiculoDetalhe from "@/pages/VeiculoDetalhe";',
        'import VeiculoDetalhe from "@/pages/VeiculoDetalhe";\nimport BuscaVeiculo360 from "@/pages/BuscaVeiculo360";'
    )
    # Rota: Coloca antes da rota de detalhes
    app_c = app_c.replace(
        '<Route path="/cadastros/veiculos/:id"',
        '<Route path="/gestao/veiculo-360" element={<BuscaVeiculo360 />} />\n          <Route path="/cadastros/veiculos/:id"'
    )
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_c)
    print("✅ Rota /gestao/veiculo-360 injetada no App.tsx.")

# ==========================================
# 3. INJETAR LINK NO SIDEBAR (MENU GESTÃO)
# ==========================================
sidebar_path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")
with open(sidebar_path, "r", encoding="utf-8") as f:
    side_c = f.read()

if "/gestao/veiculo-360" not in side_c:
    # Encontra o menu Gestão para injetar o link
    # (A âncora é o link de Performance de Fornecedores)
    ancora = '{ label: "Performance de Fornecedores", icon: BarChart3, path: "/relatorios/fornecedores" },'
    novo_link = '{ label: "Ficha 360º", icon: Eye, path: "/gestao/veiculo-360" },\n      ' + ancora
    
    side_c = side_c.replace(ancora, novo_link)
    
    # Garante que o ícone Eye está importado
    if "Eye" not in side_c.split("from \"lucide-react\"")[0]:
        side_c = re.sub(r'import\s+\{([^}]+)\}\s+from\s+"lucide-react";', r'import {\1, Eye } from "lucide-react";', side_c, count=1)

    with open(sidebar_path, "w", encoding="utf-8") as f:
        f.write(side_c)
    print("✅ Link 'Ficha 360º' injetado no menu Gestão.")
else:
    print("ℹ️ O link já existia no menu Gestão.")