import { useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { Menu, Truck } from "lucide-react";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { useMe } from "@/hooks/useSession";
import { Sidebar } from "./Sidebar";

export default function AppLayout() {
  const { data: user, isPending, isError } = useMe();
  const [open, setOpen] = useState(false);

  if (isPending) {
    return (
      <div className="grid min-h-screen place-items-center" data-testid="app-loading">
        <div className="flex items-center gap-3 text-slate-400">
          <Truck className="size-5 animate-pulse text-sky-400" /> Carregando Bravus Frota…
        </div>
      </div>
    );
  }
  if (isError || !user) return <Navigate to="/login" replace />;
  
  // FORÇAR LOGIN: Se estiver na raiz e não tiver vindo do login, joga para o login
  if (window.location.pathname === "/" && !sessionStorage.getItem("logado_agora")) {
      return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r border-sidebar-border md:block">
        <Sidebar user={user} />
      </aside>

      <div className="sticky top-0 z-20 flex items-center gap-3 border-b border-slate-800 bg-[#080C14]/90 px-4 py-3 backdrop-blur md:hidden">
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger render={<Button variant="ghost" size="icon" data-testid="mobile-menu-button" />}>
            <Menu className="size-5" />
          </SheetTrigger>
          <SheetContent side="left" className="w-72 border-sidebar-border p-0">
            <SheetTitle className="sr-only">Menu</SheetTitle>
            <Sidebar user={user} onNavigate={() => setOpen(false)} />
          </SheetContent>
        </Sheet>
        <span className="font-heading font-semibold">Bravus Frota</span>
      </div>

      <main className="px-4 py-6 md:ml-64 md:px-8 md:py-8 lg:px-10">
        <div className="mx-auto max-w-[1400px]">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
