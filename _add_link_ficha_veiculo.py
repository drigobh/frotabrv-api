import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Veiculos.tsx")

if not os.path.exists(path):
    print("❌ Arquivo Veiculos.tsx não encontrado. O nome da tela de veículos pode ser outro.")
else:
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # 1. Garantir que o ícone Eye (olho) e o useNavigate estão importados
    if "useNavigate" not in c:
        c = c.replace('import { useState', 'import { useNavigate } from "react-router-dom";\nimport { useState', 1)
    
    if "Eye" not in c.split("from \"lucide-react\"")[0]:
        c = re.sub(r'import\s+\{([^}]+)\}\s+from\s+"lucide-react";', r'import {\1, Eye } from "lucide-react";', c, count=1)

    # 2. Adicionar a lógica do useNavigate dentro do componente
    if "const navigate = useNavigate();" not in c:
        # Procura o início do componente funcional
        match_comp = re.search(r'export default function \w+\(\)\s*\{', c)
        if match_comp:
            c = c.replace(match_comp.group(0), match_comp.group(0) + "\n  const navigate = useNavigate();")

    # 3. Injetar o botão na tabela (procurando o padrão de botões de ação)
    # Geralmente tem um botão de Editar e Excluir. Vamos colocar antes do Editar.
    padrao_editar = re.search(r'(<Button[^>]*onClick=\{[^}]*setEditing[^}]*\}[^>]*>.*?<Pencil.*?</Button>)', c, re.DOTALL)
    
    if padrao_editar:
        botao_original = padrao_editar.group(1)
        novo_botao = f'''
        <Button size="icon-sm" variant="ghost" onClick={{() => navigate(`/cadastros/veiculos/${{v.id}}`)}} title="Visão 360º">
          <Eye className="size-4 text-emerald-400" />
        </Button>
        ''' + botao_original
        
        c = c.replace(botao_original, novo_botao)
        print("✅ Botão 'Visão 360º' injetado na tabela de Veículos.")
    else:
        # Fallback: Se não achar o botão de editar com setEditing, tenta achar apenas o Pencil
        padrao_pencil = re.search(r'(<Button[^>]*>.*?<Pencil.*?</Button>)', c, re.DOTALL)
        if padrao_pencil:
            botao_original = padrao_pencil.group(1)
            novo_botao = f'''
            <Button size="icon-sm" variant="ghost" onClick={{() => navigate(`/cadastros/veiculos/${{v.id}}`)}} title="Visão 360º">
              <Eye className="size-4 text-emerald-400" />
            </Button>
            ''' + botao_original
            c = c.replace(botao_original, novo_botao)
            print("✅ Botão 'Visão 360º' injetado via fallback.")
        else:
            print("⚠️ Não encontrei a área de botões na tabela. Me mande o arquivo Veiculos.tsx para eu inserir manualmente.")

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)