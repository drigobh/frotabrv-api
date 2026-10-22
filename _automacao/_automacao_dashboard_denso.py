import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_dash_denso_{agora}.zip"
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

def ajustar_css(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "index.css")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Remove as regras antigas que forçavam a altura e adiciona a correção do glass
    regras_antigas = '''
/* FORÇAR TAMANHO DOS CARDS DO DASHBOARD */
article[data-testid^="kpi-"] {
    padding: 12px !important;
    height: 120px !important;
    max-height: 120px !important;
}
article[data-testid^="kpi-"] p.font-heading {
    font-size: 24px !important;
    margin-top: 4px !important;
}
article[data-testid^="kpi-"] .mt-1.h-6 {
    height: 32px !important;
    margin-top: 8px !important;
}
'''
    if regras_antigas in conteudo:
        conteudo = conteudo.replace(regras_antigas, "")

    novas_regras = '''
/* CORREÇÃO DO CARD DO DASHBOARD */
article[data-testid^="kpi-"] {
    min-height: auto !important;
}
'''
    if "CORREÇÃO DO CARD" not in conteudo:
        conteudo += novas_regras

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ index.css atualizado (removendo min-height forçado).")

def ajustar_kpicard(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "dashboard", "KpiCard.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Ajuste para renderizar o gráfico apenas se houver série de dados
    bloco_grafico = '''      <div style={{ flex: 1, minHeight: '30px', marginTop: '4px' }}>
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
      </div>'''

    bloco_novo = '''      {kpi.serie && kpi.serie.length > 0 ? (
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
      ) : (
        <div style={{ flex: 1, minHeight: '10px', marginTop: '4px' }} />
      )}'''

    if bloco_grafico in conteudo:
        conteudo = conteudo.replace(bloco_grafico, bloco_novo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ KpiCard.tsx ajustado para esconder o gráfico quando não houver dados.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Dashboard Denso...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    ajustar_css(raiz)
    ajustar_kpicard(raiz)

    print("🚀 Automação concluída! Reinicie o frontend.")

if __name__ == "__main__":
    executar()