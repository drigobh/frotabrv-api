// Espelha backend/models/cadastros.py
export interface Veiculo {
  id: string;
  placa: string;
  modelo: string;
  ano: number;
  hodometro_km: number;
  observacoes: string;
  ativo: boolean;
  acoplado: boolean;
  created_at: string;
}

export interface Carreta {
  id: string;
  codigo: string;
  tipo: string;
  observacoes: string;
  ativo: boolean;
  acoplado: boolean;
  created_at: string;
}

export interface Motorista {
  id: string;
  nome: string;
  cnh: string;
  categoria_cnh: string;
  validade_cnh: string | null;
  telefone: string;
  email: string;
  observacoes: string;
  ativo: boolean;
  acoplado: boolean;
  created_at: string;
}
