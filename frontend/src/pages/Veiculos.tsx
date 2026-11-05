import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Eye } from "lucide-react";
import { apiGet } from "@/lib/api";
import { CadastroTable, type ColumnDef } from "@/components/cadastros/CadastroTable";
import { Button } from "@/components/ui/button";
import { num } from "@/lib/format";
import type { Veiculo } from "@/types/cadastros";

const columns: ColumnDef<Veiculo>[] = [
  { key: "placa", label: "Placa", mono: true, required: true, placeholder: "ABC1D23" },
  { key: "modelo", label: "Modelo", required: true, placeholder: "Volvo FH 540" },
  { 
    key: "template_chassi_id", 
    label: "Template de Chassi", 
    type: "text", 
    fetchOptions: { endpoint: "/chassi-templates", labelKey: "nome", filterKey: "categoria", filterValue: "CAVALO" } 
  },
  { key: "ano", label: "Ano", type: "number", required: true, defaultValue: "2024" },
  { key: "hodometro_km", label: "Hodômetro", type: "number", defaultValue: "0", format: (r) => <span className="font-mono">{num(r.hodometro_km)} km</span> },
  { key: "observacoes", label: "Observações" },
];

export default function Veiculos() {
  const navigate = useNavigate();
  const { data: templates = [] } = useQuery({
    queryKey: ["chassi-templates"],
    queryFn: () => apiGet<any[]>("/chassi-templates"),
  });

  const colunasComTemplate = columns.map(col => {
    if (col.key === "template_chassi_id") {
      return {
        ...col,
        format: (r: Veiculo) => {
          const template = templates.find((t: any) => t.id === r.template_chassi_id);
          return template ? template.nome : "—";
        }
      };
    }
    return col;
  });

  return (
    <CadastroTable<Veiculo>
      title="Veículos"
      description="Cavalos mecânicos da frota. Inative em vez de excluir — o histórico é preservado."
      endpoint="/veiculos"
      queryKey="veiculos"
      entityLabel="veículo"
      testPrefix="veiculo"
      columns={colunasComTemplate}
      searchKeys={["placa", "modelo"]}
      extraActions={(v) => (
        <Button 
          size="icon-sm" 
          variant="ghost" 
          onClick={() => navigate(`/cadastros/veiculos/${v.id}`)} 
          title="Visão 360º"
        >
          <Eye className="size-4 text-emerald-400" />
        </Button>
      )}
    />
  );
}
