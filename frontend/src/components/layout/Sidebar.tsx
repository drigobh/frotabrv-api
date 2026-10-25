import { Link, useLocation } from "react-router-dom";
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
        { label: "Combustíveis", icon: Fuel, path: "/cadastros/combustiveis" },
        { label: "Fornecedores", icon: Truck, path: "/cadastros/fornecedores" },
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
