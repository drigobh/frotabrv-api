import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_card_final_{agora}.zip"
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

def forcar_card_ultra_compacto(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "dashboard", "KpiCard.tsx")
    
    # Código do card reformulado, compacto e com estilos forçados
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
  const hasSerie = kpi.serie && kpi.serie.length > 0;

  return (
    <article 
      className="glass relative overflow-hidden rounded-xl" 
      style={{ 
        padding: '12px 16px', 
        height: '90px', 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'space-between' 
      }}
      data-testid={`kpi-${kpi.chave}`}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{ 
          display: 'flex', alignItems: 'center', justifyContent: 'center', 
          width: '28px', height: '28px', borderRadius: '8px', 
          backgroundColor: `${color}20`, color: color 
        }}>
          <Icon size={16} />
        </div>
        <p style={{ fontSize: '12px', color: '#94a3b8', margin: 0, fontWeight: 500 }}>
          {kpi.titulo}
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div>
          <p 
            style={{ fontSize: '22px', fontWeight: 600, color: '#f8fafc', margin: 0, lineHeight: 1 }}
            data-testid={`kpi-${kpi.chave}-value`}
          >
            {format(kpi.valor)}
          </p>
          <p
            style={{ 
              fontSize: '10px', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '2px',
              color: t == null || t === 0 ? "#64748b" : t > 0 ? "#10b981" : "#ef4444" 
            }}
            data-testid={`kpi-${kpi.chave}-trend`}
          >
            <Trend size={12} />
            {t == null ? "sem base" : `${t > 0 ? "+" : ""}${t}%`}
          </p>
        </div>

        {hasSerie && (
          <div style={{ width: '60px', height: '30px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={kpi.serie}>
                <Area type="monotone" dataKey="valor" stroke={color} strokeWidth={2} fill={`${color}20`} isAnimationActive={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </article>
  );
}
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo_novo)
    print("⚙️ KpiCard.tsx reescrito para um layout ultra compacto e moderno.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Estilo Final dos Cards...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    forcar_card_ultra_compacto(raiz)

    print("🚀 Automação concluída! Reinicie o frontend (yarn dev).")

if __name__ == "__main__":
    executar()