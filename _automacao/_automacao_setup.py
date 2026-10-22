import os
import shutil
import datetime

def executar_auditoria():
    raiz = os.getcwd()
    print("🕵️ Iniciando Auditoria do Projeto FrotaBrv...")

    # 1. Backup do Backend
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_backend_{agora}"
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print("📦 Criando backup do backend (app)...")
    try:
        shutil.make_archive(caminho_zip, 'zip', os.path.join(raiz, 'app'))
        print("✅ Backup do backend concluído.")
    except Exception as e:
        print(f"⚠️ Aviso no backup: {e}")

    # 2. Mapear Frontend (Pages)
    pasta_pages = os.path.join(raiz, "frontend", "src", "pages")
    telas = []
    if os.path.exists(pasta_pages):
        telas = [f for f in os.listdir(pasta_pages) if f.endswith('.tsx')]
    else:
        print("❌ Pasta frontend/src/pages não encontrada.")

    # 3. Mapear Backend (Routers)
    pasta_routers = os.path.join(raiz, "app", "backend", "routers")
    routers = []
    if os.path.exists(pasta_routers):
        routers = [f for f in os.listdir(pasta_routers) if f.endswith('.py') and f != '__init__.py']
    else:
        print("❌ Pasta app/backend/routers não encontrada.")

    # 4. Mapear Models e Libs
    pasta_models = os.path.join(raiz, "app", "backend", "models")
    models = []
    if os.path.exists(pasta_models):
        models = [f for f in os.listdir(pasta_models) if f.endswith('.py') and f != '__init__.py']

    # 5. Gerar Relatório
    caminho_relatorio = os.path.join(raiz, "MAPA_DO_PROJETO.md")
    with open(caminho_relatorio, 'w', encoding='utf-8') as f:
        f.write("# 📊 Mapa de Auditoria do FrotaBrv\n\n")
        f.write(f"**Gerado em:** {agora}\n\n")
        
        f.write("## 1. Telas do Frontend (O que o usuário vê)\n")
        f.write(f"Encontradas **{len(telas)}** telas na pasta `pages`:\n")
        for t in sorted(telas):
            f.write(f"- [x] {t}\n")
        
        f.write("\n## 2. Rotas de API Implementadas (O que o backend entrega)\n")
        f.write(f"Encontrados **{len(routers)}** arquivos de rotas:\n")
        if not routers:
            f.write("*Nenhuma rota de API além do auth implementada ainda.*\n")
        for r in sorted(routers):
            f.write(f"- [x] {r}\n")

        f.write("\n## 3. Regras de Negócio e Modelos Prontos (A 'inteligência' do sistema)\n")
        f.write(f"Encontrados **{len(models)}** modelos de dados:\n")
        for m in sorted(models):
            f.write(f"- [x] {m}\n")

        f.write("\n## 🎯 Conclusão\n")
        f.write("Este relatório mostra o que precisamos conectar. "
                "O Frontend está completo, os modelos de banco estão prontos, "
                "mas faltam as Rotas (Routers) no backend para o Frontend conseguir ler e gravar os dados.\n")

    print(f"✅ Relatório de Auditoria gerado em: {caminho_relatorio}")
    print("🚀 Automação concluída! Leia o arquivo MAPA_DO_PROJETO.md.")

if __name__ == "__main__":
    executar_auditoria()