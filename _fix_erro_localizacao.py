import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ERRO_LOC_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Fornecedores.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Substituir a célula de Localização (que ficou quebrada)
    padrao_loc = re.compile(
        r'<TableCell className="text-slate-400 text-xs">[\s\S]*?\{r\.cidade \? `\$\{r\.cidade\}/\$\{r\.estado\}` : "—"\}[\s\S]*?</TableCell>',
        re.DOTALL
    )
    
    nova_loc = '''<TableCell className="text-slate-400 text-xs">
                  <span className="flex items-center gap-1">
                    <MapPin className="size-3" /> {r.cidade ? `${r.cidade}/${r.estado}` : "—"}
                  </span>
                </TableCell>'''

    if padrao_loc.search(c):
        c = padrao_loc.sub(nova_loc, c, count=1)
        print("✅ Célula de Localização corrigida (removido o bloco quebrado).")
    else:
        # Fallback: remove a condicional vazia {r.cidade && ( ... )}
        padrao_vazio = re.compile(r'\{r\.cidade && \(\s*\)\}', re.DOTALL)
        if padrao_vazio.search(c):
            c = padrao_vazio.sub('', c)
            print("✅ Condicional vazia removida.")

    # 2. Garantir que o cabeçalho da coluna é "Rota"
    c = c.replace('>Distância</TableHead>', '>Rota</TableHead>')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)