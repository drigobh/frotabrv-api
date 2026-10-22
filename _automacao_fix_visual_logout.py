import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_fix_logout_{agora}.zip"
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

def ajustar_kpi_card(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "dashboard", "KpiCard.tsx")
    if not os.path.exists(caminho):
        print("❌ Erro: KpiCard.tsx não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Alterações cirúrgicas para diminuir a altura
    conteudo = conteudo.replace('rounded-2xl p-5"', 'rounded-2xl p-4"') # Reduz o padding geral
    conteudo = conteudo.replace('mt-2 font-heading text-3xl', 'mt-1 font-heading text-2xl') # Diminui margem e fonte
    conteudo = conteudo.replace('<div className="mt-3 h-12">', '<div className="mt-2 h-8">') # Reduz a altura do gráfico

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ KpiCard.tsx ajustado (cards mais compactos).")

def corrigir_logout_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "auth.py")
    if not os.path.exists(caminho):
        print("❌ Erro: auth.py não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Adiciona a rota de GET logout (para ser acessada via link no navegador)
    if '@router.get("/logout")' not in conteudo:
        rota_logout = '''
@router.get("/logout")
async def logout_get(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True, "msg": "Sessão encerrada."}
'''
        conteudo += rota_logout
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ Backend: Rota de GET /logout criada.")
    else:
        print("✅ Backend: Rota de logout já existe.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção (Visual e Logout)...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    ajustar_kpi_card(raiz)
    corrigir_logout_backend(raiz)

    print("🚀 Automação concluída! Faça o commit e push para o Render.")

if __name__ == "__main__":
    executar()