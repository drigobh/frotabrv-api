import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_DASH_SIMPLES_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Dashboard.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Dashboard.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Dashboard.tsx")
    
    codigo = '''import { useQuery } from "@tanstack/react-query";
import { Truck, Wrench, Fuel, Users, MapPin, DollarSign } from "lucide-react";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { brl } from "@/lib/format";

export default function Dashboard() {
  const { data: fornecedores = [] } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });
  const { data: abastecimentos = [] } = useQuery({ queryKey: ["abastecimentos"], queryFn: () => apiGet<any[]>("/abastecimentos") });

  const totalFornecedores = fornecedores.length;
  const custoManutencoes = manutencoes.reduce((acc: number, m: any) => acc + (m.custo || 0), 0);
  const volumeAbastecido = abastecimentos.reduce((acc: number, a: any) => acc + (a.litros || 0), 0);
  
  const estados = [...new Set(fornecedores.map((f: any) => f.estado))].filter(Boolean);

  return (
    <div>
      <PageHeader eyebrow="Visão Geral" title="Dashboard" description="Indicadores consolidados da frota." />

      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="glass p-5 rounded-2xl flex justify-between items-center">
          <div>
            <p className="text-xs uppercase text-slate-400 mb-1">Total Fornecedores</p>
            <p className="text-3xl font-bold text-slate-100">{totalFornecedores}</p>
          </div>
          <div className="p-3 bg-sky-500/10 rounded-xl"><Truck className="size-6 text-sky-400" /></div>
        </div>
        
        <div className="glass p-5 rounded-2xl flex justify-between items-center">
          <div>
            <p className="text-xs uppercase text-slate-400 mb-1">Custo Manutenções</p>
            <p className="text-3xl font-bold text-amber-400">{brl(custoManutencoes)}</p>
          </div>
          <div className="p-3 bg-amber-500/10 rounded-xl"><Wrench className="size-6 text-amber-400" /></div>
        </div>

        <div className="glass p-5 rounded-2xl flex justify-between items-center">
          <div>
            <p className="text-xs uppercase text-slate-400 mb-1">Volume Abastecido</p>
            <p className="text-3xl font-bold text-emerald-400">{volumeAbastecido.toLocaleString('pt-BR')} L</p>
          </div>
          <div className="p-3 bg-emerald-500/10 rounded-xl"><Fuel className="size-6 text-emerald-400" /></div>
        </div>

        <div className="glass p-5 rounded-2xl flex justify-between items-center">
          <div>
            <p className="text-xs uppercase text-slate-400 mb-1">Estados Atendidos</p>
            <p className="text-3xl font-bold text-indigo-400">{estados.length}</p>
          </div>
          <div className="p-3 bg-indigo-500/10 rounded-xl"><MapPin className="size-6 text-indigo-400" /></div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass p-6 rounded-2xl">
          <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2"><Users className="size-5 text-sky-400" /> Últimas Manutenções</h3>
          <div className="space-y-2">
            {manutencoes.slice(0, 5).map((m: any) => (
              <div key={m.id} className="flex justify-between items-center p-2 border-b border-slate-800">
                <div>
                  <p className="text-sm font-medium text-slate-200">{m.descricao}</p>
                  <p className="text-xs text-slate-500">{m.veiculo_label}</p>
                </div>
                <span className="text-sm font-bold text-amber-400">{brl(m.custo)}</span>
              </div>
            ))}
            {manutencoes.length === 0 && <p className="text-slate-500 text-sm">Nenhuma manutenção registrada.</p>}
          </div>
        </div>

        <div className="glass p-6 rounded-2xl">
          <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2"><Fuel className="size-5 text-emerald-400" /> Últimos Abastecimentos</h3>
          <div className="space-y-2">
            {abastecimentos.slice(0, 5).map((a: any) => (
              <div key={a.id} className="flex justify-between items-center p-2 border-b border-slate-800">
                <div>
                  <p className="text-sm font-medium text-slate-200">{a.veiculo_label}</p>
                  <p className="text-xs text-slate-500">{a.produto}</p>
                </div>
                <span className="text-sm font-bold text-emerald-400">{a.litros} L</span>
              </div>
            ))}
            {abastecimentos.length === 0 && <p className="text-slate-500 text-sm">Nenhum abastecimento registrado.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
'''
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Dashboard.tsx recriado com sucesso (sem gráficos quebrados).")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")