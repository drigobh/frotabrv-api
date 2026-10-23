import os
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_rapido_sidebar_rebuild_{agora}.zip"
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print("📦 Criando Backup Rápido...")
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pasta_front = os.path.join(raiz, "frontend", "src")
        for root, dirs, files in os.walk(pasta_front):
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', 'build']]
            for file in files:
                caminho_completo = os.path.join(root, file)
                caminho_relativo = os.path.relpath(caminho_completo, raiz)
                try:
                    zipf.write(caminho_completo, caminho_relativo)
                except Exception:
                    pass
    print(f"✅ Backup salvo: {nome_backup}")

def recriar_sidebar(raiz):
    caminho_sidebar = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    
    if not os.path.exists(caminho_sidebar):
        print("❌ Arquivo Sidebar.tsx não encontrado em components/layout.")
        return

    # Código completo e limpo do Sidebar
    codigo_sidebar = '''import { Link, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, Truck, Users, Link as LinkIcon, Fuel, Wrench, 
  FileText, DollarSign, Trophy, BarChart3, Shield, FileWarning, 
  Bell, Database, LogOut 
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useMe } from "@/hooks/useSession";
import { Button } from "@/components/ui/button";

type SidebarProps = {
  user: { nome: string; perfil: string };
  onNavigate?: () => void;
};

export function Sidebar({ user, onNavigate }: SidebarProps) {
  const location = useLocation();
  const currentPath = location.pathname;

  const menuSections = [
    {
      title: "VISÃO GERAL",
      items: [
        { label: "Dashboard", icon: LayoutDashboard, path: "/" },
      ],
    },
    {
      title: "CADASTROS",
      items: [
        { label: "Veículos", icon: Truck, path: "/cadastros/veiculos" },
        { label: "Carretas", icon: LinkIcon, path: "/cadastros/carretas" },
        { label: "Motoristas", icon: Users, path: "/cadastros/motoristas" },
      ],
    },
    {
      title: "OPERAÇÃO",
      items: [
        { label: "Acoplamentos", icon: LinkIcon, path: "/acoplamentos" },
        { label: "Abastecimentos", icon: Fuel, path: "/abastecimentos" },
        { label: "Manutenções", icon: Wrench, path: "/manutencoes" },
      ],
    },
    {
      title: "GESTÃO",
      items: [
        { label: "Documentos", icon: FileText, path: "/documentos" },
        { label: "Financeiro", icon: DollarSign, path: "/financeiro" },
        { label: "Ranking", icon: Trophy, path: "/ranking" },
        { label: "Relatórios", icon: BarChart3, path: "/relatorios" },
      ],
    },
    {
      title: "ADMINISTRAÇÃO",
      items: [
        { label: "Usuários", icon: Users, path: "/usuarios" },
        { label: "Auditoria", icon: Shield, path: "/auditoria" },
        { label: "Avisos", icon: Bell, path: "/avisos" },
        { label: "Segurança", icon: FileWarning, path: "/seguranca" },
        { label: "Base", icon: Database, path: "/admin/base" },
      ],
    },
  ];

  return (
    <div className="flex h-full flex-col bg-sidebar text-sidebar-foreground">
      <div className="flex h-16 items-center border-b border-sidebar-border px-6">
        <Link to="/" className="flex items-center gap-2" onClick={onNavigate}>
          <Truck className="size-6 text-sky-400" />
          <div className="flex flex-col">
            <span className="font-heading text-sm font-bold leading-tight">Bravus</span>
            <span className="text-[10px] font-medium uppercase tracking-wider text-slate-500">Gestão de Frotas</span>
          </div>
        </Link>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-4">
        {menuSections.map((section) => (
          <div key={section.title} className="mb-6">
            <h3 className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
              {section.title}
            </h3>
            <nav className="space-y-1">
              {section.items.map((item) => {
                const isActive = currentPath === item.path || (item.path !== "/" && currentPath.startsWith(item.path));
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={onNavigate}
                    className={cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-slate-800 text-slate-100"
                        : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                    )}
                  >
                    <item.icon className="size-4" />
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>
        ))}
      </div>

      <div className="border-t border-sidebar-border p-4">
        <div className="flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-sm font-medium">{user.nome}</span>
            <span className="text-xs text-slate-500">{user.perfil}</span>
          </div>
          <Button variant="ghost" size="icon" className="text-slate-400 hover:text-red-400" title="Sair">
            <LogOut className="size-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
'''

    with open(caminho_sidebar, 'w', encoding='utf-8') as f:
        f.write(codigo_sidebar)
    print("✅ Arquivo Sidebar.tsx recriado com sucesso, com o link 'Base' incluído.")

if __name__ == "__main__":
    raiz = os.getcwd()
    print("🤖 Iniciando Recriação do Sidebar...")
    criar_backup_rapido(raiz)
    recriar_sidebar(raiz)
    print("\n🚀 Concluído! Reinicie o Vite para testar.")