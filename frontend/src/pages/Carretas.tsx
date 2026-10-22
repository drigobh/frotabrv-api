import { CadastroTable } from "@/components/cadastros/CadastroTable";
import type { Carreta } from "@/types/cadastros";

const TIPOS_CARRETA = [
  "Bau", "Sider", "Graneleiro", "Frigorifico", "Tanque", "Prancha", "Cacamba", "Porta-conteiner"
];

const columns = [
  { key: "codigo", label: "Código", required: true, placeholder: "CR-001" },
  { key: "placa", label: "Placa", placeholder: "ABC-1234" },
  { key: "modelo", label: "Modelo", placeholder: "Ex: Graneleiro" },
  { key: "ano", label: "Ano", type: "number", placeholder: "2024" },
  { key: "hodometro_km", label: "KM", type: "number", placeholder: "0" },
  { key: "tipo", label: "Tipo", required: true, options: TIPOS_CARRETA },
  { key: "observacoes", label: "Observações", placeholder: "Opcional" },
];

export default function Carretas() {
  return (
    <CadastroTable<Carreta>
      title="Carretas"
      description="Semirreboques da frota. Inative em vez de excluir."
      endpoint="/carretas"
      queryKey="carretas"
      entityLabel="carreta"
      testPrefix="carreta"
      columns={columns}
      searchKeys={["codigo", "tipo", "placa", "modelo"]}
    />
  );
}
