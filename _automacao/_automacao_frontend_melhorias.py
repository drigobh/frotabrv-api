import os
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_rapido_front_melhorias_{agora}.zip"
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    print("📦 Criando Backup Rápido do Frontend...")
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pasta_front = os.path.join(raiz, "frontend", "src")
        for root, dirs, files in os.walk(pasta_front):
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', 'build']]
            for file in files:
                caminho_completo = os.path.join(root, file)
                caminho_relativo = os.path.relpath(caminho_completo, raiz)
                try: zipf.write(caminho_completo, caminho_relativo)
                except: pass

def atualizar_frontend(raiz):
    # 1. Corrigir Abastecimentos.tsx para o Modal de Erros
    caminho_abast = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    if os.path.exists(caminho_abast):
        with open(caminho_abast, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        if "const [importProgress" not in conteudo:
            conteudo = conteudo.replace(
                'const [excluirId, setExcluirId] = useState<string | null>(null);',
                'const [excluirId, setExcluirId] = useState<string | null>(null);\n  const [importProgress, setImportProgress] = useState<{ total: number; current: number; errors: any[]; success: boolean } | null>(null);'
            )
            
        # Injeta o Modal antes do ConfirmDialog
        modal_jsx = '''
      <Dialog open={importProgress !== null} onOpenChange={() => {}}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Importando Planilha</DialogTitle>
            <DialogDescription>
              {importProgress && importProgress.current < importProgress.total ? "Processando..." : "Concluído!"}
            </DialogDescription>
          </DialogHeader>
          {importProgress && (
            <div className="space-y-4 py-4">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Progresso</span>
                <span className="font-mono">{importProgress.current} / {importProgress.total}</span>
              </div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-sky-500 transition-all" style={{ width: `${(importProgress.current / importProgress.total) * 100}%` }} />
              </div>
              {importProgress.errors.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-semibold text-red-400 mb-2 flex items-center gap-2"><AlertTriangle className="size-4" /> Erros ({importProgress.errors.length})</h4>
                  <div className="max-h-40 overflow-y-auto rounded-md border border-slate-800 bg-slate-950 p-2">
                    <ul className="space-y-1 text-xs">
                      {importProgress.errors.map((err, idx) => (
                        <li key={idx} className="text-slate-300"><span className="font-mono text-slate-500">Linha {err.linha}</span> - <span className="text-red-300">{err.placa}</span>: {err.erro}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            {importProgress && importProgress.current >= importProgress.total ? (
              <Button onClick={() => setImportProgress(null)}>Fechar</Button>
            ) : <Button disabled variant="outline">Processando...</Button>}
          </DialogFooter>
        </DialogContent>
      </Dialog>
'''
        if "importProgress !== null" not in conteudo:
            conteudo = conteudo.replace("<ConfirmDialog", modal_jsx + "\n      <ConfirmDialog")
            conteudo = conteudo.replace("Fuel, Plus, Trash2,", "Fuel, Plus, Trash2, AlertTriangle,")
            
        with open(caminho_abast, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Abastecimentos.tsx atualizado com o Modal de Erros.")

    # 2. Criar a página Hodometro.tsx
    caminho_hodometro = os.path.join(raiz, "frontend", "src", "pages", "Hodometro.tsx")
    codigo_hodometro = '''import { useQuery } from "@tanstack/react-query";
import { Gauge, Info, TrendingUp, DollarSign, Droplets } from "lucide-react";
import { apiGet } from "@/lib/api";
import { brl, num } from "@/lib/format";
import { PageHeader } from "@/components/common/PageHeader";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

export default function Hodometro() {
  const { data, isLoading } = useQuery({
    queryKey: ["hodometro-atual"],
    queryFn: () => apiGet<any[]>("/abastecimentos/hodometro-atual"),
  });

  const rows = data ?? [];

  return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Hodômetro Atual"
        description="Acompanhamento em tempo real do último KM registrado e estatísticas por veículo."
      />

      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead className="text-xs">Veículo</TableHead>
              <TableHead className="text-xs text-right">Último KM</TableHead>
              <TableHead className="text-xs text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && <TableRow><TableCell colSpan={3} className="text-center py-10">Carregando...</TableCell></TableRow>}
            {rows.map((v) => (
              <TableRow key={v.veiculo_id} className="border-slate-800/70">
                <TableCell>
                  <p className="font-mono font-medium text-slate-200">{v.placa}</p>
                  <p className="text-xs text-slate-500">{v.modelo}</p>
                </TableCell>
                <TableCell className="text-right font-mono text-sky-300 font-bold">{num(v.ultimo_km)} km</TableCell>
                <TableCell className="text-center">
                  <Dialog>
                    <DialogTrigger render={<Button variant="ghost" size="icon-sm" className="text-sky-400 hover:bg-sky-500/10" />}>
                      <Info className="size-5" />
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-md bg-[#0F172A] border-slate-800 text-slate-200">
                      <DialogHeader>
                        <DialogTitle className="flex items-center gap-2"><Gauge className="size-5 text-sky-400" /> Detalhes - {v.placa}</DialogTitle>
                      </DialogHeader>
                      <div className="grid grid-cols-2 gap-4 py-4">
                        <div className="p-3 bg-slate-900 rounded-lg">
                          <p className="text-xs text-slate-400 mb-1 flex items-center gap-1"><TrendingUp className="size-3" /> Abastecimentos</p>
                          <p className="text-lg font-bold">{v.qtd_geral} <span className="text-xs font-normal text-slate-500">total</span></p>
                          <p className="text-sm text-slate-300">{v.qtd_mes} este mês / {v.qtd_mes_anterior} mês ant.</p>
                        </div>
                        <div className="p-3 bg-slate-900 rounded-lg">
                          <p className="text-xs text-slate-400 mb-1 flex items-center gap-1"><Droplets className="size-3" /> Média KM/L</p>
                          <p className="text-lg font-bold text-sky-400">{num(v.media_ultimo, 2)} <span className="text-xs font-normal text-slate-500">último</span></p>
                          <p className="text-sm text-slate-300">{num(v.media_mes, 2)} este mês / {num(v.media_mes_anterior, 2)} mês ant.</p>
                        </div>
                        <div className="p-3 bg-slate-900 rounded-lg col-span-2 flex justify-between">
                          <div>
                            <p className="text-xs text-slate-400 mb-1 flex items-center gap-1"><DollarSign className="size-3" /> Custos</p>
                            <p className="text-lg font-bold">{brl(v.total_mes)} <span className="text-xs font-normal text-slate-500">este mês</span></p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-slate-400 mb-1">Mês Anterior</p>
                            <p className="text-lg font-bold text-slate-400">{brl(v.total_mes_anterior)}</p>
                          </div>
                        </div>
                        <div className="col-span-2 text-center text-sm text-slate-400">
                          Preço médio pago este mês: <strong className="text-slate-200">{brl(v.media_preco_mes)}/L</strong>
                        </div>
                      </div>
                    </DialogContent>
                  </Dialog>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
'''
    with open(caminho_hodometro, 'w', encoding='utf-8') as f:
        f.write(codigo_hodometro)
    print("✅ Página Hodometro.tsx criada.")

    # 3. Registrar no App.tsx e Sidebar.tsx (já que o script anterior falhou em fazer isso corretamente)
    caminho_app = os.path.join(raiz, "frontend", "src", "App.tsx")
    if os.path.exists(caminho_app):
        with open(caminho_app, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        if "import Hodometro" not in conteudo:
            conteudo = conteudo.replace("import Abastecimentos", "import Hodometro from '@/pages/Hodometro';\nimport Abastecimentos")
            conteudo = conteudo.replace('<Route path="abastecimentos"', '<Route path="hodometro" element={<Hodometro />} />\n          <Route path="abastecimentos"')
            with open(caminho_app, 'w', encoding='utf-8') as f: f.write(conteudo)
            print("✅ Rota '/hodometro' adicionada no App.tsx.")

    caminho_sidebar = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    if os.path.exists(caminho_sidebar):
        with open(caminho_sidebar, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        if "/hodometro" not in conteudo:
            conteudo = conteudo.replace(
                '{ label: "Abastecimentos", icon: Fuel, path: "/abastecimentos" }',
                '{ label: "Hodômetro Atual", icon: Gauge, path: "/hodometro" },\n        { label: "Abastecimentos", icon: Fuel, path: "/abastecimentos" }'
            )
            conteudo = conteudo.replace("LayoutDashboard,", "Gauge, LayoutDashboard,")
            with open(caminho_sidebar, 'w', encoding='utf-8') as f: f.write(conteudo)
            print("✅ Link do Hodômetro adicionado no Sidebar.")

if __name__ == "__main__":
    raiz = os.getcwd()
    criar_backup_rapido(raiz)
    atualizar_frontend(raiz)
    print("\n🚀 Concluído! Reinicie o Vite e faça o push para o Render.")