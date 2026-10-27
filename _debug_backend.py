import re

caminho = 'app/backend/routers/abastecimentos.py'
with open(caminho, 'r', encoding='utf-8') as f:
    c = f.read()

# Extrai a função importar_pdf completa
m = re.search(r'@router\.post\("/importar"[\s\S]*?(?=@router\.|$)', c)

with open('debug_backend.txt', 'w', encoding='utf-8') as f:
    f.write("--- FUNCAO IMPORTAR_PDF ---\n")
    f.write(m.group(0) if m else "NAO ENCONTRADA")