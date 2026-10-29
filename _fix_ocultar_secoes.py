import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_OCULTAR_SECOES_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Abastecimentos.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar os estados de controle
    if 'const [showCards, setShowCards] = useState(true);' not in c:
        c = c.replace(
            'const [openExportModal, setOpenExportModal] = useState(false);',
            'const [openExportModal, setOpenExportModal] = useState(false);\n  const [showCards, setShowCards] = useState(true);\n  const [showTermometro, setShowTermometro] = useState(true);\n  const [showGrid, setShowGrid] = useState(true);'
        )
        print("✅ Estados de visibilidade adicionados.")

    # 2. Inserir a barra de controle após o PageHeader
    padrao_header = re.compile(r'(<\/PageHeader>)', re.DOTALL)
    barra_controle = '''</PageHeader>

      <div className="flex justify-end gap-2 mb-3">
        <Button variant="outline" size="sm" onClick={() => setShowCards(!showCards)} className="h-7 px-2 text-[10px] text-slate-400 border-slate-800 hover:bg-slate-800 hover:text-slate-200">
          {showCards ? <EyeOff className="size-3 mr-1" /> : <Eye className="size-3 mr-1" />} Cards
        </Button>
        <Button variant="outline" size="sm" onClick={() => setShowTermometro(!showTermometro)} className="h-7 px-2 text-[10px] text-slate-400 border-slate-800 hover:bg-slate-800 hover:text-slate-200">
          {showTermometro ? <EyeOff className="size-3 mr-1" /> : <Eye className="size-3 mr-1" />} Termômetro
        </Button>
        <Button variant="outline" size="sm" onClick={() => setShowGrid(!showGrid)} className="h-7 px-2 text-[10px] text-slate-400 border-slate-800 hover:bg-slate-800 hover:text-slate-200">
          {showGrid ? <EyeOff className="size-3 mr-1" /> : <Eye className="size-3 mr-1" />} Filtros/Grid
        </Button>
      </div>'''
    
    if 'Filtros/Grid</Button>' not in c:
        c = padrao_header.sub(barra_controle, c, count=1)
        print("✅ Barra de controle adicionada.")

    # 3. Envolver os Cards condicionalmente
    padrao_cards = re.compile(r'(<div className="mb-4 grid gap-2 grid-cols-2[\s\S]*?</div>\s*)(?=<div className="mb-4 glass rounded-xl p-3">)', re.DOTALL)
    if '{showCards && (' not in c:
        def wrap_cards(m):
            return '{showCards && (\n      ' + m.group(1) + '\n      )}\n\n      '
        c = padrao_cards.sub(wrap_cards, c)
        print("✅ Cards envolvidos na condicional.")

    # 4. Envolver o Termômetro condicionalmente
    padrao_term = re.compile(r'(<div className="mb-4 glass rounded-xl p-3">[\s\S]*?</div>\s*)(?=<div className="mb-4 flex flex-wrap gap-2 items-end">)', re.DOTALL)
    if '{showTermometro && (' not in c:
        def wrap_term(m):
            return '{showTermometro && (\n      ' + m.group(1) + '\n      )}\n\n      '
        c = padrao_term.sub(wrap_term, c)
        print("✅ Termômetro envolvido na condicional.")

    # 5. Envolver Filtros + Grid condicionalmente
    padrao_grid = re.compile(r'(<div className="mb-4 flex flex-wrap gap-2 items-end">[\s\S]*?</Table>\s*</div>)', re.DOTALL)
    if '{showGrid && (' not in c:
        def wrap_grid(m):
            return '{showGrid && (\n      <>\n      ' + m.group(1) + '\n      </>\n      )}'
        c = padrao_grid.sub(wrap_grid, c)
        print("✅ Filtros e Grid envolvidos na condicional.")

    # 6. Garantir que o ícone EyeOff está importado
    if 'EyeOff' not in c.split('lucide-react')[0]:
        c = c.replace('import { Fuel, Plus', 'import { Fuel, Plus, EyeOff')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)