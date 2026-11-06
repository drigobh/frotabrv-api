import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  FileBarChart, CalendarClock, LayoutDashboard, Fuel, Wrench, Truck, Users, Car, 
  Settings, Package, Disc, Activity, BarChart3, 
  FileText, DollarSign, LogOut, ChevronDown, ChevronRight, PanelLeftClose, PanelLeftOpen, Briefcase,
  Shield, Bell, UserCog, FileBox, Tag, Building, FolderOpen, Layers, BellRing, Eye
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useMe } from "@/hooks/useSession";
import { usePermissions } from "@/hooks/usePermissions";
import { Button } from "@/components/ui/button";

const MENUS = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, path: "/", isDashboard: true, items: [] },
  {
    id: "administracao", label: "Administração", icon: Shield,
    items: [
      { label: "Avisos", icon: Bell, path: "/admin/avisos" },
      { label: "Auditoria", icon: FileBox, path: "/admin/auditoria" },
      { label: "Base (Limpeza)", icon: FileText, path: "/admin/base" },
      { label: "Empresa", icon: Building, path: "/admin/empresa" },
      { label: "Parametrização", icon: Settings, path: "/admin/parametrizacao" },
      { label: "Segurança", icon: Shield, path: "/admin/seguranca" },
      { label: "Usuários", icon: UserCog, path: "/admin/usuarios" },
      { label: "Perfis de Acesso", icon: Shield, path: "/admin/perfis" },
    ]
  },
  {
    id: "cadastros", label: "Cadastro", icon: FolderOpen,
    items: [
      { label: "Cadastro de Planos", icon: Wrench, path: "/cadastros/planos-manutencao" },
      { label: "Medidas de Pneus", icon: Disc, path: "/cadastros/pneu-medidas" },
      { label: "Marcas de Pneus", icon: Tag, path: "/cadastros/pneu-marcas" },
      { label: "Modelos de Pneus", icon: Tag, path: "/cadastros/pneu-modelos" },
      { label: "Templates de Chassi", icon: Layers, path: "/cadastros/chassi-templates" },
      { label: "Carretas", icon: Car, path: "/cadastros/carretas" },
      { label: "Combustíveis", icon: Fuel, path: "/cadastros/combustiveis" },
      { label: "Fornecedores", icon: Briefcase, path: "/cadastros/fornecedores" },
      { label: "Motoristas", icon: Users, path: "/cadastros/motoristas" },
      { label: "Tipos de Fornecedores", icon: Tag, path: "/cadastros/tipos-fornecedores" },
      { label: "Veículos", icon: Truck, path: "/cadastros/veiculos" },
    ]
  },
  { id: "financeiro", label: "Financeiro", icon: DollarSign, path: "/financeiro", items: [] },
  {
    id: "frota", label: "Frota", icon: Truck,
    items: [
      { label: "Abastecimentos", icon: Fuel, path: "/abastecimentos" },
      { label: "Acoplamentos", icon: Settings, path: "/cadastros/acoplamentos" },
      { label: "Estoque", icon: Package, path: "/operacao/estoque" },
      { label: "Pneus", icon: Disc, path: "/operacao/pneus" },
    ]
  },
  {
    id: "manutencao", label: "Manutenção", icon: Wrench,
    items: [
      { label: "Plano de Manutenção", icon: CalendarClock, path: "/agendamento" },
      { label: "Gestão de Manutenção", icon: Wrench, path: "/admin/manutencoes" },
    ]
  },
  {
    id: "gestao", label: "Gestão", icon: BarChart3,
    items: [
      { label: "Central de Alertas", icon: BellRing, path: "/alertas" },
      { label: "Performance de Fornecedores", icon: BarChart3, path: "/relatorios/fornecedores" },
      { label: "Relatório de Estoque", icon: Package, path: "/relatorios/estoque" },
      { label: "Relatório de Manutenção", icon: FileBarChart, path: "/relatorio-manutencao" },
    ]
  },
  {
    id: "relatorios-gerais", label: "Relatórios Gerais", icon: FileText,
    items: [
      { label: "Relatórios Pneus", icon: BarChart3, path: "/operacao/relatorios-pneus" },
      { label: "Ficha 360º", icon: Eye, path: "/gestao/veiculo-360" },
    ]
  },
];

export function Sidebar() {
  const handleLogoff = async () => {
    try {
      // Limpa o cache do React Query (se estiver acessível)
      if (window.__REACT_QUERY_CLIENT__) {
        window.__REACT_QUERY_CLIENT__.clear();
      }
    } catch (e) {}
    // Limpa todo o armazenamento local e de sessão
    localStorage.clear();
    sessionStorage.clear();
    // Redireciona para a tela de login, forçando recarregamento completo
    window.location.replace("/login");
  };

  const { pathname } = useLocation();
  const { data: me } = useMe();
  const { podeVer } = usePermissions();
  const [isCollapsed, setIsCollapsed] = useState(() => localStorage.getItem("sidebar_collapsed") === "true");
  const [expandedMenu, setExpandedMenu] = useState<string | null>("operacao");

  useEffect(() => {
    localStorage.setItem("sidebar_collapsed", String(isCollapsed));
  }, [isCollapsed]);

  const toggleMenu = (id: string) => {
    if (expandedMenu === id) setExpandedMenu(null);
    else setExpandedMenu(id);
  };

  const handleLogout = () => {
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = "/login";
  };

  return (
    <aside className={cn("border-r border-slate-800 bg-slate-950 flex flex-col h-screen transition-all duration-300 relative z-40 shrink-0", isCollapsed ? "w-20" : "w-64")}>
      <div className={cn("p-4 flex items-center border-b border-slate-800 h-16 shrink-0", isCollapsed ? "justify-center" : "justify-between")}>
        {!isCollapsed && (
          <div className="flex items-center gap-3">
            <Truck className="size-8 text-sky-500 shrink-0" />
            <div>
              <span className="font-bold text-sm text-slate-100 tracking-tight block">Bravus</span>
              <span className="text-[10px] text-slate-400 block uppercase">Gestão de Frotas</span>
            </div>
          </div>
        )}
        
      </div>
    </aside>
  );
}
