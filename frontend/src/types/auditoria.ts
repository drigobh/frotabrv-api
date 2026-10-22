// Espelha backend/models/auditoria.py
export interface AuditoriaItem {
  id: string;
  usuario_nome: string;
  acao: string;
  entidade: string;
  entidade_id: string | null;
  detalhes: string;
  ip: string | null;
  created_at: string;
}
