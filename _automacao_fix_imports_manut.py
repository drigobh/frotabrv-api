import os
import re

def fix_imports(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Manutencoes.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    novas_linhas = []
    lucide_import_idx = -1

    # 1. Encontra a linha do lucide-react e isola os ícones
    for i, linha in enumerate(linhas):
        if 'lucide-react' in linha:
            # Extrai os ícones que já estão lá dentro
            match = re.search(r'import\s*\{([^}]+)\}\s*from\s*["\']lucide-react["\']', linha)
            if match:
                icones_existentes = [x.strip() for x in match.group(1).split(',')]
                
                # Lista de ícones que precisamos garantir que estejam lá
                icones_necessarios = ["UserCircle", "Info", "Wrench", "Plus", "Trash2", "Pencil", "CheckCircle2", "Clock", "AlertCircle"]
                
                # Junta tudo sem duplicar
                todos_icones = sorted(list(set(icones_existentes + icones_necessarios)))
                
                # Remove strings vazias
                todos_icones = [x for x in todos_icones if x]
                
                # Reconstrói a linha de import
                nova_linha = f'import {{ {", ".join(todos_icones)} }} from "lucide-react";\n'
                linhas[i] = nova_linha
            break

    with open(caminho, 'w', encoding='utf-8') as f:
        f.writelines(linhas)
    print("✅ Imports do Lucide corrigidos (UserCircle e Info garantidos).")

if __name__ == "__main__":
    fix_imports(os.getcwd())