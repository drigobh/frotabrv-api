import { PageHeader } from "@/components/common/PageHeader";
import { Shield } from "lucide-react";

export default function Seguranca() {
  return (
    <div>
      <PageHeader eyebrow="Administração" title="Segurança" description="Configurações de segurança." />
      <div className="glass rounded-2xl p-10 flex flex-col items-center justify-center text-center min-h-[400px]">
        <div className="size-16 bg-emerald-500/10 rounded-full flex items-center justify-center mb-4">
          <Shield className="size-8 text-emerald-400" />
        </div>
        <h2 className="text-xl font-bold text-slate-200 mb-2">Segurança do Sistema</h2>
        <p className="text-slate-500 max-w-md">Em construção. Aqui você poderá trocar senhas, ativar 2FA e ver logs de acesso.</p>
      </div>
    </div>
  );
}
