import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "types", "cadastros.ts")

if not os.path.exists(path):
    print("❌ Arquivo types/cadastros.ts não encontrado.")
else:
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # Procura a interface Veiculo e adiciona template_chassi_id
    if "interface Veiculo" in c or "type Veiculo" in c:
        if "template_chassi_id" not in c:
            # Encontra a declaração do Veiculo
            match = re.search(r'(export\s+(?:interface|type)\s+Veiculo\s*(?:=|{))', c)
            if match:
                # Se for interface com chaves
                if "{" in match.group(0):
                    c = c.replace(match.group(0), match.group(0) + "\n  template_chassi_id?: string;")
                # Se for type = { ... }
                elif "=" in match.group(0) and "{" in c[match.start():match.start()+200]:
                     c = c.replace(match.group(0), match.group(0) + "\n  template_chassi_id?: string;")
                print("✅ Campo 'template_chassi_id' adicionado à interface Veiculo.")
            else:
                print("⚠️ Não foi possível encontrar a definição do tipo Veiculo.")
        else:
            print("ℹ️ O campo 'template_chassi_id' já existia.")

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)

print("✅ Correção aplicada! Verifique no VS Code se o erro sumiu.")