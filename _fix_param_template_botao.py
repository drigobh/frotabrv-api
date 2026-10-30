import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PARAM_TEMPLATE_BOTAO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/models/parametrizacao.py",
        "app/backend/routers/parametrizacao.py",
        "frontend/src/pages/Parametrizacao.tsx",
        "frontend/src/pages/ChassiTemplates.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    # 1. Adicionar flag mostrar_seed_templates no Model
    model_path = os.path.join(raiz, "app", "backend", "models", "parametrizacao.py")
    with open(model_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'mostrar_seed_templates' not in c:
        c = c.replace(
            'mostrar_seed_marcas: bool = False',
            'mostrar_seed_marcas: bool = False\n    mostrar_seed_templates: bool = False'
        )
        with open(model_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Model: flag mostrar_seed_templates adicionada.")

    # 2. Atualizar Router
    router_path = os.path.join(raiz, "app", "backend", "routers", "parametrizacao.py")
    with open(router_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'mostrar_seed_templates' not in c:
        c = c.replace(
            'mostrar_seed_marcas=config.get("mostrar_seed_marcas", False)',
            'mostrar_seed_marcas=config.get("mostrar_seed_marcas", False),\n        mostrar_seed_templates=config.get("mostrar_seed_templates", False)'
        )
        c = c.replace(
            '"mostrar_seed_marcas": body.mostrar_seed_marcas,',
            '"mostrar_seed_marcas": body.mostrar_seed_marcas,\n            "mostrar_seed_templates": body.mostrar_seed_templates,'
        )
        with open(router_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Router: flag mostrar_seed_templates adicionada.")

def fix_parametrizacao_front(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Parametrizacao.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar estado
    if 'mostrarSeedTemplates' not in c:
        c = c.replace(
            'const [mostrarSeedMarcas, setMostrarSeedMarcas] = useState(false);',
            'const [mostrarSeedMarcas, setMostrarSeedMarcas] = useState(false);\n  const [mostrarSeedTemplates, setMostrarSeedTemplates] = useState(false);'
        )
        # 2. Adicionar no useEffect
        c = c.replace(
            'setMostrarSeedMarcas(config.mostrar_seed_marcas || false);',
            'setMostrarSeedMarcas(config.mostrar_seed_marcas || false);\n      setMostrarSeedTemplates(config.mostrar_seed_templates || false);'
        )
        # 3. Adicionar no payload
        c = c.replace(
            'mostrar_seed_marcas: mostrarSeedMarcas,',
            'mostrar_seed_marcas: mostrarSeedMarcas,\n      mostrar_seed_templates: mostrarSeedTemplates,'
        )
        print("✅ Estados e payload da Parametrização atualizados.")

    # 4. Adicionar a linha na tabela (após a linha de Marcas)
    if 'Popular Templates' not in c:
        alvo = '''<TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">
                Exibir botão "Popular Marcas" na tela de Marcas de Pneus
              </TableCell>
              <TableCell>
                <button
                  type="button"
                  onClick={() => setMostrarSeedMarcas(!mostrarSeedMarcas)}
                  className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                    mostrarSeedMarcas
                      ? "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"
                      : "bg-red-500/20 text-red-400 hover:bg-red-500/30"
                  }`}
                >
                  {mostrarSeedMarcas ? <CheckCircle2 className="size-3" /> : <XCircle className="size-3" />}
                  {mostrarSeedMarcas ? "Visível" : "Oculto"}
                </button>
              </TableCell>
              <TableCell colSpan={2} className="text-xs text-slate-500 italic">Útil apenas para setup inicial do sistema.</TableCell>
            </TableRow>'''
        
        novo = alvo + '''
            <TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">
                Exibir botão "Popular Templates" na tela de Templates de Chassi
              </TableCell>
              <TableCell>
                <button
                  type="button"
                  onClick={() => setMostrarSeedTemplates(!mostrarSeedTemplates)}
                  className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                    mostrarSeedTemplates
                      ? "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"
                      : "bg-red-500/20 text-red-400 hover:bg-red-500/30"
                  }`}
                >
                  {mostrarSeedTemplates ? <CheckCircle2 className="size-3" /> : <XCircle className="size-3" />}
                  {mostrarSeedTemplates ? "Visível" : "Oculto"}
                </button>
              </TableCell>
              <TableCell colSpan={2} className="text-xs text-slate-500 italic">Útil apenas para setup inicial do sistema.</TableCell>
            </TableRow>'''
        
        if alvo in c:
            c = c.replace(alvo, novo)
            print("✅ Linha de 'Popular Templates' adicionada à Parametrização.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

def fix_templates_front(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "ChassiTemplates.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Trocar o botão fixo pela versão condicional
    # Remove o botão fixo se existir
    c = re.sub(r'<Button variant="outline" onClick=\{\(\) => \{ if\(confirm\("Adicionar templates padrão de fábrica\?"\)\) seed\.mutate\(\); \}\} disabled=\{seed\.isPending\} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10 h-9">\s*<Database className="size-4 mr-2" /> \{seed\.isPending \? "Populando\.\.\." : "Popular Templates"\}\s*</Button>', '', c)
    
    # Adiciona a versão condicional
    alvo = '<Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Novo Template</Button>'
    novo = '''{config?.mostrar_seed_templates && (
            <Button variant="outline" onClick={() => { if(confirm("Adicionar templates padrão de fábrica?")) seed.mutate(); }} disabled={seed.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10 h-9">
              <Database className="size-4 mr-2" /> {seed.isPending ? "Populando..." : "Popular Templates"}
            </Button>
          )}
          ''' + alvo
        
    if alvo in c:
        c = c.replace(alvo, novo)
        print("✅ Botão 'Popular Templates' agora respeita a flag 'mostrar_seed_templates'.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_parametrizacao_front(raiz)
    fix_templates_front(raiz)
    print("\n✅ Script aplicado com sucesso!")