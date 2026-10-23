import os
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_rapido_front_{agora}.zip"
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pasta_front = os.path.join(raiz, "frontend", "src")
        if os.path.exists(pasta_front):
            for root, dirs, files in os.walk(pasta_front):
                dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', 'build']]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try:
                        zipf.write(caminho_completo, caminho_relativo)
                    except Exception:
                        pass
    print(f"✅ Backup Frontend salvo: {nome_backup}")

def criar_tela_e_rotas(raiz):
    pasta_pages = os.path.join(raiz, "frontend", "src", "pages")
    os.makedirs(pasta_pages, exist_ok=True)
    
    # 1. Cria a página Base.tsx
    caminho_base = os.path.join(pasta_pages, "Base.tsx")
    codigo_base = '''import { useState } from "react";
import { Database, Trash2, AlertTriangle } from "lucide-react";
import { toast } from "sonner";
import { apiPost } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const COLECOES = [
  { id: "veiculos", nome: "Veículos" },
  { id: "carretas", nome: "Carretas" },
  { id: "motoristas", nome: "Motoristas" },
  { id: "acoplamentos", nome: "Acoplamentos" },
  { id: "abastecimentos", nome: "Abastecimentos" },
];

export default function Base() {
  const [open, setOpen] = useState(false);
  const [colecaoAlvo, setColecaoAlvo] = useState<string | null>(null);
  const [confirmacao, setConfirmacao] = useState("");
  const [pending, setPending] = useState(false);

  const abrirDialogo = (id: string) => {
    setColecaoAlvo(id);
    setConfirmacao("");
    setOpen(true);
  };

  const limparBase = async () => {
    if (confirmacao !== "LIMPAR") {
      toast.error("Digite a palavra LIMPAR para confirmar.");
      return;
    }
    
    setPending(true);
    try {
      await apiPost(`/admin/limpar-base?colecao=${colecaoAlvo}`);
      toast.success(`Base de ${colecaoAlvo} limpa com sucesso! Backups gerados.`);
      setOpen(false);
    } catch (error: any) {
      toast.error(error.message || "Erro ao limpar a base.");
    } finally {
      setPending(false);
    }
  };

  return (
    <div>
      <PageHeader
        eyebrow="Administração"
        title="Limpeza de Base"
        description="Apague os dados de tabelas específicas. O sistema gera um backup automático antes de qualquer exclusão."
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {COLECOES.map((c) => (
          <Card key={c.id} className="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-slate-200">
                <Database className="size-5 text-sky-400" />
                {c.nome}
              </CardTitle>
              <CardDescription>Apaga todos os registros da tabela.</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="destructive" className="w-full" onClick={() => abrirDialogo(c.id)}>
                <Trash2 className="size-4 mr-2" /> Limpar {c.nome}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-400">
              <AlertTriangle className="size-5" /> Atenção!
            </DialogTitle>
            <DialogDescription>
              Você está prestes a apagar <strong>TODOS</strong> os dados de <strong>{colecaoAlvo}</strong>.
              Um backup será gerado automaticamente, mas esta ação não pode ser desfeita pelo sistema.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-2 py-4">
            <Label>Digite <strong className="text-red-400">LIMPAR</strong> para confirmar:</Label>
            <Input value={confirmacao} onChange={(e) => setConfirmacao(e.target.value)} placeholder="LIMPAR" />
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setOpen(false)}>Cancelar</Button>
            <Button variant="destructive" disabled={confirmacao !== "LIMPAR" || pending} onClick={limparBase}>
              {pending ? "Limpando..." : "Confirmar Exclusão"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
'''
    with open(caminho_base, 'w', encoding='utf-8') as f:
        f.write(codigo_base)
    print("✅ Página Base.tsx criada.")

    # 2. Adiciona rota no App.tsx
    caminho_app = os.path.join(raiz, "frontend", "src", "App.tsx")
    if os.path.exists(caminho_app):
        with open(caminho_app, 'r', encoding='utf-8') as f:
            conteudo_app = f.read()
        
        if "import Base from" not in conteudo_app:
            # Adiciona import
            conteudo_app = conteudo_app.replace(
                "import Abastecimentos from",
                "import Base from '@/pages/Base';\nimport Abastecimentos from"
            )
            # Adiciona a Route
            if '<Route path="/abastecimentos"' in conteudo_app:
                conteudo_app = conteudo_app.replace(
                    '<Route path="/abastecimentos"',
                    '<Route path="/admin/base" element={<Base />} />\n          <Route path="/abastecimentos"'
                )
            elif '<Route path="/dashboard"' in conteudo_app:
                conteudo_app = conteudo_app.replace(
                    '<Route path="/dashboard"',
                    '<Route path="/admin/base" element={<Base />} />\n          <Route path="/dashboard"'
                )
            
            with open(caminho_app, 'w', encoding='utf-8') as f:
                f.write(conteudo_app)
            print("✅ Rota '/admin/base' adicionada no App.tsx.")
        else:
            print("ℹ️ Rota já existia no App.tsx.")

    # 3. Adiciona no Menu Lateral (Sidebar)
    caminho_sidebar = os.path.join(raiz, "frontend", "src", "components", "layout", "AppLayout.tsx")
    if not os.path.exists(caminho_sidebar):
        caminho_sidebar = os.path.join(raiz, "frontend", "src", "components", "AppLayout.tsx")
        
    if os.path.exists(caminho_sidebar):
        with open(caminho_sidebar, 'r', encoding='utf-8') as f:
            conteudo_sidebar = f.read()
            
        if "admin/base" not in conteudo_sidebar:
            # Procura a seção de gestão/administração
            if "ADMINISTRAÇÃO" in conteudo_sidebar:
                # Adiciona um item antes do fechamento da seção (isso é um pouco complexo via replace, então vou usar um método genérico)
                item_menu = '''<Link to="/admin/base" className="flex items-center gap-2 p-2 rounded-md hover:bg-slate-800">
                  <Database className="size-4" />
                  <span>Base</span>
                </Link>
                '''
                # Encontra onde termina a seção de administração (pode variar)
                conteudo_sidebar = conteudo_sidebar.replace(
                    "GESTÃO",
                    "ADMINISTRAÇÃO\n" + item_menu + "GESTÃO" # Gambiarra segura para inserir antes de Gestão
                )
            else:
                # Se não achar, adiciona no final do menu
                conteudo_sidebar = conteudo_sidebar.replace(
                    "</nav>",
                    '<div className="mt-4 border-t border-slate-800 pt-4">\n<p className="text-xs font-semibold text-slate-500 mb-2">ADMINISTRAÇÃO</p>\n<a href="/admin/base" className="flex items-center gap-2 p-2 rounded-md hover:bg-slate-800 text-sm text-slate-300">\n<Database className="size-4" /> Base\n</a>\n</div>\n</nav>'
                )
            
            with open(caminho_sidebar, 'w', encoding='utf-8') as f:
                f.write(conteudo_sidebar)
            print("✅ Link 'Base' adicionado no menu lateral (Sidebar).")
        else:
            print("ℹ️ Link 'Base' já existia no menu.")

if __name__ == "__main__":
    raiz = os.getcwd()
    criar_backup_rapido(raiz)
    criar_tela_e_rotas(raiz)
    print("\n🚀 Automação concluída! Reinicie o Vite para testar.")