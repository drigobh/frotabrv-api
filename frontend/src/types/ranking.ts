// Espelha backend/models/ranking.py
export interface MetaIn {
  meta_km_l: number;
}

export interface RankingItem {
  posicao: number;
  motorista_id: string;
  motorista_nome: string;
  abastecimentos: number;
  litros: number;
  km_rodados: number;
  media_km_l: number;
  percentual_meta: number;
  atingiu_meta: boolean;
}

export interface Ranking {
  mes: string;
  meta_km_l: number;
  media_frota: number | null;
  itens: RankingItem[];
}

export interface ParabensEnvio {
  mes: string;
  enviado_em: string;
  origem: "agendado" | "manual";
  motorista_email: string | null;
  destinatarios: string[];
  enviados: number;
  falhas: string[];
}

export interface CampeaoMes {
  mes: string;
  motorista_id: string;
  motorista_nome: string;
  media_km_l: number;
  km_rodados: number;
  meta_km_l: number;
  atingiu_meta: boolean;
  participantes: number;
  vice_nome: string | null;
  vice_media: number | null;
  parabens: ParabensEnvio | null;
}

export interface PlacarItem {
  motorista_id: string;
  motorista_nome: string;
  vitorias: number;
  meses: string[];
  melhor_media: number;
}

export interface HistoricoCampeoes {
  meses: CampeaoMes[];
  placar: PlacarItem[];
}
