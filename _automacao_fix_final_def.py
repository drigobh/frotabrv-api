import os

def fix_backend(raiz):
    # 1. Garantir que o Modelo LoginOut tenha o campo token
    model_path = os.path.join(raiz, "app", "backend", "models", "auth.py")
    with open(model_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'class LoginOut' in c and 'token:' not in c:
        c = c.replace('class LoginOut(BaseModel):', 'class LoginOut(BaseModel):\n    token: str | None = None')
        with open(model_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Modelo LoginOut atualizado com campo 'token'.")

    # 2. Retornar o token no Router de Auth
    router_path = os.path.join(raiz, "app", "backend", "routers", "auth.py")
    with open(router_path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if 'return LoginOut(requires_2fa=False, user=user)' in c:
        c = c.replace(
            'return LoginOut(requires_2fa=False, user=user)',
            'return LoginOut(requires_2fa=False, user=user, token=token)'
        )
        with open(router_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota de login agora retorna o token no corpo.")
    else:
        print("ℹ️ Backend: Rota já retorna o token ou estrutura diferente.")

def fix_frontend(raiz):
    # 1. Atualizar api.ts para usar o token do localStorage
    api_path = os.path.join(raiz, "frontend", "src", "lib", "api.ts")
    codigo_api = '''const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:3000/api";

export class ApiError extends Error {
  public status: number;
  public body: any;
  constructor(status: number, body: any, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

function getHeaders() {
  const token = localStorage.getItem("token") || localStorage.getItem("auth_token");
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const msg = errorData.detail || errorData.message || `Erro ${res.status}`;
    throw new ApiError(res.status, errorData, typeof msg === "string" ? msg : "Erro na requisição");
  }
  if (res.status === 204) return {} as T;
  return res.json();
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { headers: getHeaders(), credentials: "include" });
  return handleResponse<T>(res);
}
export async function apiPost<T>(path: string, body?: any): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { method: "POST", headers: getHeaders(), body: body ? JSON.stringify(body) : undefined, credentials: "include" });
  return handleResponse<T>(res);
}
export async function apiPut<T>(path: string, body?: any): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { method: "PUT", headers: getHeaders(), body: body ? JSON.stringify(body) : undefined, credentials: "include" });
  return handleResponse<T>(res);
}
export async function apiPatch<T>(path: string, body?: any): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { method: "PATCH", headers: getHeaders(), body: body ? JSON.stringify(body) : undefined, credentials: "include" });
  return handleResponse<T>(res);
}
export async function apiDelete<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { method: "DELETE", headers: getHeaders(), credentials: "include" });
  return handleResponse<T>(res);
}
'''
    with open(api_path, 'w', encoding='utf-8') as f:
        f.write(codigo_api)
    print("✅ Frontend: api.ts reescrito para usar token do localStorage.")

    # 2. Atualizar Login.tsx para salvar o token
    login_path = os.path.join(raiz, "frontend", "src", "pages", "Login.tsx")
    with open(login_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'localStorage.setItem("token", r.token)' not in c:
        c = c.replace(
            'beginSession();',
            'if (r.token) { localStorage.setItem("token", r.token); localStorage.setItem("auth_token", r.token); }\n      beginSession();'
        )
        with open(login_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Frontend: Login.tsx agora salva o token no localStorage.")

def fix_dashboard(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Dashboard.tsx")
    codigo = r'''import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Truck, Fuel, Wrench, TrendingUp, AlertTriangle, Activity, Gauge, Calendar, Droplets } from "lucide-react";
import { apiGet } from "@/lib/api";
import { brl, num } from "@/lib/format";
import { PageHeader } from "@/components/common/PageHeader";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import { useMe } from "@/hooks/useSession";
import { FieldSelect } from "@/components/common/FieldSelect";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function Dashboard() {
  const { data: me } = useMe();
  const [dataInicio, setDataInicio] = useState("");
  const [dataFim, setDataFim] = useState("");
  const [filtroVeiculo, setFiltroVeiculo] = useState("__all__");
  const [filtroMotorista, setFiltroMotorista] = useState("__all__");

  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: motoristas = [] } = useQuery({ queryKey: ["motoristas"], queryFn: () => apiGet<any[]>("/motoristas") });
  const { data: abastecimentos = [], isLoading: loadAb } = useQuery({ queryKey: ["abastecimentos"], queryFn: () => apiGet<any[]>("/abastecimentos"), staleTime: 0 });
  const { data: manutencoes = [], isLoading: loadMan } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes"), staleTime: 0 });

  const filteredData = useMemo(() => {
    let fAbast = abastecimentos;
    let fManut = manutencoes;
    if (dataInicio) { fAbast = fAbast.filter(a => a.data >= dataInicio); fManut = fManut.filter(m => m.data >= dataInicio); }
    if (dataFim) { fAbast = fAbast.filter(a => a.data <= dataFim); fManut = fManut.filter(m => m.data <= dataFim); }
    if (filtroVeiculo !== "__all__") { fAbast = fAbast.filter(a => a.veiculo_id === filtroVeiculo); fManut = fManut.filter(m => m.veiculo_id === filtroVeiculo); }
    if (filtroMotorista !== "__all__") { fAbast = fAbast.filter(a => a.motorista_id === filtroMotorista); fManut = fManut.filter(m => m.motorista_id === filtroMotorista); }
    return { fAbast, fManut };
  }, [abastecimentos, manutencoes, dataInicio, dataFim, filtroVeiculo, filtroMotorista]);

  const meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];
  const dadosGrafico = useMemo(() => {
    const agrupado: Record<string, { mes: string, abastecimento: number, manutencao: number }> = {};
    const hoje = new Date();
    for (let i = 5; i >= 0; i--) {
      const d = new Date(hoje.getFullYear(), hoje.getMonth() - i, 1);
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
      const label = `${meses[d.getMonth()]}/${d.getFullYear().toString().slice(2)}`;
      agrupado[key] = { mes: label, abastecimento: 0, manutencao: 0 };
    }
    filteredData.fAbast.forEach(a => {
      if (!a.data) return;
      const key = a.data.substring(0, 7);
      if (agrupado[key]) agrupado[key].abastecimento += (Number(a.valor_total) || 0);
    });
    filteredData.fManut.forEach(m => {
      if (!m.data) return;
      const key = m.data.substring(0, 7);
      if (agrupado[key]) agrupado[key].manutencao += (Number(m.custo) || Number(m.valor) || Number(m.valor_total) || 0);
    });
    return Object.values(agrupado);
  }, [filteredData]);

  const topVeiculos = useMemo(() => {
    const ranking: Record<string, { label: string, litros: number, km: number }> = {};
    filteredData.fAbast.forEach(a => {
      const vId = a.veiculo_id;
      if (!vId) return;
      if (!ranking[vId]) ranking[vId] = { label: (a.veiculo_label || "").split(" · ")[0], litros: 0, km: 0 };
      ranking[vId].litros += (Number(a.litros) || 0);
      ranking[vId].km += (Number(a.km_rodados) || 0);
    });
    return Object.values(ranking).map(v => ({ label: v.label, media: v.litros > 0 ? v.km / v.litros : 0 })).sort((a, b) => b.media - a.media).slice(0, 5);
  }, [filteredData]);

  if (loadAb || loadMan) return <div className="p-10 text-center text-slate-500">Carregando indicadores...</div>;

  const totalLitros = filteredData.fAbast.reduce((s, a) => s + (Number(a.litros) || 0), 0);
  const totalAbast = filteredData.fAbast.reduce((s, a) => s + (Number(a.valor_total) || 0), 0);
  const totalManut = filteredData.fManut.reduce((s, m) => s + (Number(m.custo) || Number(m.valor) || Number(m.valor_total) || 0), 0);
  const totalGeral = totalAbast + totalManut;
  const qtdAbast = filteredData.fAbast.length;
  const qtdManut = filteredData.fManut.length;
  const veiculosParados = new Set(filteredData.fManut.filter(m => m.status === "Agendada" || m.status === "Em execução").map(m => m.veiculo_id)).size;
  const kmTotal = filteredData.fAbast.reduce((s, a) => s + (Number(a.km_rodados) || 0), 0);
  const mediaGeral = totalLitros > 0 ? kmTotal / totalLitros : 0;

  const kpis = [
    { label: "Total Abastecido", valor: `${num(totalLitros, 1)} L`, icon: Droplets, color: "#0ea5e9" },
    { label: "Custo Combustível", valor: brl(totalAbast), icon: Fuel, color: "#0284c7" },
    { label: "Custo Manutenção", valor: brl(totalManut), icon: Wrench, color: "#f59e0b" },
    { label: "Custo Total", valor: brl(totalGeral), icon: TrendingUp, color: "#10b981" },
    { label: "Qtd. Abastecimentos", valor: num(qtdAbast), icon: Truck, color: "#8b5cf6" },
    { label: "Qtd. Manutenções", valor: num(qtdManut), icon: Activity, color: "#f43f5e" },
    { label: "Veículos Parados", valor: num(veiculosParados), icon: AlertTriangle, color: "#ef4444" },
    { label: "Média Geral", valor: `${num(mediaGeral, 2)} km/L`, icon: Gauge, color: "#6366f1" },
  ];

  return (
    <div>
      <PageHeader eyebrow="Dashboard" title={`Olá, ${me?.nome?.split(" ")[0] || "Usuário"}`} description="Indicadores da frota, custos e eficiência com filtros dinâmicos." />
      <div className="mb-6 flex flex-wrap gap-3 items-end glass p-4 rounded-xl">
        <div className="grid gap-1"><Label className="text-[10px] uppercase text-slate-500">Data Inicial</Label><Input type="date" value={dataInicio} onChange={e => setDataInicio(e.target.value)} className="w-36 h-9" /></div>
        <div className="grid gap-1"><Label className="text-[10px] uppercase text-slate-500">Data Final</Label><Input type="date" value={dataFim} onChange={e => setDataFim(e.target.value)} className="w-36 h-9" /></div>
        <div className="grid gap-1 w-48"><Label className="text-[10px] uppercase text-slate-500">Veículo</Label><FieldSelect value={filtroVeiculo} onChange={setFiltroVeiculo} options={[{ value: "__all__", label: "Todos" }, ...veiculos.map((v: any) => ({ value: v.id, label: v.placa }))]} /></div>
        <div className="grid gap-1 w-48"><Label className="text-[10px] uppercase text-slate-500">Motorista</Label><FieldSelect value={filtroMotorista} onChange={setFiltroMotorista} options={[{ value: "__all__", label: "Todos" }, ...motoristas.map((m: any) => ({ value: m.id, label: m.nome }))]} /></div>
        <button onClick={() => { setDataInicio(""); setDataFim(""); setFiltroVeiculo("__all__"); setFiltroMotorista("__all__"); }} className="text-sm text-sky-400 hover:underline pb-2 ml-2">Limpar Filtros</button>
      </div>

      <div className="mb-6 grid gap-3 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-4">
        {kpis.map((kpi, i) => (
          <div key={i} className="glass rounded-xl p-3 flex items-center justify-between h-[72px]">
            <div><p className="text-[11px] text-slate-500 font-medium truncate">{kpi.label}</p><p className="text-lg font-bold text-slate-100 mt-0.5 truncate">{kpi.valor}</p></div>
            <div className="size-8 rounded-lg flex items-center justify-center shrink-0 ml-2" style={{ backgroundColor: `${kpi.color}20`, color: kpi.color }}><kpi.icon className="size-4" /></div>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-bold text-slate-200 mb-6 flex items-center gap-2"><Calendar className="size-4 text-sky-400"/> Custos Operacionais (Combustível x Manutenção)</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dadosGrafico}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="mes" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `R$${v/1000}k`} />
                <Tooltip cursor={{ fill: '#1e293b' }} contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }} formatter={(value: any) => brl(value)} />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Bar dataKey="abastecimento" name="Combustível" stackId="a" fill="#0ea5e9" radius={[0, 0, 4, 4]} />
                <Bar dataKey="manutencao" name="Manutenção" stackId="a" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-bold text-slate-200 mb-6 flex items-center gap-2"><TrendingUp className="size-4 text-emerald-400" /> Top 5 Veículos (KM/L)</h3>
          <div className="space-y-4">
            {topVeiculos.length === 0 && <p className="text-sm text-slate-500 text-center py-10">Sem dados suficientes para o período/filtro selecionado.</p>}
            {topVeiculos.map((v: any, i: number) => (
              <div key={i}>
                <div className="flex justify-between text-xs mb-1"><span className="font-medium text-slate-300">{i + 1}º {v.label}</span><span className="font-bold text-emerald-400">{num(v.media, 2)}</span></div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden"><div className="h-full bg-gradient-to-r from-emerald-600 to-emerald-400 rounded-full" style={{ width: `${Math.min((v.media / 5) * 100, 100)}%` }} /></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Frontend: Dashboard.tsx reescrito com cards corretos e cálculo robusto.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)
    fix_dashboard(raiz)