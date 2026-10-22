// Períodos derivados do "hoje" do servidor (YYYY-MM-DD) — sem relógio do navegador.
const toYmd = (d: Date) => d.toISOString().slice(0, 10);
const fromYmd = (ymd: string) => new Date(`${ymd}T00:00:00Z`);

export const addDias = (ymd: string, n: number) => {
  const d = fromYmd(ymd);
  d.setUTCDate(d.getUTCDate() + n);
  return toYmd(d);
};

export const inicioMes = (ymd: string) => `${ymd.slice(0, 7)}-01`;

export function mesAnterior(ymd: string): [string, string] {
  const fim = addDias(inicioMes(ymd), -1);
  return [inicioMes(fim), fim];
}

export interface Preset {
  id: string;
  label: string;
  range: (hoje: string) => [string, string];
}

export const PRESETS: Preset[] = [
  { id: "mes", label: "Este mês", range: (h) => [inicioMes(h), h] },
  { id: "anterior", label: "Mês passado", range: mesAnterior },
  { id: "90d", label: "Últimos 90 dias", range: (h) => [addDias(h, -89), h] },
  { id: "6m", label: "Últimos 6 meses", range: (h) => [inicioMes(addDias(inicioMes(h), -150)), h] },
];
