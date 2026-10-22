// Espelha backend/models/usuarios.py e backend/models/auth.py
export type Perfil = "admin" | "operador";

export interface Usuario {
  id: string;
  nome: string;
  email: string;
  perfil: Perfil;
  ativo: boolean;
  totp_enabled: boolean;
  created_at: string;
}

export interface LoginOut {
  requires_2fa: boolean;
  user: Usuario | null;
}

export interface TwoFASetupOut {
  secret: string;
  otpauth_url: string;
  qr_code: string;
}

export interface OkOut {
  ok: boolean;
}

export interface ApiRoot {
  message: string;
  status: string;
  hoje: string;
}
