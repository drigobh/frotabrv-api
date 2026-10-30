import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ORGANIZAR_MENUS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/components/layout/Sidebar.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Trocar o ícone do Cadastro (de Truck para FolderOpen)
    c = c.replace('id: "cadastros", label: "Cadastro", icon: Truck,', 'id: "cadastros", label: "Cadastro", icon: FolderOpen,')

    # 2. Garantir import do FolderOpen
    if 'FolderOpen' not in c.split('lucide-react')[0]:
        c = c.replace('import { ', 'import { FolderOpen, ')

    # 3. Ordenar os menus (exceto Dashboard)
    # Vamos usar um padrão para capturar o bloco do array MENUS
    padrao_menu = re.compile(r'const MENUS = \[[\s\S]*?\];', re.DOTALL)
    match = padrao_menu.search(c)
    
    if match:
        bloco_original = match.group(0)
        
        # Extrai os itens de nível superior (menus principais)
        # O Dashboard é mantido no topo
        dashboard_match = re.search(r'(\{\s*id:\s*"dashboard"[^}]*\},)', bloco_original)
        dashboard_item = dashboard_match.group(1) if dashboard_match else ''
        
        # Extrai os outros menus (blocos que começam com { id: "...)
        # Vamos capturar cada menu completo com seus submenus
        padrao_menus = re.compile(r'(\{[^{}]*?id:\s*"[^"]+"[^{}]*?(?:\{[^{}]*?\})*?[^{}]*?\},?)', re.DOTALL)
        
        # Remove o dashboard do bloco para pegar os outros
        bloco_sem_dashboard = bloco_original.replace(dashboard_item, '')
        
        # Extrai todos os menus (que têm a estrutura { id: ..., label: ..., items: [...] })
        menus = re.findall(r'(\{\s*id:\s*"[^"]+"[\s\S]*?\n\s*\},?)', bloco_sem_dashboard)
        
        # Se não encontrou com regex, tenta uma abordagem mais simples
        if not menus:
            # Abordagem alternativa: divide o bloco por "  }," e junta
            partes = bloco_sem_dashboard.split('  },\n')
            menus = [parte + '  },\n' for parte in partes if 'id:' in parte]
        
        # Ordena os menus pelo label (alfabeticamente)
        def extrair_label(menu_str):
            match = re.search(r'label:\s*"([^"]+)"', menu_str)
            return match.group(1) if match else ''
        
        menus.sort(key=extrair_label)
        
        # Reconstrói o array MENUS
        novo_bloco = 'const MENUS = [\n'
        novo_bloco += '  ' + dashboard_item + '\n'
        
        for menu in menus:
            # Remove vírgulas extras no final
            menu = menu.rstrip().rstrip(',')
            novo_bloco += '  ' + menu + ',\n'
        
        novo_bloco += '];'
        
        # Substitui o bloco antigo pelo novo
        c = c.replace(bloco_original, novo_bloco)
        print("✅ Menus reordenados alfabeticamente.")
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Sidebar.tsx atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")