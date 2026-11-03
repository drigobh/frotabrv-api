import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { Disc, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";

export default function Base() {
  const qc = useQueryClient();

  const limpar = async (tabela: string, label: string, invalidateKey: string) => {
    if (!confirm(`Tem certeza que deseja apagar TODOS os registros de ${label}? Esta ação não pode ser desfeita.`)) {
      return;
    }
    try {
      await apiDelete(`/${tabela}/limpar`);
      toast.success(`Todos os registros de ${label} foram removidos.`);
      qc.invalidateQueries({ queryKey: [invalidateKey] });
    } catch (e: any) {
      toast.error(e.message || `Erro ao limpar ${label}.`);
    }
  };

  return (
    <div>
      <PageHeader
        eyebrow="Administração"
        title="Limpeza de Base"
        description="Apague os dados de tabelas específicas. O sistema gera um backup automático."
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Veículos */}
        <div className="glass rounded-xl border border-slate-800 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-sky-500/10">
              <Disc className="size-5 text-sky-400" />
            </div>
            <h3 className="text-lg font-bold text-slate-100">Veículos</h3>
          </div>
          <p className="text-sm text-slate-400 mb-6">Apaga todos os registros da tabela.</p>
          <Button
            variant="destructive"
            className="w-full bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30"
            onClick={() => limpar("veiculos", "Veículos", "veiculos")}
          >
            <Trash2 className="size-4 mr-2" /> Limpar Veículos
          </Button>
        </div>

        {/* Carretas */}
        <div className="glass rounded-xl border border-slate-800 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-sky-500/10">
              <Disc className="size-5 text-sky-400" />
            </div>
            <h3 className="text-lg font-bold text-slate-100">Carretas</h3>
          </div>
          <p className="text-sm text-slate-400 mb-6">Apaga todos os registros da tabela.</p>
          <Button
            variant="destructive"
            className="w-full bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30"
            onClick={() => limpar("carretas", "Carretas", "carretas")}
          >
            <Trash2 className="size-4 mr-2" /> Limpar Carretas
          </Button>
        </div>

        {/* Motoristas */}
        <div className="glass rounded-xl border border-slate-800 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-sky-500/10">
              <Disc className="size-5 text-sky-400" />
            </div>
            <h3 className="text-lg font-bold text-slate-100">Motoristas</h3>
          </div>
          <p className="text-sm text-slate-400 mb-6">Apaga todos os registros da tabela.</p>
          <Button
            variant="destructive"
            className="w-full bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30"
            onClick={() => limpar("motoristas", "Motoristas", "motoristas")}
          >
            <Trash2 className="size-4 mr-2" /> Limpar Motoristas
          </Button>
        </div>

        {/* Acoplamentos */}
        <div className="glass rounded-xl border border-slate-800 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-sky-500/10">
              <Disc className="size-5 text-sky-400" />
            </div>
            <h3 className="text-lg font-bold text-slate-100">Acoplamentos</h3>
          </div>
          <p className="text-sm text-slate-400 mb-6">Apaga todos os registros da tabela.</p>
          <Button
            variant="destructive"
            className="w-full bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30"
            onClick={() => limpar("acoplamentos", "Acoplamentos", "acoplamentos")}
          >
            <Trash2 className="size-4 mr-2" /> Limpar Acoplamentos
          </Button>
        </div>

        {/* Abastecimentos */}
        <div className="glass rounded-xl border border-slate-800 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-sky-500/10">
              <Disc className="size-5 text-sky-400" />
            </div>
            <h3 className="text-lg font-bold text-slate-100">Abastecimentos</h3>
          </div>
          <p className="text-sm text-slate-400 mb-6">Apaga todos os registros da tabela.</p>
          <Button
            variant="destructive"
            className="w-full bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30"
            onClick={() => limpar("abastecimentos", "Abastecimentos", "abastecimentos")}
          >
            <Trash2 className="size-4 mr-2" /> Limpar Abastecimentos
          </Button>
        </div>

        {/* Fornecedores */}
        <div className="glass rounded-xl border border-slate-800 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-sky-500/10">
              <Disc className="size-5 text-sky-400" />
            </div>
            <h3 className="text-lg font-bold text-slate-100">Fornecedores</h3>
          </div>
          <p className="text-sm text-slate-400 mb-6">Apaga todos os registros da tabela.</p>
          <Button
            variant="destructive"
            className="w-full bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30"
            onClick={() => limpar("fornecedores", "Fornecedores", "fornecedores")}
          >
            <Trash2 className="size-4 mr-2" /> Limpar Fornecedores
          </Button>
        </div>

        {/* Pneus (NOVO) */}
        <div className="glass rounded-xl border border-slate-800 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-sky-500/10">
              <Disc className="size-5 text-sky-400" />
            </div>
            <h3 className="text-lg font-bold text-slate-100">Pneus</h3>
          </div>
          <p className="text-sm text-slate-400 mb-6">Apaga todos os registros da tabela.</p>
          <Button
            variant="destructive"
            className="w-full bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30"
            onClick={() => limpar("pneus", "Pneus", "pneus")}
          >
            <Trash2 className="size-4 mr-2" /> Limpar Pneus
          </Button>
        </div>
      </div>
    </div>
  );
}