import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ADMIN_FORN_V2_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos_para_backup = [
        "frontend/src/pages/Fornecedores.tsx",
        "frontend/src/pages/Admin.tsx",
        "frontend/src/pages/Configuracoes.tsx",
        "app/backend/routers/admin.py",
        "app/backend/routers/base.py",
        "app/backend/routers/configuracoes.py"
    ]
    # CORREÇÃO: Abrindo o arquivo zip para escrita
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in arquivos_para_backup:
            caminho_abs = os.path.join(raiz, p)
            if os.path.exists(caminho_abs):
                zipf.write(caminho_abs, p)
                print(f"Backup de {p} adicionado.")
    print(f"✅ Backup salvo: {caminho_zip}")

def find_and_patch_backend(raiz):
    pastas = ["app/backend/routers", "app/backend"]
    for pasta in pastas:
        caminho_pasta = os.path.join(raiz, pasta)
        if not os.path.exists(caminho_pasta): continue
        for file in os.listdir(caminho_pasta):
            if file.endswith(".py"):
                caminho = os.path.join(caminho_pasta, file)
                with open(caminho, 'r', encoding='utf-8') as f:
                    c = f.read()
                
                if 'limpar_abastecimentos' in c or 'limpar-base' in c or 'limpar' in c:
                    if 'limpar_fornecedores' not in c:
                        padrao_limpar = re.compile(r'(@router\.(?:post|delete)\([^)]*limpar[^)]*\)[\s\S]*?async def limpar_abastecimentos[\s\S]*?return [^\n]+)', re.DOTALL)
                        match = padrao_limpar.search(c)
                        if match:
                            bloco_antigo = match.group(1)
                            bloco_novo = bloco_antigo.replace('limpar_abastecimentos', 'limpar_fornecedores').replace('abastecimentos', 'fornecedores')
                            c = c.replace(bloco_antigo, bloco_antigo + "\n\n" + bloco_novo)
                            with open(caminho, 'w', encoding='utf-8') as f:
                                f.write(c)
                            print(f"✅ Backend: Rota de limpar fornecedores adicionada em {caminho}.")
                            return

def find_and_patch_frontend_admin(raiz):
    pastas = ["frontend/src/pages"]
    for file in os.listdir(os.path.join(raiz, pastas[0])):
        if file.endswith(".tsx"):
            caminho = os.path.join(raiz, pastas[0], file)
            with open(caminho, 'r', encoding='utf-8') as f:
                c = f.read()
            
            if 'Limpar Abastecimentos' in c or 'limpar-abastecimentos' in c or 'Limpar Base' in c:
                if 'Limpar Fornecedores' not in c:
                    # Tenta achar o botão de limpar abastecimentos
                    padrao_botao = re.compile(r'(<(?:Button|button)[^>]*>[\s\S]*?Limpar[^<]*Abastecimentos[\s\S]*?</(?:Button|button)>)', re.DOTALL)
                    match = padrao_botao.search(c)
                    if match:
                        botao_antigo = match.group(1)
                        # Copia o botão, muda o texto e a rota de API se houver
                        botao_novo = botao_antigo.replace('Limpar Abastecimentos', 'Limpar Fornecedores').replace('abastecimentos', 'fornecedores').replace('Limpar', 'Limpar')
                        c = c.replace(botao_antigo, botao_antigo + "\n" + botao_novo)
                        with open(caminho, 'w', encoding='utf-8') as f:
                            f.write(c)
                        print(f"✅ Frontend: Botão de limpar fornecedores adicionado em {caminho}.")
                        return

def patch_fornecedores_grid(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Adicionar o ícone AlertTriangle no import
    if 'AlertTriangle' not in c.split('lucide-react')[0]:
        c = c.replace('from "lucide-react"', ', AlertTriangle } from "lucide-react"')
        # Fallback
        if 'AlertTriangle' not in c:
            c = c.replace('import { ', 'import { AlertTriangle, ')

    # Encontrar a célula do CNPJ e adicionar o alerta
    padrao_cnpj_cell = re.compile(r'<TableCell[^>]*>\{r\.documento[^}]*\}</TableCell>', re.DOTALL)
    
    if padrao_cnpj_cell.search(c):
        def replace_cell(match):
            return f'''<TableCell className="text-xs text-slate-300 text-center font-mono">
              <div className="flex flex-col items-center justify-center">
                <span>{{r.documento || "—"}}</span>
                {{(!r.documento || r.documento.trim() === "") && (
                  <span className="text-red-500 animate-pulse font-bold text-[9px] flex items-center justify-center gap-1 mt-1">
                    <AlertTriangle className="size-3" /> CNPJ Pendente
                  </span>
                )}}
              </div>
            </TableCell>'''
        c = padrao_cnpj_cell.sub(replace_cell, c)
        print("✅ Frontend: Alerta de CNPJ Pendente adicionado no grid de Fornecedores.")
    else:
        if '<TableCell className="font-mono text-xs">{r.documento}</TableCell>' in c:
            c = c.replace(
                '<TableCell className="font-mono text-xs">{r.documento}</TableCell>',
                '''<TableCell className="text-xs text-slate-300 text-center font-mono">
              <div className="flex flex-col items-center justify-center">
                <span>{r.documento || "—"}</span>
                {(!r.documento || r.documento.trim() === "") && (
                  <span className="text-red-500 animate-pulse font-bold text-[9px] flex items-center justify-center gap-1 mt-1">
                    <AlertTriangle className="size-3" /> CNPJ Pendente
                  </span>
                )}
              </div>
            </TableCell>'''
            )
            print("✅ Frontend: Alerta de CNPJ Pendente adicionado (fallback).")
        else:
            print("⚠️ Não foi possível encontrar a célula do CNPJ no grid de Fornecedores.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    find_and_patch_backend(raiz)
    find_and_patch_frontend_admin(raiz)
    patch_fornecedores_grid(raiz)