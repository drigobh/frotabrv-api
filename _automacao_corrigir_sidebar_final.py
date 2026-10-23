import os
import re
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_rapido_sidebar_final_{agora}.zip"
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pasta_front = os.path.join(raiz, "frontend", "src")
        for root, dirs, files in os.walk(pasta_front):
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', 'build']]
            for file in files:
                caminho_completo = os.path.join(root, file)
                caminho_relativo = os.path.relpath(caminho_completo, raiz)
                try:
                    zipf.write(caminho_completo, caminho_relativo)
                except Exception:
                    pass

def corrigir_sidebar(raiz):
    caminho_sidebar = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    
    if not os.path.exists(caminho_sidebar):
        print("❌ Arquivo Sidebar.tsx não encontrado.")
        return

    with open(caminho_sidebar, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Encontra e remove qualquer linha de import quebrada do lucide-react
    # O padrão busca por "import" seguido de qualquer coisa e "from lucide-react"
    padrao_import = re.compile(r'import\s*\{[^}]*\}\s*from\s*["\']lucide-react["\'];?', re.DOTALL)
    
    # Extrai os ícones que já estavam sendo importados (para não perder nenhum)
    # Busca todos os blocos de import do lucide e junta os nomes
    import_blocks = padrao_import.findall(conteudo)
    icones_existentes = set()
    for block in import_blocks:
        # Extrai o que está entre { e }
        match = re.search(r'\{(.*?)\}', block, re.DOTALL)
        if match:
            # Limpa, remove quebras de linha, divide por vírgula e adiciona ao set
            nomes = match.group(1).replace('\n', ' ').split(',')
            for nome in nomes:
                nome_limpo = nome.strip()
                if nome_limpo:
                    icones_existentes.add(nome_limpo)
    
    # Remove todos os imports antigos do lucide-react do conteúdo
    conteudo = padrao_import.sub('', conteudo)
    
    # Adiciona os ícones que precisamos
    icones_existentes.add("Database")
    icones_existentes.add("Menu")
    icones_existentes.add("Truck")
    
    # Monta a nova linha de import do lucide-react
    icones_ordenados = sorted(list(icones_existentes))
    novo_import = f'import {{ {", ".join(icones_ordenados)} }} from "lucide-react";\n'
    
    # Insere o novo import no topo do arquivo (após o primeiro import de react)
    if "import" in conteudo:
        # Adiciona no início, que é seguro
        conteudo = novo_import + conteudo
    else:
        conteudo = novo_import + conteudo

    # 2. Adiciona o link para a Base, se não existir
    if "/admin/base" not in conteudo:
        # Procura a seção "GESTÃO" ou "ADMINISTRAÇÃO" ou um link existente para ancorar
        linhas = conteudo.split('\n')
        ancora_encontrada = False
        
        for i, linha in enumerate(linhas):
            # Procura por um link existente para se ancorar (Usuarios, Auditoria, etc.)
            if 'to="/usuarios"' in linha or 'to="/auditoria"' in linha or 'to="/seguranca"' in linha or 'to="/ranking"' in linha:
                indentacao = linha[:len(linha) - len(linha.lstrip())]
                link_base = f'''{indentacao}<Link
{indentacao}  to="/admin/base"
{indentacao}  className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-400 hover:bg-slate-800 hover:text-slate-100"
{indentacao}>
{indentacao}  <Database className="size-4" />
{indentacao}  <span>Base</span>
{indentacao}</Link>'''
                linhas.insert(i + 1, link_base)
                ancora_encontrada = True
                print(f"✅ Link 'Base' inserido após o link da linha {i+1}.")
                break
        
        if not ancora_encontrada:
            # Se não achar âncora, adiciona no final do componente Sidebar (antes do último return)
            # Essa é uma solução de emergência, mas funcional
            print("⚠️ Não foi encontrada âncora. O link não foi inserido. Verifique o Sidebar.tsx.")
            return
            
        conteudo = '\n'.join(linhas)

    with open(caminho_sidebar, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✅ Arquivo Sidebar.tsx corrigido com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    print("🤖 Iniciando Correção Definitiva do Sidebar...")
    criar_backup_rapido(raiz)
    corrigir_sidebar(raiz)
    print("\n🚀 Concluído! Reinicie o Vite para testar.")