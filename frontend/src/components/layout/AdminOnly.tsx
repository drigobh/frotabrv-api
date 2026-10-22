import { Navigate } from "react-router-dom";
import { Lock } from "lucide-react";
import type { ReactNode } from "react";
import { useMe } from "@/hooks/useSession";

// Esconde páginas de admin para operadores (o backend também nega com 403).
export function AdminOnly({ children }: { children: ReactNode }) {
  const { data: user } = useMe();
  if (!user) return <Navigate to="/login" replace />;
  if (user.perfil !== "admin") {
    return (
      <div className="glass mt-10 flex flex-col items-center gap-3 rounded-2xl p-10 text-center" data-testid="admin-only-block">
        <Lock className="size-8 text-amber-400" />
        <h2 className="text-xl font-semibold">Acesso restrito</h2>
        <p className="text-sm text-slate-400">Somente administradores podem acessar esta área.</p>
      </div>
    );
  }
  return <>{children}</>;
}
