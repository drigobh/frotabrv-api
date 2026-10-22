// Espelha backend/models/financeiro.py
export type TipoConta = "pagar" | "receber";
export type OrigemConta = "abastecimento" | "manutencao" | "frete" | "manual";
export type StatusConta = "aberta" | "paga";

export interface ContaCreate {
  tipo: TipoConta;
  descricao: string;
  categoria: string;
  veiculo_id: string | null;
  valor: number;
  vencimento: string;
}

export interface Conta {
  id: string;
  tipo: TipoConta;
  origem: OrigemConta;
  origem_id: string | null;
  descricao: string;
  categoria: string;
  veiculo_id: string | null;
  veiculo_label: string | null;
  valor: number;
  vencimento: string;
  status: StatusConta;
  pago_em: string | null;
  vencida: boolean;
  created_by: string;
  created_at: string;
}

export interface BaixaIn {
  data: string;
}

export interface FreteCreate {
  data: string;
  veiculo_id: string;
  motorista_id: string | null;
  cliente: string;
  origem: string;
  destino: string;
  valor: number;
  vencimento: string;
  observacoes: string;
}

export interface Frete extends FreteCreate {
  id: string;
  veiculo_label: string;
  motorista_label: string | null;
  created_by: string;
  created_at: string;
}

export interface RentabilidadeVeiculo {
  veiculo_id: string;
  veiculo_label: string;
  viagens: number;
  receita: number;
  combustivel: number;
  manutencao: number;
  outras_despesas: number;
  lucro: number;
  margem: number | null;
  km_rodados: number;
  custo_km: number | null;
}

export interface ResumoFinanceiro {
  inicio: string;
  fim: string;
  receita_total: number;
  despesa_total: number;
  lucro_total: number;
  a_pagar_aberto: number;
  a_receber_aberto: number;
  vencidas_pagar: number;
  vencidas_receber: number;
  veiculos: RentabilidadeVeiculo[];
}

export const ORIGEM_LABEL: Record<OrigemConta, string> = {
  abastecimento: "Abastecimento",
  manutencao: "Manutenção",
  frete: "Frete",
  manual: "Manual",
};
