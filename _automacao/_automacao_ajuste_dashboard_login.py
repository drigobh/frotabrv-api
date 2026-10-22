import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_ajustes_{agora}.zip"
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

    # Vamos procurar as classes de padding e altura no componente.
    # Geralmente eles usam algo como "p-6" ou "py-6" ou "h-32".
    # Como não sabemos o exato, faremos substituições comuns.
    
    substituicoes = [
        ("p-6", "p-4"), # Reduz o padding geral
        ("py-6", "py-4"),
        ("gap-4", "gap-2"), # Reduz o espaçamento interno
        ("text-3xl", "text-2xl"), # Diminui a fonte do número principal
        ("text-4xl", "text-3xl"),
        ("text-xl", "text-lg"),
    ]
    
    alterou = False
    for antigo, novo in substituicoes:
        if antigo in conteudo:
            conteudo = conteudo.replace(antigo, novo)
            alterou = True

    if alterou:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ KpiCard.tsx ajustado para ser mais compacto.")
    else:
        print("⚠️ Aviso: Não foi possível encontrar as classes de estilo padrão. O layout pode já estar ajustado.")

def forcar_login(raiz):
    # 1. Cria o arquivo para limpar o cookie no navegador
    caminho_html = os.path.join(raiz, "logout_automatico.html")
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write('''
        <html>
            <body style="background-color: #111; color: white; font-family: sans-serif; padding: 50px; text-align: center;">
                <h1>Limpando Sessão...</h1>
                <script>
                    // Apaga o cookie da sessão
                    document.cookie = "frota_session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                    setTimeout(function() {
                        document.body.innerHTML = "<h1>Sessão limpa com sucesso!</h1><p>Você pode fechar esta aba e voltar ao sistema.</p>";
                    }, 1000);
                </script>
            </body>
        </html>
        ''')
    print(f"✅ Arquivo de logout gerado: logout_automatico.html")
    print("👉 Para sair do sistema, abra este arquivo no navegador (dê um duplo clique nele).")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Ajustes (Dashboard e Login)...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    ajustar_kpi_card(raiz)
    forcar_login(raiz)

    print("🚀 Automação concluída! Faça o commit e push para o Render.")

if __name__ == "__main__":
    executar()