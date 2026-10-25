import { PageHeader } from "@/components/common/PageHeader";
import { Package } from "lucide-react";

export default function Estoque() {
  return (
    <div>
      <PageHeader eyebrow="Operação" title="Estoque" description="Controle de peças e insumos." />
      <div className="glass rounded-2xl p-10 flex flex-col items-center justify-center text-center min-h-[400px]">
        <div className="size-16 bg-amber-500/10 rounded-full flex items-center justify-center mb-4">
          <Package className="size-8 text-amber-400" />
        </div>
        <h2 className="text-xl font-bold text-slate-200 mb-2">Estoque e Peças</h2>
        <p className="text-slate-500 max-w-md">Esta tela está em construção. Em breve você poderá dar entrada em peças, controlar o estoque mínimo, e integrar as peças utilizadas nas manutenções.</p>
      </div>
    </div>
  );
}
