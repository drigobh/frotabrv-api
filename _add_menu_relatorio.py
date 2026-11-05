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
        # Procura a linha do link de Pneus
        # Geralmente é algo como: { to: "/operacao/pneus", label: "Pneus", icon: Disc }
        match = re.search(r'\{[^{}]*to:\s*["\']\/operacao\/pneus["\'][^{}]*\}', c)
        
        if match:
            link_pneus = match.group(0)
            # Cria a cópia do link trocando os valores para Relatórios
            link_relatorio = link_pneus.replace("/operacao/pneus", "/operacao/relatorios-pneus")
            link_relatorio = link_relatorio.replace("Pneus", "Relatórios Pneus")
            
            # Tenta trocar o ícone para BarChart3 se o lucide estiver sendo usado
            if "icon: Disc" in link_relatorio:
                link_relatorio = link_relatorio.replace("icon: Disc", "icon: BarChart3")
            
            # Insere o novo link logo após o link de pneus
            c = c.replace(link_pneus, link_pneus + ",\n      " + link_relatorio)
            
            # Garante que o BarChart3 está importado
            if "BarChart3" not in c.split("export")[0]:
                c = c.replace("import {", "import { BarChart3,", 1)
                
            with open(path, "w", encoding="utf-8") as f:
                f.write(c)
            print("✅ Link 'Relatórios Pneus' adicionado ao menu lateral com sucesso!")
        else:
            # Fallback: Se não achar o objeto, tenta achar a tag <Link>
            match_link = re.search(r'<Link[^>]*to=["\']\/operacao\/pneus["\'][^>]*>([\s\S]*?)<\/Link>', c)
            if match_link:
                bloco_pneus = match_link.group(0)
                bloco_relatorio = bloco_pneus.replace("/operacao/pneus", "/operacao/relatorios-pneus")
                bloco_relatorio = bloco_relatorio.replace("Pneus", "Relatórios")
                # Troca o ícone de disco pelo de gráfico
                bloco_relatorio = bloco_relatorio.replace("<Disc", "<BarChart3").replace("</Disc>", "</BarChart3>")
                
                c = c.replace(bloco_pneus, bloco_pneus + "\n      " + bloco_relatorio)
                
                if "BarChart3" not in c.split("export")[0]:
                    c = c.replace("import {", "import { BarChart3,", 1)

                with open(path, "w", encoding="utf-8") as f:
                    f.write(c)
                print("✅ Link 'Relatórios Pneus' adicionado (via tag <Link>)!")
            else:
                print("⚠️ Não foi possível identificar o padrão do link de Pneus no Sidebar.tsx. Me envie o arquivo para eu analisar.")