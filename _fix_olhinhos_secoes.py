import os
import re
import time
import datetime
import zipfile
import subprocess

RAIZ = os.getcwd()
CAMINHO_TSX = os.path.join(RAIZ, "frontend", "src", "pages", "Abastecimentos.tsx")
CAMINHO_REL = "frontend/src/pages/Abastecimentos.tsx"

def backup():
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = os.path.join(RAIZ, "_automacao", "backups", f"BACKUP_OLHINHOS_{agora}.zip")
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    if os.path.exists(CAMINHO_TSX):
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(CAMINHO_TSX, CAMINHO_REL)
        print(f"✅ Backup: {zip_path}")

def try_git_restore():
    try:
        r = subprocess.run(["git", "status", "--short", "--", CAMINHO_REL],
                           capture_output=True, text=True, timeout=10, cwd=RAIZ)
        status = r.stdout.strip()
        if not status:
            print("ℹ️  Arquivo já está limpo (sem modificações pendentes).")
            return True
        print(f"⚠️  Modificações pendentes:\n  {status}")
        print("   ⚠️  Ctrl+C em 3s para abortar (caso tenha trabalho bom não commitado).")
        time.sleep(3)
        r = subprocess.run(["git", "checkout", "--", CAMINHO_REL],
                           capture_output=True, text=True, timeout=10, cwd=RAIZ)
        if r.returncode == 0:
            print("✅ Arquivo restaurado para o último commit (tentativa anterior descartada).")
            return True
        print(f"⚠️  Git checkout retornou: {r.stderr.strip()}")
        return False
    except Exception as e:
        print(f"⚠️  Git indisponível: {e}")
        return False

def aplicar():
    with open(CAMINHO_TSX, 'r', encoding='utf-8') as f:
        c = f.read()

    # --- 1. Estados ---
    if 'const [showCards' not in c:
        anchor = 'const [openExportModal, setOpenExportModal] = useState(false);'
        if anchor in c:
            c = c.replace(anchor, anchor +
                '\n  const [showCards, setShowCards] = useState(true);'
                '\n  const [showTermometro, setShowTermometro] = useState(true);'
                '\n  const [showGrid, setShowGrid] = useState(true);', 1)
        else:
            idx = c.find('  return (')
            if idx < 0:
                print("❌ Não achei o return do componente.")
                return False
            c = c[:idx] + (
                '  const [showCards, setShowCards] = useState(true);\n'
                '  const [showTermometro, setShowTermometro] = useState(true);\n'
                '  const [showGrid, setShowGrid] = useState(true);\n'
            ) + c[idx:]
        print("✅ Estados adicionados.")

    # --- 2. Import EyeOff ---
    if 'EyeOff' not in c:
        m = re.search(r'import\s*\{([^}]+)\}\s*from\s*["\']lucide-react["\']', c)
        if m:
            imports = m.group(1)
            if 'Eye' in imports:
                # adiciona EyeOff logo após Eye (ou no final)
                if re.search(r'\bEye\b\s*,', imports):
                    new_imports = re.sub(r'\bEye\b\s*,', 'Eye, EyeOff,', imports, count=1)
                else:
                    new_imports = imports.rstrip() + ', EyeOff'
            else:
                new_imports = imports.rstrip() + ', Eye, EyeOff'
            c = c[:m.start(1)] + new_imports + c[m.end(1):]
            print("✅ EyeOff importado.")

    # --- 3. Botão + wrapper para CARDS ---
    padrao_cards = re.compile(
        r'(<div className="mb-4 grid gap-2 grid-cols-2[^"]*">[\s\S]*?)(?=\n\s*<div className="mb-4 glass rounded-xl p-3">)'
    )
    m = padrao_cards.search(c)
    if m:
        bloco = m.group(1).rstrip()
        novo = (
            '<div className="flex items-center gap-2 mb-2">\n'
            '        <Button variant="ghost" size="icon" onClick={() => setShowCards(!showCards)} className="h-6 w-6 text-slate-400 hover:text-white">\n'
            '          {showCards ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}\n'
            '        </Button>\n'
            '        <span className="text-[10px] uppercase font-semibold text-slate-500 tracking-wider">Cards</span>\n'
            '      </div>\n'
            '      {showCards && (\n'
            '      ' + bloco + '\n'
            '      )}'
        )
        c = c[:m.start()] + novo + c[m.end():]
        print("✅ Cards: olhinho + condicional aplicados.")
    else:
        print("⚠️  Cards não encontrado (âncora ausente).")

    # --- 4. Botão + wrapper para TERMÔMETRO ---
    padrao_term = re.compile(
        r'(<div className="mb-4 glass rounded-xl p-3">[\s\S]*?)(?=\n\s*<div className="mb-4 flex flex-wrap gap-2 items-end">)'
    )
    m = padrao_term.search(c)
    if m:
        bloco = m.group(1).rstrip()
        novo = (
            '<div className="flex items-center gap-2 mb-2">\n'
            '        <Button variant="ghost" size="icon" onClick={() => setShowTermometro(!showTermometro)} className="h-6 w-6 text-slate-400 hover:text-white">\n'
            '          {showTermometro ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}\n'
            '        </Button>\n'
            '        <span className="text-[10px] uppercase font-semibold text-slate-500 tracking-wider">Termômetro</span>\n'
            '      </div>\n'
            '      {showTermometro && (\n'
            '      ' + bloco + '\n'
            '      )}'
        )
        c = c[:m.start()] + novo + c[m.end():]
        print("✅ Termômetro: olhinho + condicional aplicados.")
    else:
        print("⚠️  Termômetro não encontrado (âncora ausente).")

    # --- 5. Botão + wrapper para FILTROS/GRID ---
    padrao_grid = re.compile(
        r'(<div className="mb-4 flex flex-wrap gap-2 items-end">[\s\S]*?)(?=\n\s*<Dialog)'
    )
    m = padrao_grid.search(c)
    if m:
        bloco = m.group(1).rstrip()
        novo = (
            '<div className="flex items-center gap-2 mb-2">\n'
            '        <Button variant="ghost" size="icon" onClick={() => setShowGrid(!showGrid)} className="h-6 w-6 text-slate-400 hover:text-white">\n'
            '          {showGrid ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}\n'
            '        </Button>\n'
            '        <span className="text-[10px] uppercase font-semibold text-slate-500 tracking-wider">Filtros / Grid</span>\n'
            '      </div>\n'
            '      {showGrid && (\n'
            '      <>\n'
            '      ' + bloco + '\n'
            '      </>\n'
            '      )}'
        )
        c = c[:m.start()] + novo + c[m.end():]
        print("✅ Filtros/Grid: olhinho + condicional aplicados.")
    else:
        print("⚠️  Filtros/Grid não encontrado (âncora ausente).")

    with open(CAMINHO_TSX, 'w', encoding='utf-8') as f:
        f.write(c)
    return True

if __name__ == "__main__":
    print("🔧 Aplicando olhinhos por seção...\n")
    backup()
    if try_git_restore():
        print("\n→ Aplicando patch no arquivo limpo...\n")
    else:
        print("\n→ Tentando aplicar no arquivo atual (pode haver duplicações)...\n")
    ok = aplicar()
    if ok:
        print("\n✅ Pronto! Reinicie o Vite (Ctrl+C e npm run dev) e recarregue a página.")
    else:
        print("\n❌ Não foi possível aplicar. Me envie o erro exato.")