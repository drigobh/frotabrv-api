import { ApiError } from "./api";

const MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];

export const brl = (v: any): string => {
  const num = Number(v);
  if (isNaN(num)) return "R$ 0,00";
  return num.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
};

export const num = (v: number, d = 0) =>
  v.toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d });

export const dataBR = (ymd?: string | null) => (ymd ? ymd.slice(0, 10).split("-").reverse().join("/") : "—");

export const dataHoraBR = (iso: string) =>
  new Date(iso).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

export const mesCurto = (ym: string) => {
  const [y, m] = ym.split("-");
  return `${MESES[Number(m) - 1]}/${y.slice(2)}`;
};

// Mensagem amigável a partir de qualquer erro da API (detail string ou lista 422).
export function errMsg(e: unknown): string {
  if (e instanceof ApiError) {
    const detail = (e.body as { detail?: unknown } | null)?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: string; loc?: (string | number)[] };
      const campo = first.loc ? String(first.loc[first.loc.length - 1]) : "campo";
      return `Campo inválido (${campo}): ${first.msg ?? ""}`;
    }
    return `Erro ${e.status}`;
  }
  return "Falha de conexão com o servidor";
}
