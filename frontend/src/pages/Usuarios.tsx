import { PageHeader } from "@/components/common/PageHeader";
import { UserCog } from "lucide-react";

export default function Usuarios() {
  return (
    <div>
      <PageHeader eyebrow="Administração" title="Usuários" description="Gestão de acessos." />
      <div className="glass rounded-2xl p-10 flex flex-col items-center justify-center text-center min-h-[400px]">
        <div className="size-16 bg-sky-500/10 rounded-full flex items-center justify-center mb-4">
          <UserCog className="size-8 text-sky-400" />
        </div>
        <h2 className="text-xl font-bold text-slate-200 mb-2">Módulo de Usuários</h2>
        <p className="text-slate-500 max-w-md">Em construção. Em breve você poderá gerenciar permissões e acessos.</p>
      </div>
    </div>
  );
}
