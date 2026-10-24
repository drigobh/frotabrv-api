import os
import re

def fix_imports(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    novas_linhas = []
    for linha in linhas:
        # Se a linha importar o Info mas NÃO for do lucide-react, removemos o Info
        if linha.startswith('import { Info, ') and 'lucide-react' not in linha:
            linha = linha.replace('import { Info, ', 'import { ')
        
        # Se for a linha do lucide-react, garantimos que o Info esteja lá
        if 'lucide-react' in linha:
            if 'Info' not in linha:
                linha = linha.replace('import { ', 'import { Info, ')
            
        novas_linhas.append(linha)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.writelines(novas_linhas)
    print("✅ Imports corrigidos! O ícone Info agora está apenas no lugar certo.")

if __name__ == "__main__":
    fix_imports(os.getcwd())