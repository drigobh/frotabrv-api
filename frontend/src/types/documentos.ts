// Espelha backend/models/documentos.py
export type EntidadeDoc = "veiculo" | "motorista";
export type SituacaoDoc = "vigente" | "vencendo" | "vencido";

export interface DocumentoCreate {
  entidade: EntidadeDoc;
  entidade_id: string;
  tipo: string;
  numero: string;
  emissao: string | null;
  validade: string;
  observacoes: string;
}

export interface Documento extends DocumentoCreate {
  id: string;
  entidade_label: string;
  situacao: SituacaoDoc;
  dias_restantes: number;
  created_by: string;
  created_at: string;
}

export const TIPOS_DOC: Record<EntidadeDoc, string[]> = {
  veiculo: ["CRLV", "ANTT / RNTRC", "Seguro", "Tacógrafo", "Licença ambiental", "Outro"],
  motorista: ["MOPP", "Exame toxicológico", "ASO / Exame médico", "Curso de direção defensiva", "Outro"],
};

export const SITUACAO_LABEL: Record<SituacaoDoc, string> = {
  vigente: "Vigente",
  vencendo: "Vencendo",
  vencido: "Vencido",
};
