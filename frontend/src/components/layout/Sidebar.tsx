import { NavLink } from "react-router-dom";
import {
  ClipboardList,
  FileBadge,
  FileDown,
  Fuel,
  Gauge,
  Link2,
  Mail,
  ShieldCheck,
  Trophy,
  Truck,
  UserRound,
  Users,
  Wallet,
  Wrench,
  Container,
  LogOut,
} from "lucide-react";
import type { Usuario } from "@/types/auth";
import { endSession } from "@/lib/session";
import { cn } from "@/lib/utils";

interface Item {
  to: string;
  label: string;
  icon: typeof Gauge;
  admin?: boolean;
}

const GRUPOS: { titulo: string; itens: Item[] }[] = [
  { titulo: "Visão geral", itens: [{ to: "/", label: "Dashboard", icon: Gauge }] },
  {
    titulo: "Cadastros",
    itens: [
      { to: "/cadastros/veiculos", label: "Veículos", icon: Truck },
      { to: "/cadastros/carretas", label: "Carretas", icon: Container },
      { to: "/cadastros/motoristas", label: "Motoristas", icon: UserRound },
    ],
  },
  {
    titulo: "Operação",
    itens: [
      { to: "/acoplamentos", label: "Acoplamentos", icon: Link2 },
      { to: "/abastecimentos", label: "Abastecimentos", icon: Fuel },
      { to: "/manutencoes", label: "Manutenções", icon: Wrench },
    ],
  },
  {
    titulo: "Gestão",
    itens: [
      { to: "/documentos", label: "Documentos", icon: FileBadge },
      { to: "/financeiro", label: "Financeiro", icon: Wallet },
      { to: "/ranking", label: "Ranking", icon: Trophy },
      { to: "/relatorios", label: "Relatórios", icon: FileDown },
    ],
  },
  {
    titulo: "Administração",
    itens: [
      { to: "/usuarios", label: "Usuários", icon: Users, admin: true },
      { to: "/auditoria", label: "Auditoria", icon: ClipboardList, admin: true },
      { to: "/avisos", label: "Avisos por e-mail", icon: Mail, admin: true },
      { to: "/seguranca", label: "Segurança", icon: ShieldCheck },
    ],
  },
];

const slug = (to: string) => (to === "/" ? "dashboard" : to.split("/").pop());

export function Sidebar({ user, onNavigate }: { user: Usuario; onNavigate?: () => void }) {
  return (
    <div className="flex h-full flex-col bg-sidebar">
      <div className="flex items-center gap-3 px-5 pb-6 pt-6">
        <div className="grid size-9 place-items-center rounded-lg bg-sky-500/15 ring-1 ring-sky-400/30">
          <Truck className="size-5 text-sky-400" />
        </div>
        <div>
          <p className="font-heading text-lg font-semibold leading-none text-slate-50">Bravus</p>
          <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.2em] text-slate-500">Gestão de Frotas</p>
        </div>
      </div>

      <nav className="flex-1 space-y-5 overflow-y-auto px-3" data-testid="sidebar-nav">
        {GRUPOS.map((g) => {
          const itens = g.itens.filter((i) => !i.admin || user.perfil === "admin");
          if (itens.length === 0) return null;
          return (
            <div key={g.titulo}>
              <p className="mb-1.5 px-3 text-[10px] font-medium uppercase tracking-[0.16em] text-slate-600">{g.titulo}</p>
              <ul className="space-y-0.5">
                {itens.map((i) => (
                  <li key={i.to}>
                    <NavLink
                      to={i.to}
                      end={i.to === "/"}
                      onClick={onNavigate}
                      data-testid={`nav-${slug(i.to)}`}
                      className={({ isActive }) =>
                        cn(
                          "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors duration-150",
                          isActive
                            ? "bg-sidebar-accent text-sky-400 shadow-[inset_2px_0_0_#38BDF8]"
                            : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-100",
                        )
                      }
                    >
                      <i.icon className="size-4 shrink-0" />
                      {i.label}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </nav>

      <div className="m-3 rounded-xl border border-slate-800 bg-slate-900/60 p-3">
        <div className="flex items-center justify-between gap-2">
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-slate-100" data-testid="sidebar-user-name">{user.nome}</p>
            <p className="truncate text-xs text-slate-500">{user.perfil === "admin" ? "Administrador" : "Operador"}</p>
          </div>
          <button
            type="button"
            onClick={() => void endSession()}
            className="rounded-md p-2 text-slate-400 transition-colors hover:bg-slate-800 hover:text-red-300"
            aria-label="Sair"
            data-testid="logout-button"
          >
            <LogOut className="size-4" />
          </button>
        </div>
        <p
          className={cn("mt-2 flex items-center gap-1.5 text-[11px]", user.totp_enabled ? "text-emerald-400" : "text-amber-400")}
          data-testid="sidebar-2fa-status"
        >
          <ShieldCheck className="size-3.5" /> {user.totp_enabled ? "2FA ativo" : "2FA desativado"}
        </p>
      </div>
    </div>
  );
}
