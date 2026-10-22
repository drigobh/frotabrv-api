import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { apiGet } from "@/lib/api";
import { dataHoraBR } from "@/lib/format";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PageHeader } from "@/components/common/PageHeader";
import { FieldSelect } from "@/components/common/FieldSelect";
import { StatusBadge, type Tone } from "@/components/common/StatusBadge";
import { AdminOnly } from "@/components/layout/AdminOnly";
import type { AuditoriaItem } from "@/types/auditoria";

const TODAS = "__all__";
const ENTIDADES = [
  { value: TODAS, label: "Todas as entidades" },
  { value: "auth", label: "Autenticação" },
  { value: "veiculos", label: "Veículos" },
  { value: "carretas", label: "Carretas" },
  { value: "motoristas", label: "Motoristas" },
  { value: "acoplamentos", label: "Acoplamentos" },
  { value: "abastecimentos", label: "Abastecimentos" },
  { value: "manutencoes", label: "Manutenções" },
  { value: "usuarios", label: "Usuários" },
];

const tom = (acao: string): Tone =>
  acao.startsWith("excluir") || acao === "inativar" ? "excluido" : acao === "criar" || acao === "acoplar" || acao === "reativar" ? "ativo" : acao === "login" ? "info" : "desacoplado";

function AuditoriaConteudo() {
  const [entidade, setEntidade] = useState(TODAS);
  const [busca, setBusca] = useState("");
  const params = new URLSearchParams();
  if (entidade !== TODAS) params.set("entidade", entidade);
  if (busca.trim()) params.set("q", busca.trim());
  const q = useQuery({ queryKey: ["auditoria", entidade, busca.trim()], queryFn: () => apiGet<AuditoriaItem[]>(`/auditoria?${params.toString()}`) });
  const rows = q.isError ? [] : (q.data ?? []);

  return (
    <div>
      <PageHeader eyebrow="Administração" title="Auditoria" description="Registro completo de ações: quem fez o quê, quando e de onde." />
      <div className="mb-4 flex flex-wrap gap-3">
        <div className="w-60"><FieldSelect value={entidade} onChange={setEntidade} options={ENTIDADES} testId="auditoria-filtro-entidade" /></div>
        <div className="relative">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-slate-500" />
          <Input value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Buscar usuário, ação, detalhe…" className="w-72 pl-8" data-testid="auditoria-search-input" />
        </div>
      </div>
      <div className="glass overflow-hidden rounded-2xl">
        <Table data-testid="auditoria-table">
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {["Quando", "Usuário", "Ação", "Entidade", "Detalhes", "IP"].map((h) => (
                <TableHead key={h} className="text-xs uppercase tracking-wider text-slate-500">{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.length === 0 && (
              <TableRow><TableCell colSpan={6} className="py-10 text-center text-slate-500">{q.isPending ? "Carregando…" : "Nenhum registro."}</TableCell></TableRow>
            )}
            {rows.map((a) => (
              <TableRow key={a.id} className="border-slate-800/70" data-testid="auditoria-row">
                <TableCell className="whitespace-nowrap font-mono text-xs">{dataHoraBR(a.created_at)}</TableCell>
                <TableCell>{a.usuario_nome}</TableCell>
                <TableCell><StatusBadge tone={tom(a.acao)}>{a.acao}</StatusBadge></TableCell>
                <TableCell className="text-slate-400">{a.entidade}</TableCell>
                <TableCell className="max-w-[420px] truncate text-sm text-slate-300" title={a.detalhes}>{a.detalhes}</TableCell>
                <TableCell className="font-mono text-xs text-slate-500">{a.ip ?? "—"}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

export default function Auditoria() {
  return <AdminOnly><AuditoriaConteudo /></AdminOnly>;
}
