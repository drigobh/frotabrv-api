// Espelha backend/models/acoplamentos.py
export type Campo = "veiculo" | "carreta" | "motorista";

export interface Acoplamento {
  id: string;
  veiculo_id: string;
  veiculo_label: string;
  carreta_id: string | null;
  carreta_label: string | null;
  motorista_id: string | null;
  motorista_label: string | null;
  status: "ativo" | "liberado" | "excluido";
  completo: boolean;
  created_at: string;
  created_by: string;
  updated_at: string;
}

export interface HistoricoItem {
  id: string;
  acoplamento_id: string;
  conjunto: string;
  evento: string;
  item: Campo | "conjunto";
  descricao: string;
  status: "Acoplado" | "Desacoplado" | "Excluído";
  usuario: string;
  created_at: string;
}
