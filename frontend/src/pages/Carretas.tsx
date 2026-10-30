import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
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
  { key: "template_chassi_id", label: "Template de Chassi", type: "text", fetchOptions: { endpoint: "/chassi-templates", labelKey: "nome", filterKey: "categoria", filterValue: "CARRETA" } },
  { key: "observacoes", label: "Observações", placeholder: "Opcional" },
];

export default function Carretas() {
  const { data: templates = [] } = useQuery({
    queryKey: ["chassi-templates"],
    queryFn: () => apiGet<any[]>("/chassi-templates"),
  });

  const colunasComTemplate = columns.map(col => {
    if (col.key === "template_chassi_id") {
      return {
        ...col,
        format: (r: Carreta) => {
          const template = templates.find((t: any) => t.id === r.template_chassi_id);
          return template ? template.nome : "—";
        }
      };
    }
    return col;
  });

  return (
    <CadastroTable<Carreta>
      title="Carretas"
      description="Semirreboques da frota. Inative em vez de excluir."
      endpoint="/carretas"
      queryKey="carretas"
      entityLabel="carreta"
      testPrefix="carreta"
      columns={colunasComTemplate}
      searchKeys={["codigo", "placa", "tipo"]}
    />
  );
}
