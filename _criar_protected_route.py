import os

path = os.path.join(os.getcwd(), "frontend", "src", "components", "auth", "ProtectedRoute.tsx")

os.makedirs(os.path.dirname(path), exist_ok=True)

conteudo = r'''import { Navigate, Outlet } from "react-router-dom";
import { usePermissions } from "@/hooks/usePermissions";
import { Loader2 } from "lucide-react";

interface ProtectedRouteProps {
  modulo: string;
  acao?: string;
}

export function ProtectedRoute({ modulo, acao = "Ver" }: ProtectedRouteProps) {
  const { temPermissao, me } = usePermissions();

  // Se o usuário ainda não carregou, mostra um loading
  if (!me) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-950">
        <Loader2 className="size-8 animate-spin text-sky-500" />
      </div>
    );
  }

  // Se não tem permissão, redireciona para o dashboard
  if (!temPermissao(modulo, acao)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
'''

with open(path, "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✅ Componente ProtectedRoute criado.")