import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  FileBarChart, CalendarClock, LayoutDashboard, Fuel, Wrench, Truck, Users, Car, 
  Settings, Package, Disc, Activity, BarChart3, 
  FileText, DollarSign, LogOut, ChevronDown, ChevronRight, PanelLeftClose, PanelLeftOpen, Briefcase,
  Shield, Bell, UserCog, FileBox
, Tag , Building , FolderOpen , Layers, BellRing , Eye } from "lucide-react";
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
      { label: "Ficha 360º", icon: Eye, path: "/gestao/veiculo-360" },
      { label: "Performance de Fornecedores", icon: BarChart3, path: "/relatorios/fornecedores" },
      { label: "Relatório de Estoque", icon: Package, path: "/relatorios/estoque" },
      { label: "Relatório de Manutenção", icon: FileBarChart, path: "/relatorio-manutencao" },
    ]
  },
  {
    id: "relatorios-gerais", label: "Relatórios Gerais", icon: FileText,
    items: [
      { label: "Relatórios Pneus", icon: BarChart3, path: "/operacao/relatorios-pneus" },
    ]
  },
];

export function Sidebar() {
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
        <Button variant="ghost" size="icon" onClick={() => setIsCollapsed(!isCollapsed)} className="text-slate-400 hover:text-slate-100 hover:bg-slate-800 shrink-0">
          {isCollapsed ? <PanelLeftOpen className="size-5" /> : <PanelLeftClose className="size-5" />}
        </Button>
      </div>

      <div className="flex-1 py-4 overflow-y-auto overflow-x-hidden">
        {MENUS.filter(menu => {
            if (menu.isDashboard) return true; // Dashboard é livre
            const modulo = {
              "administracao": "Administração",
              "cadastros": "Cadastros",
              "frota": "Frota",
              "manutencao": "Manutenção",
              "financeiro": "Financeiro",
              "gestao": "Relatórios",
              "relatorios-gerais": "Relatórios",
            }[menu.id];
            return modulo ? podeVer(modulo) : true;
          }).map((menu) => {
          if (menu.isDashboard) {
            const isActive = pathname === menu.path;
            return (
              <div key={menu.id} className="px-3 mb-2">
                <Link to={menu.path!} className={cn("flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors group", isActive ? "bg-sky-500/10 text-sky-400 font-medium" : "text-slate-400 hover:bg-slate-900 hover:text-slate-200", isCollapsed && "justify-center px-0")} title={isCollapsed ? menu.label : undefined}>
                  <menu.icon className={cn("size-5", isActive ? "text-sky-400" : "text-slate-500 group-hover:text-slate-300")} />
                  {!isCollapsed && <span>{menu.label}</span>}
                </Link>
              </div>
            );
          }

          const isExpanded = expandedMenu === menu.id;
          const hasActiveChild = menu.items.some(item => pathname === item.path);

          return (
            <div key={menu.id} className="relative px-3 mb-1 group">
              <button onClick={() => !isCollapsed && toggleMenu(menu.id)} className={cn("w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors", (isExpanded || hasActiveChild) ? "text-slate-200 font-medium" : "text-slate-400 hover:bg-slate-900 hover:text-slate-200", isCollapsed && "justify-center px-0")} title={isCollapsed ? menu.label : undefined}>
                <menu.icon className={cn("size-5 shrink-0", (isExpanded || hasActiveChild) ? "text-sky-400" : "text-slate-500")} />
                {!isCollapsed && (
                  <>
                    <span className="flex-1 text-left">{menu.label}</span>
                    {isExpanded ? <ChevronDown className="size-4 text-slate-500" /> : <ChevronRight className="size-4 text-slate-500" />}
                  </>
                )}
              </button>

              {!isCollapsed && isExpanded && (
                <div className="mt-1 mb-2 space-y-1 pl-9 pr-1">
                  {menu.items.filter(item => {
                    // Lógica básica: se o usuário tem permissão no módulo pai, vê todos os filhos.
                    // Para refinamento, mapearíamos cada item para uma ação específica.
                    return true; 
                  }).map((item) => (
                    <Link key={item.path} to={item.path} className={cn("flex items-center gap-2 px-3 py-1.5 rounded-md text-xs transition-colors", pathname === item.path ? "bg-sky-500/10 text-sky-400 font-medium" : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/50")}>
                      <item.icon className="size-3.5 shrink-0" />
                      <span className="truncate">{item.label}</span>
                    </Link>
                  ))}
                </div>
              )}

              {isCollapsed && (
                <div className="absolute left-full top-0 ml-2 w-56 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 pointer-events-auto">
                  <div className="p-2">
                    <p className="text-[10px] font-bold uppercase text-sky-400 px-2 py-1 mb-1 border-b border-slate-800 pb-2">{menu.label}</p>
                    {menu.items.filter(item => {
                    // Lógica básica: se o usuário tem permissão no módulo pai, vê todos os filhos.
                    // Para refinamento, mapearíamos cada item para uma ação específica.
                    return true; 
                  }).map((item) => (
                      <Link key={item.path} to={item.path} className={cn("flex items-center gap-2 px-2 py-2 rounded-md text-xs transition-colors", pathname === item.path ? "bg-sky-500/10 text-sky-400 font-medium" : "text-slate-400 hover:text-slate-100 hover:bg-slate-800")}>
                        <item.icon className="size-3.5 shrink-0" />
                        <span className="truncate">{item.label}</span>
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="p-3 border-t border-slate-800 shrink-0">
        <Link to="/perfil" className={cn("flex items-center gap-3 px-2 py-2 rounded-lg bg-slate-900/50 mb-2 transition-colors hover:bg-slate-800", isCollapsed && "justify-center")}>
          <div className="size-8 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-300 shrink-0 overflow-hidden">
            {me?.foto_url ? (
              <img src={me.foto_url} alt={me.nome} className="size-full object-cover" />
            ) : (
              me?.nome?.charAt(0).toUpperCase() || "U"
            )}
          </div>
          {!isCollapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-slate-200 truncate">{me?.nome || "Rodrigo Admin"}</p>
              <p className="text-[10px] text-slate-500 truncate">{me?.perfil || "Administrador"}</p>
            </div>
          )}
        </Link>
        <Button variant="ghost" className={cn("w-full text-red-400 hover:text-red-300 hover:bg-red-500/10 h-9", isCollapsed ? "justify-center px-0" : "justify-start px-3")} onClick={() => { localStorage.clear(); window.location.href = "/login"; }}>
          <LogOut className={cn("size-4", !isCollapsed && "mr-2")} /> 
          {!isCollapsed && "Sair"}
        </Button>
      </div>
    </aside>
  );
}
