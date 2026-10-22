import { CadastroTable, type ColumnDef } from "@/components/cadastros/CadastroTable";
import { useHoje } from "@/hooks/useSession";
import { dataBR } from "@/lib/format";
import type { Motorista } from "@/types/cadastros";

export default function Motoristas() {
  const hoje = useHoje();
  const columns: ColumnDef<Motorista>[] = [
    { key: "nome", label: "Nome", required: true },
    { key: "cnh", label: "CNH", mono: true, required: true },
    { key: "categoria_cnh", label: "Cat.", options: ["C", "D", "E", "AC", "AD", "AE"], defaultValue: "E" },
    {
      key: "validade_cnh",
      label: "Validade CNH",
      type: "date",
      format: (r) => {
        const vencida = !!r.validade_cnh && !!hoje && r.validade_cnh < hoje;
        return (
          <span className={vencida ? "font-medium text-red-300" : ""} data-testid={`motorista-validade-${r.id}`}>
            {dataBR(r.validade_cnh)}
            {vencida && " · vencida"}
          </span>
        );
      },
    },
    { key: "telefone", label: "Telefone", placeholder: "(31) 99999-0000" },
    { key: "email", label: "E-mail", type: "email", placeholder: "Recebe o parabéns se for campeão", format: (r) => <span className="text-sm text-slate-400">{r.email || "—"}</span> },
    { key: "observacoes", label: "Observações" },
  ];
  return (
    <CadastroTable<Motorista>
      title="Motoristas"
      description="Condutores habilitados. CNHs vencidas aparecem destacadas e geram alerta no dashboard."
      endpoint="/motoristas"
      queryKey="motoristas"
      entityLabel="motorista"
      testPrefix="motorista"
      columns={columns}
      searchKeys={["nome", "cnh", "telefone", "email"]}
    />
  );
}
