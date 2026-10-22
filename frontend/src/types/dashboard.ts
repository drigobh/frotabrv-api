// Espelha backend/models/dashboard.py
import type { HistoricoItem } from "./acoplamentos";

export interface SeriePonto {
  mes: string;
  valor: number;
}

export interface Kpi {
  chave: "veiculos" | "motoristas" | "acoplamentos" | "km";
  titulo: string;
  valor: number;
  tendencia: number | null;
  serie: SeriePonto[];
}

export interface StatusFrota {
  acoplados: number;
  disponiveis: number;
  em_manutencao: number;
  inativos: number;
}

export interface CustoMes {
  mes: string;
  combustivel: number;
  manutencao: number;
}

export interface Alerta {
  tipo: "manutencao" | "cnh" | "documento";
  titulo: string;
  detalhe: string;
  severidade: "alta" | "media";
}

export interface Campeao {
  mes: string;
  motorista_nome: string;
  media_km_l: number;
  km_rodados: number;
  meta_km_l: number;
  atingiu_meta: boolean;
  participantes: number;
}

export interface Campeoes {
  mes_passado: Campeao | null;
  mes_atual: Campeao | null;
}

export interface Dashboard {
  kpis: Kpi[];
  status_frota: StatusFrota;
  custos: CustoMes[];
  alertas: Alerta[];
  historico_recente: HistoricoItem[];
  campeoes: Campeoes;
}
