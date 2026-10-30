import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PARAM_REAL_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "frontend/src/pages/Parametrizacao.tsx",
        "frontend/src/pages/TiposFornecedores.tsx",
        "app/backend/routers/parametrizacao.py"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_parametrizacao(raiz):
    # 1. Remover o botão "Forçar Flags de Seed"
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Parametrizacao.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Remove o botão "Forçar Flags"
    c = re.sub(r'<div className="flex gap-2">\s*<Button\s*variant="outline"\s*onClick=\{async \(\) => \{[\s\S]*?Forçar Flags de Seed\s*</Button>', '<div className="flex justify-end mt-6">', c)
    
    # Remove qualquer resquício do botão
    if 'Forçar Flags de Seed' in c:
        c = c.replace('Forçar Flags de Seed', '')

    # 2. Garantir que a mutation de salvar envia TODAS as flags
    if 'mostrar_seed_fornecedores: mostrarSeedFornecedores,' not in c:
        # Adicionar as flags no payload
        c = c.replace(
            'meta_abastecimento_ativo: ativo,',
            'meta_abastecimento_ativo: ativo,\n      mostrar_seed_fornecedores: mostrarSeedFornecedores,\n      mostrar_seed_medidas: mostrarSeedMedidas,\n      mostrar_seed_marcas: mostrarSeedMarcas,'
        )
        print("✅ Flags garantidas no payload de salvamento.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Parametrizacao.tsx corrigida.")

def fix_backend(raiz):
    # 1. Remover a rota "forcar-seed" (não deve existir)
    caminho = os.path.join(raiz, "app", "backend", "routers", "parametrizacao.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Remove a rota de forçar
    c = re.sub(r'@router\.post\("/forcar-seed"\)[\s\S]*?return \{"ok": True[^}]*\}', '', c)
    print("✅ Rota '/forcar-seed' removida do Backend.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

def fix_tipos_fornecedores(raiz):
    # Garantir que a tela de Tipos de Fornecedores busque a parametrização corretamente
    caminho = os.path.join(raiz, "frontend", "src", "pages", "TiposFornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Verificar se a query está correta
    if 'queryKey: ["parametrizacao-meta"]' not in c:
        c = c.replace(
            'const { data: tipos = [] } = useQuery({ queryKey: ["tipos-fornecedores"], queryFn: () => apiGet<any[]>("/tipos-fornecedores") });',
            'const { data: tipos = [] } = useQuery({ queryKey: ["tipos-fornecedores"], queryFn: () => apiGet<any[]>("/tipos-fornecedores") });\n  const { data: config } = useQuery({ queryKey: ["parametrizacao-meta"], queryFn: () => apiGet<any>("/parametrizacao/meta") });'
        )
        print("✅ Query de parametrização garantida na tela de Tipos de Fornecedores.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_parametrizacao(raiz)
    fix_backend(raiz)
    fix_tipos_fornecedores(raiz)
    print("\n✅ Script aplicado com sucesso!")