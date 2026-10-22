import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_tabela_sem_scroll_{agora}.zip"
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Criando Backup Full do Sistema...")
    ignorar = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build']
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta_alvo in ['app', 'frontend']:
            caminho_pasta = os.path.join(raiz, pasta_alvo)
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ignorar]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try:
                        zipf.write(caminho_completo, caminho_relativo)
                    except Exception:
                        pass
    print(f"✅ Backup Full salvo em: _automacao/backups/{nome_backup}")

def ajustar_componente_table(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "ui", "table.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Remove o "overflow-x-auto" e o wrapper <div> para a tabela ocupar 100%
    if "overflow-x-auto" in conteudo:
        conteudo = conteudo.replace(
            '<div className="relative w-full overflow-x-auto">',
            '<div className="relative w-full">'
        )
        # Alguns templates usam "overflow-auto"
        conteudo = conteudo.replace(
            '<div className="relative w-full overflow-auto">',
            '<div className="relative w-full">'
        )
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ Componente Table ajustado (rolagem horizontal removida).")
    else:
        print("ℹ️ O componente Table já está sem overflow-x-auto.")

def ajustar_abastecimentos(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Remove os w-[...] fixos e coloca whitespace-nowrap e text-xs
    tabela_antiga = '''              <TableHead className="w-[80px] text-xs uppercase tracking-wider text-slate-500">Data</TableHead>
              <TableHead className="w-[60px] text-xs uppercase tracking-wider text-slate-500 text-center">Origem</TableHead>
              <TableHead className="w-[140px] text-xs uppercase tracking-wider text-slate-500">Veículo</TableHead>
              <TableHead className="w-[180px] text-xs uppercase tracking-wider text-slate-500">Motorista</TableHead>
              <TableHead className="w-[70px] text-xs uppercase tracking-wider text-slate-500 text-right">Litros</TableHead>
              <TableHead className="w-[60px] text-xs uppercase tracking-wider text-slate-500 text-right">R$/L</TableHead>
              <TableHead className="w-[90px] text-xs uppercase tracking-wider text-slate-500 text-right">Total</TableHead>
              <TableHead className="w-[100px] text-xs uppercase tracking-wider text-slate-500">Posto</TableHead>
              <TableHead className="w-[70px] text-xs uppercase tracking-wider text-slate-500 text-right">KM</TableHead>
              <TableHead className="w-[70px] text-xs uppercase tracking-wider text-slate-500 text-right">Rodados</TableHead>
              <TableHead className="w-[60px] text-xs uppercase tracking-wider text-slate-500 text-right">Média</TableHead>
              <TableHead className="w-[80px] text-xs uppercase tracking-wider text-slate-500 text-center">Ações</TableHead>'''

    tabela_nova = '''              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 whitespace-nowrap px-1">Data</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-center px-1">Origem</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 px-1">Veículo</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 px-1">Motorista</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-1">Litros</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-1">R$/L</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-1">Total</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 px-1">Posto</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-1">KM</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-1">Rodados</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-1">Média</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-center px-1">Ações</TableHead>'''
    
    if "w-[80px]" in conteudo:
        conteudo = conteudo.replace(tabela_antiga, tabela_nova)
        print("⚙️ Cabeçalho da tabela ajustado (texto menor e sem larguras fixas).")

    # 2. Ajustar as células do corpo da tabela
    # Substituir classes antigas por versões mais compactas
    conteudo = conteudo.replace('className="font-mono text-sm"', 'className="font-mono text-xs whitespace-nowrap px-1"')
    conteudo = conteudo.replace('className="font-mono"', 'className="font-mono text-xs whitespace-nowrap px-1"')
    conteudo = conteudo.replace('className="text-slate-300"', 'className="text-slate-300 text-xs whitespace-nowrap px-1 truncate max-w-[100px]"')
    conteudo = conteudo.replace('className="tabular-nums"', 'className="tabular-nums text-xs whitespace-nowrap px-1 text-right"')
    conteudo = conteudo.replace('className="tabular-nums font-medium"', 'className="tabular-nums font-medium text-xs whitespace-nowrap px-1 text-right"')
    conteudo = conteudo.replace('className="max-w-[180px] truncate text-slate-400"', 'className="text-xs whitespace-nowrap px-1 truncate max-w-[80px] text-slate-400"')
    conteudo = conteudo.replace('className="text-center"', 'className="text-center text-xs px-1 whitespace-nowrap"')
    
    # Ajustar a célula de Ações
    conteudo = conteudo.replace(
        'className="text-right flex gap-2 justify-end"',
        'className="text-right flex gap-1 justify-end px-1"'
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ Células da tabela ajustadas para serem compactas.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Tabela sem Rolagem...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    ajustar_componente_table(raiz)
    ajustar_abastecimentos(raiz)

    print("\n🚀 Automação concluída! Siga os passos:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()