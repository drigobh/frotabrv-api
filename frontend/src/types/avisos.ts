// Espelha backend/models/avisos.py
export interface AvisoItem {
  categoria: "documento" | "cnh" | "pagar" | "receber";
  titulo: string;
  detalhe: string;
  data: string;
  dias: number;
  valor: number | null;
}

export interface AvisoResumo {
  gerado_em: string;
  ate: string;
  documentos: AvisoItem[];
  contas_pagar: AvisoItem[];
  contas_receber: AvisoItem[];
  total_pagar: number;
  total_receber: number;
}

export interface AvisoConfigIn {
  emails_extras: string[];
}

export interface AvisoConfig {
  emails_extras: string[];
  admins: string[];
  destinatarios: string[];
}

export interface AvisoEnvio {
  id: string;
  origem: "agendado" | "manual";
  enviado_em: string;
  destinatarios: string[];
  enviados: number;
  falhas: string[];
  itens: number;
  usuario: string | null;
}
