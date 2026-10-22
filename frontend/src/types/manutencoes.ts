// Espelha backend/models/manutencoes.py
export type TipoManutencao = "preventiva" | "corretiva";
export type StatusManutencao = "agendada" | "em_execucao" | "concluida";

export interface ManutencaoCreate {
  veiculo_id: string;
  tipo: TipoManutencao;
  descricao: string;
  oficina: string;
  custo: number;
  data: string;
  km: number | null;
  pecas: string;
  status: StatusManutencao;
  proxima_km: number | null;
}

export interface Manutencao extends ManutencaoCreate {
  id: string;
  veiculo_label: string;
  created_by: string;
  created_at: string;
}

export const STATUS_MANUTENCAO: Record<StatusManutencao, string> = {
  agendada: "Agendada",
  em_execucao: "Em execução",
  concluida: "Concluída",
};
