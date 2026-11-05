import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Veiculos.tsx")

if not os.path.exists(path):
    print("❌ Arquivo Veiculos.tsx não encontrado.")
else:
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # 1. Garantir imports do useNavigate e do ícone Eye
    if "useNavigate" not in c:
        c = c.replace('import { useState', 'import { useNavigate } from "react-router-dom";\nimport { useState', 1)
    
    if "Eye" not in c.split("from \"lucide-react\"")[0]:
        c = re.sub(r'import\s+\{([^}]+)\}\s+from\s+"lucide-react";', r'import {\1, Eye } from "lucide-react";', c, count=1)

    # 2. Adicionar const navigate = useNavigate(); no início do componente
    if "const navigate = useNavigate();" not in c:
        match_comp = re.search(r'(export default function \w+\(\)\s*\{)', c)
        if match_comp:
            c = c.replace(match_comp.group(1), match_comp.group(1) + "\n  const navigate = useNavigate();")

    # 3. Encontrar o bloco de botões da tabela (onde tem a lixeira ou o lápis)
    # Procura uma TableCell que contenha Trash2 ou Pencil
    padrao_celula = re.search(r'(<TableCell[^>]*className="[^"]*text-right[^"]*"[^>]*>)\s*(<div[^>]*>\s*)?(<Button[^>]*>.*?<Pencil|<Button[^>]*>.*?<Trash2)', c, re.DOTALL)
    
    if padrao_celula:
        # Insere o botão do olho logo após a abertura da TableCell (e do div se existir)
        prefixo = padrao_celula.group(1)
        div_abertura = padrao_celula.group(2) or ""
        
        botao_olho = f'''
          <Button size="icon-sm" variant="ghost" onClick={{() => navigate(`/cadastros/veiculos/${{v.id}}`)}} title="Visão 360º">
            <Eye className="size-4 text-emerald-400" />
          </Button>
        '''
        
        # Substitui a abertura da célula pelo botão + abertura original
        c = c.replace(prefixo + div_abertura, prefixo + div_abertura + botao_olho)
        print("✅ Botão 'Visão 360º' injetado com sucesso na tabela!")
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(c)
    else:
        print("⚠️ Ainda não consegui achar o padrão exato da tabela. Vou tentar um fallback por 'Ações'.")
        
        # Fallback: Procura a linha que tem a palavra "Ações" no cabeçalho e adiciona uma coluna
        # Ou tenta achar qualquer <Button> que tenha um ícone Pencil
        padrao_pencil = re.search(r'(<Button[^>]*>.*?<Pencil)', c, re.DOTALL)
        if padrao_pencil:
            # Pega os 100 caracteres antes do Pencil para achar a TableCell
            inicio = max(0, padrao_pencil.start() - 150)
            trecho = c[inicio:padrao_pencil.end()]
            
            # Encontra a última ocorrência de <TableCell antes do Pencil
            if "<TableCell" in trecho:
                # Substitui a primeira aparição do botão lápis por (Olho + Lápis)
                botao_original = padrao_pencil.group(1)
                botao_olho = f'''
                  <Button size="icon-sm" variant="ghost" onClick={{() => navigate(`/cadastros/veiculos/${{v.id}}`)}} title="Visão 360º">
                    <Eye className="size-4 text-emerald-400" />
                  </Button>
                ''' + botao_original
                
                c = c.replace(botao_original, botao_olho)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(c)
                print("✅ Botão 'Visão 360º' injetado (fallback).")
        else:
            print("❌ Não foi possível encontrar o botão de editar. Preciso que me mande o trecho da tabela do Veiculos.tsx.")