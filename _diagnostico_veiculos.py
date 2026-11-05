import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Veiculos.tsx")

if not os.path.exists(path):
    print("❌ Arquivo Veiculos.tsx não encontrado. O nome da tela de veículos pode ser diferente.")
else:
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    print("🔍 Procurando por botões de ação (Pencil, Trash2, Edit)...\n")
    
    # Procura por qualquer menção a Pencil ou Trash2
    matches = re.finditer(r'.*(Pencil|Trash2|Edit|Delete).*', c)
    encontrou = False
    for m in matches:
        print(f"Linha: {m.group(0).strip()}")
        encontrou = True
    
    if not encontrou:
        print("❌ Nenhum botão de ação encontrado no arquivo.")
        
    print("\n" + "="*50)
    print("🔍 Procurando por tag <TableBody> ou <TableCell>...\n")
    
    # Procura a definição da tabela
    match_table = re.search(r'<TableBody>[\s\S]{0, 1500}', c)
    if match_table:
        print(match_table.group(0)[:1500])
    else:
        print("❌ Não encontrei a tag <TableBody> no arquivo.")