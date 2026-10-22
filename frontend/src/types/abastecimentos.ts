// Espelha backend/models/abastecimentos.py
export interface AbastecimentoCreate {
  data: string;
  veiculo_id: string;
  motorista_id: string | null;
  litros: number;
  preco_litro: number;
  posto: string;
  km: number;
  observacoes: string;
}

export interface Abastecimento extends AbastecimentoCreate {
  id: string;
  valor_total: number;
  km_rodados: number | null;
  media_km_l: number | null;
  veiculo_label: string;
  motorista_label: string | null;
  created_by: string;
  created_at: string;
}
