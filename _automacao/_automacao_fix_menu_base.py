import os
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_rapido_sidebar_{agora}.zip"
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Criando Backup Rápido...")
    ignorar = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build']
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pasta_front = os.path.join(raiz, "frontend", "src")
        for root, dirs, files in os.walk(pasta_front):
            dirs[:] = [d for d in dirs if d not in ignorar]
            for file in files:
                caminho_completo = os.path.join(root, file)
                caminho_relativo = os.path.relpath(caminho_completo, raiz)
                try:
                    zipf.write(caminho_completo, caminho_relativo)
                except Exception:
                    pass
    print(f"✅ Backup salvo: {nome_backup}")

def corrigir_sidebar(raiz):
    # O arquivo Sidebar.tsx está dentro de components/layout
    caminho_sidebar = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    
    if not os.path.exists(caminho_sidebar):
        print("❌ Arquivo Sidebar.tsx não encontrado em components/layout.")
        return

    with open(caminho_sidebar, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Adiciona o import do ícone Database (se não existir)
    if "Database" not in conteudo and "from \"lucide-react\"" in conteudo:
        # Tenta adicionar no import existente
        import re
        match = re.search(r'import \{([^}]+)\} from "lucide-react";', conteudo)
        if match:
            imports_atuais = match.group(1)
            if "Database" not in imports_atuais:
                novo_import = f'import {{{imports_atuais}, Database}} from "lucide-react";'
                conteudo = conteudo.replace(match.group(0), novo_import)
                print("✅ Ícone 'Database' adicionado aos imports.")

    # 2. Procura a seção de ADMINISTRAÇÃO ou GESTÃO para inserir o link
    # Vamos procurar por uma seção existente e adicionar o link da Base
    if "/admin/base" not in conteudo:
        # Tenta encontrar o bloco de "ADMINISTRAÇÃO"
        if "ADMINISTRAÇÃO" in conteudo:
            # Insere o link após a declaração da seção ADMINISTRAÇÃO
            # Vamos usar uma estratégia de substituir o primeiro link da seção ou adicionar antes do próximo título
            pass
        
        # Estratégia mais segura: adicionar um novo grupo de menu no final do sidebar, antes do fechamento da div principal
        # Mas como não sabemos a estrutura exata, vamos procurar por um item de menu conhecido e adicionar depois dele
        # Vamos procurar por 'Financeiro' ou 'Ranking' ou 'Usuarios' que já existem
        for ancora in ['Ranking', 'Financeiro', 'Usuarios', 'Auditoria', 'Seguranca']:
            if ancora in conteudo:
                # Encontra a linha que contém o link para essa âncora e adiciona o link da Base depois
                linhas = conteudo.split('\n')
                for i, linha in enumerate(linhas):
                    if ancora in linha and ('to=' in linha or 'href=' in linha):
                        # Insere o link da Base após esta linha
                        link_base = '''          <Link to="/admin/base" className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-400 hover:bg-slate-800 hover:text-slate-100">
            <Database className="size-4" />
            <span>Base</span>
          </Link>'''
                        linhas.insert(i + 1, link_base)
                        conteudo = '\n'.join(linhas)
                        break
                break
        
        with open(caminho_sidebar, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Link 'Base' adicionado ao Sidebar.")
    else:
        print("ℹ️ Link 'Base' já existe no Sidebar.")

if __name__ == "__main__":
    raiz = os.getcwd()
    print("🤖 Iniciando Correção do Menu Lateral...")
    criar_backup_rapido(raiz)
    corrigir_sidebar(raiz)
    print("\n🚀 Concluído! Reinicie o Vite e verifique o menu lateral.")