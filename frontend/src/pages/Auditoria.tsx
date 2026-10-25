import { PageHeader } from "@/components/common/PageHeader";
import { FileBox } from "lucide-react";

export default function Auditoria() {
  return (
    <div>
      <PageHeader eyebrow="Administração" title="Auditoria" description="Histórico de ações." />
      <div className="glass rounded-2xl p-10 flex flex-col items-center justify-center text-center min-h-[400px]">
        <div className="size-16 bg-purple-500/10 rounded-full flex items-center justify-center mb-4">
          <FileBox className="size-8 text-purple-400" />
        </div>
        <h2 className="text-xl font-bold text-slate-200 mb-2">Auditoria</h2>
        <p className="text-slate-500 max-w-md">Em construção. Aqui você verá o log de todas as ações do sistema.</p>
      </div>
    </div>
  );
}
