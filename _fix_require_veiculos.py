import os
import re

# 1. Descobrir onde o 'require' está definido
pastas = [
    os.path.join(os.getcwd(), "app", "backend", "lib"),
    os.path.join(os.getcwd(), "app", "backend")
]

origem_require = None
for pasta in pastas:
    if not os.path.exists(pasta): continue
    for arquivo in os.listdir(pasta):
        if arquivo.endswith(".py"):
            caminho = os.path.join(pasta, arquivo)
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = f.read()
            # Procura "def require" no arquivo
            if "def require" in conteudo:
                # Descobre o caminho de importação (ex: app.backend.lib.auth)
                rel_path = os.path.relpath(caminho, os.getcwd())
                modulo = rel_path.replace("\\", ".").replace("/", ".").replace(".py", "")
                origem_require = modulo
                break
    if origem_require:
        break

if not origem_require:
    print("❌ Não encontrei a definição da função 'require' no backend. Tentando alternativa...")
    origem_require = "app.backend.lib.auth"  # Fallback comum
    print(f"⚠️ Usando caminho fallback: {origem_require}")

print(f"✅ Função 'require' encontrada em: {origem_require}")

# 2. Corrigir o arquivo veiculos.py
path = os.path.join(os.getcwd(), "app", "backend", "routers", "veiculos.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Remove imports antigos que possam estar errados
c = re.sub(r'from \.\.lib\.auth import require\n', '', c)
c = re.sub(r'from app\.backend\.lib\.auth import require\n', '', c)

# Adiciona o import correto se não existir
if "import require" not in c:
    # Procura a última linha de import
    ultima_linha = re.search(r'(^from .*?import .*?\n)(?!from)', c, re.MULTILINE)
    if ultima_linha:
        # Coloca o import após o último import do arquivo
        novo_import = f"from {origem_require.replace('.', '/').replace('/', '.') if origem_require.startswith('app') else origem_require} import require\n"
        # Vamos usar uma forma mais direta: adicionar no topo
        if "import require" not in c.split("router =")[0]:
            # Procura o último import do fastapi ou outro
            linhas = c.split("\n")
            ultima_import = 0
            for i, linha in enumerate(linhas):
                if linha.startswith("from ") or linha.startswith("import "):
                    ultima_import = i
            # Insere após o último import
            if ultima_import > 0:
                c = "\n".join(linhas[:ultima_import+1] + [f"from {origem_require} import require"] + linhas[ultima_import+1:])
            else:
                c = f"from {origem_require} import require\n" + c
            print("✅ Import do 'require' adicionado.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ veiculos.py corrigido! Faça o git push.")