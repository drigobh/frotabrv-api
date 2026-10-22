import { CadastroTable, type ColumnDef } from "@/components/cadastros/CadastroTable";
import type { Carreta } from "@/types/cadastros";

const TIPOS = ["Baú", "Sider", "Graneleiro", "Frigorífico", "Tanque", "Prancha", "Caçamba", "Porta-contêiner"];

const columns: ColumnDef<Carreta>[] = [
  { key: "codigo", label: "Código", mono: true, required: true, placeholder: "CR-107" },
  { key: "tipo", label: "Tipo", required: true, options: TIPOS, defaultValue: "Baú" },
  { key: "observacoes", label: "Observações" },
];

export default function Carretas() {
  return (
    <CadastroTable<Carreta>
      title="Carretas"
      description="Implementos rodoviários disponíveis para acoplamento."
      endpoint="/carretas"
      queryKey="carretas"
      entityLabel="carreta"
      testPrefix="carreta"
      columns={columns}
      searchKeys={["codigo", "tipo"]}
    />
  );
}
