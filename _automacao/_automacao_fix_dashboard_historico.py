import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_fix_hist_dash_{agora}.zip"
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

def corrigir_dashboard_historico(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "dashboard.py")
    if not os.path.exists(caminho):
        print("❌ Erro: dashboard.py não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Adiciona a importação do HistoricoItem (se não estiver lá)
    if "from models.acoplamentos import HistoricoItem" not in conteudo:
        conteudo = conteudo.replace(
            "from models.dashboard import Dashboard, Kpi, StatusFrota, CustoMes, Campeoes",
            "from models.dashboard import Dashboard, Kpi, StatusFrota, CustoMes, Campeoes\nfrom models.acoplamentos import HistoricoItem"
        )

    # 2. Adiciona a busca do histórico antes do return
    busca = "    campeoes = Campeoes(mes_atual=c_atual, mes_passado=c_ant)"
    novo = """    campeoes = Campeoes(mes_atual=c_atual, mes_passado=c_ant)
    
    # Busca as últimas 5 movimentações de acoplamento
    hist_docs = await db.acoplamentos_historico.find({}, {"_id": 0}).sort("created_at", -1).to_list(5)
    historico_recente = [HistoricoItem(**h) for h in hist_docs]"""

    if busca in conteudo:
        conteudo = conteudo.replace(busca, novo)
    else:
        print("⚠️ Aviso: A linha de campeões não foi encontrada. O arquivo pode ser diferente do esperado.")

    # 3. Substitui o historico_recente=[] pelo historico_recente
    if "historico_recente=[]" in conteudo:
        conteudo = conteudo.replace("historico_recente=[]", "historico_recente=historico_recente")
    else:
        print("⚠️ Aviso: O campo historico_recente=[] não foi encontrado no return.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ dashboard.py atualizado para incluir o histórico de acoplamentos!")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção do Histórico no Dashboard...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_dashboard_historico(raiz)

    print("🚀 Automação concluída! Faça o commit e push para o Render.")

if __name__ == "__main__":
    executar()