import { CadastroTable, type ColumnDef } from "@/components/cadastros/CadastroTable";
import { num } from "@/lib/format";
import type { Veiculo } from "@/types/cadastros";

const columns: ColumnDef<Veiculo>[] = [
  { key: "placa", label: "Placa", mono: true, required: true, placeholder: "ABC1D23" },
  { key: "modelo", label: "Modelo", required: true, placeholder: "Volvo FH 540" },
  { key: "ano", label: "Ano", type: "number", required: true, defaultValue: "2024" },
  { key: "hodometro_km", label: "Hodômetro", type: "number", defaultValue: "0", format: (r) => <span className="font-mono">{num(r.hodometro_km)} km</span> },
  { key: "observacoes", label: "Observações" },
];

export default function Veiculos() {
  return (
    <CadastroTable<Veiculo>
      title="Veículos"
      description="Cavalos mecânicos da frota. Inative em vez de excluir — o histórico é preservado."
      endpoint="/veiculos"
      queryKey="veiculos"
      entityLabel="veículo"
      testPrefix="veiculo"
      columns={columns}
      searchKeys={["placa", "modelo"]}
    />
  );
}
