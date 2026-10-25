import { PageHeader } from "@/components/common/PageHeader";
import { Bell } from "lucide-react";

export default function Avisos() {
  return (
    <div>
      <PageHeader eyebrow="Administração" title="Avisos" description="Comunicados internos." />
      <div className="glass rounded-2xl p-10 flex flex-col items-center justify-center text-center min-h-[400px]">
        <div className="size-16 bg-amber-500/10 rounded-full flex items-center justify-center mb-4">
          <Bell className="size-8 text-amber-400" />
        </div>
        <h2 className="text-xl font-bold text-slate-200 mb-2">Mural de Avisos</h2>
        <p className="text-slate-500 max-w-md">Em construção. Espaço para comunicados da gestão para os motoristas.</p>
      </div>
    </div>
  );
}
