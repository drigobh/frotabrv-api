import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_card_inline_{agora}.zip"
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Criando Backup Full do Sistema...")
    ignorar = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build']
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta_alvo in ['app', 'frontend']:
            caminho_pasta = os.path.join(raiz, pasta_alvo)
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ignorar]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try:
                        zipf.write(caminho_completo, caminho_relativo)
                    except Exception:
                        pass
    print(f"✅ Backup Full salvo em: _automacao/backups/{nome_backup}")

def forcar_card_inline(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "dashboard", "KpiCard.tsx")
    if not os.path.exists(caminho):
        print("❌ Erro: KpiCard.tsx não encontrado.")
        return

    # Código com estilos inline (style={{...}})
    codigo_novo = '''import { ArrowDownRight, ArrowUpRight, Minus, type LucideIcon } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer } from "recharts";
import type { Kpi } from "@/types/dashboard";
import { cn } from "@/lib/utils";

interface Props {
  kpi: Kpi;
  icon: LucideIcon;
  format: (v: number) => string;
  color: string;
}

export function KpiCard({ kpi, icon: Icon, format, color }: Props) {
  const t = kpi.tendencia;
  const Trend = t == null || t === 0 ? Minus : t > 0 ? ArrowUpRight : ArrowDownRight;
  return (
    <article 
      className="glass lift relative overflow-hidden rounded-xl" 
      style={{ padding: '12px', height: '110px', display: 'flex', flexDirection: 'column' }}
      data-testid={`kpi-${kpi.chave}`}
    >
      <div className="flex items-start justify-between">
        <p className="text-xs text-slate-400">{kpi.titulo}</p>
        <Icon className="size-3.5 text-slate-500" />
      </div>
      <p 
        className="font-heading font-semibold tabular-nums text-slate-50" 
        style={{ fontSize: '24px', marginTop: '4px', lineHeight: '1.2' }}
        data-testid={`kpi-${kpi.chave}-value`}
      >
        {format(kpi.valor)}
      </p>
      <p
        className={cn(
          "inline-flex items-center gap-1 text-[10px]",
          t == null || t === 0 ? "text-slate-500" : t > 0 ? "text-emerald-400" : "text-red-400",
        )}
        style={{ marginTop: '2px' }}
        data-testid={`kpi-${kpi.chave}-trend`}
      >
        <Trend className="size-3" />
        {t == null ? "sem base anterior" : `${t > 0 ? "+" : ""}${t.toLocaleString("pt-BR")}% vs anterior`}
      </p>
      <div style={{ flex: 1, minHeight: '30px', marginTop: '4px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={kpi.serie} margin={{ top: 2, right: 0, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id={`spark-${kpi.chave}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.35} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area type="monotone" dataKey="valor" stroke={color} strokeWidth={2} fill={`url(#spark-${kpi.chave})`} isAnimationActive={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </article>
  );
}
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo_novo)
    print("⚙️ KpiCard.tsx reescrito com estilos inline forçados.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Estilo Forçado (Inline)...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    forcar_card_inline(raiz)

    print("🚀 Automação concluída! Reinicie o frontend (yarn dev) para testar.")

if __name__ == "__main__":
    executar()