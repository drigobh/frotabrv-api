import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

if not os.path.exists(path):
    print("❌ Sidebar.tsx não encontrado.")
else:
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    if "relatorios-pneus" in c:
        print("ℹ️ O link de Relatórios já existe no menu.")
    else:
        # Procura qualquer trecho do arquivo que contenha '/operacao/pneus'
        # E captura o bloco HTML/JSX ao redor dele
        linhas = c.split("\n")
        novas_linhas = []
        injetado = False

        for i, linha in enumerate(linhas):
            novas_linhas.append(linha)
            
            # Se achar a linha que contém o link de pneus (e não for a importação)
            if "/operacao/pneus" in linha and "import" not in linha and not injetado:
                # Vamos clonar essa linha e adaptar para relatórios
                nova_linha = linha.replace("/operacao/pneus", "/operacao/relatorios-pneus")
                nova_linha = nova_linha.replace("Pneus", "Relatórios Pneus")
                nova_linha = nova_linha.replace("Disc", "BarChart3").replace("disc", "barchart-3")
                
                # Se a linha tiver a palavra 'label', ela é um objeto
                if "to:" in linha:
                    # Adiciona a nova linha formatada
                    novas_linhas.append(nova_linha)
                    injetado = True
                elif "<Link" in linha:
                    # Se for JSX, insere depois do fechamento da tag
                    novas_linhas.append(nova_linha)
                    injetado = True
                elif "<a " in linha or "NavLink" in linha:
                    novas_linhas.append(nova_linha)
                    injetado = True
                else:
                    # Fallback genérico: insere a linha clonada logo abaixo
                    novas_linhas.append(nova_linha)
                    injetado = True

        if injetado:
            c = "\n".join(novas_linhas)
            # Garante que o ícone BarChart3 esteja importado
            if "BarChart3" not in c.split("export")[0]:
                # Tenta achar um import do lucide-react
                c = re.sub(r'(import\s+\{[^}]*)\}', r'\1, BarChart3 }', c, count=1)
            
            with open(path, "w", encoding="utf-8") as f:
                f.write(c)
            print("✅ Link 'Relatórios Pneus' inserido com sucesso no menu lateral!")
        else:
            print("⚠️ Ainda não foi possível achar a âncora do link de Pneus. Me mande o conteúdo do Sidebar.tsx para eu analisar manualmente.")