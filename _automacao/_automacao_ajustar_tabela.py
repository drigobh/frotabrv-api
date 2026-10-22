import os
import shutil
import datetime
import zipfile
import re

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_tabela_width_{agora}.zip"
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

def ajustar_tabela(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Ajustar a definição das colunas (TableHead)
    # Vamos substituir os cabeçalhos para incluir larguras específicas
    tabela_antiga = '''              {["Data", "Origem", "Veículo", "Motorista", "Litros", "R$/L", "Total", "Posto", "KM", "Rodados", "Média", "Ações"].map((h) => (
                <TableHead key={h} className="text-xs uppercase tracking-wider text-slate-500">{h}</TableHead>
              ))}'''
    
    tabela_nova = '''              <TableHead className="w-[80px] text-xs uppercase tracking-wider text-slate-500">Data</TableHead>
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
    
    if "w-[80px]" not in conteudo:
        conteudo = conteudo.replace(tabela_antiga, tabela_nova)
        print("⚙️ Cabeçalho da tabela ajustado com larguras fixas.")

    # 2. Ajustar o padding das células (TableCell)
    # Substitui as classes "px-3" ou "p-3" por "px-2" para ganhar espaço
    if "px-2" not in conteudo:
        conteudo = conteudo.replace('className="font-mono text-sm"', 'className="font-mono text-sm px-2"')
        conteudo = conteudo.replace('className="font-mono"', 'className="font-mono px-2"')
        conteudo = conteudo.replace('className="text-slate-300"', 'className="text-slate-300 px-2 truncate max-w-[180px]"')
        conteudo = conteudo.replace('className="tabular-nums"', 'className="tabular-nums px-2 text-right"')
        conteudo = conteudo.replace('className="tabular-nums font-medium"', 'className="tabular-nums font-medium px-2 text-right"')
        conteudo = conteudo.replace('className="max-w-[180px] truncate text-slate-400"', 'className="max-w-[100px] truncate text-slate-400 px-2"')
        conteudo = conteudo.replace('className="text-center"', 'className="text-center px-2"')
        print("⚙️ Padding das células reduzido.")

    # 3. Envolver o conteudo da tabela em um container com "text-sm" para diminuir a fonte geral
    # Mas vamos apenas garantir que a tabela use text-xs
    if "text-xs" not in conteudo:
        conteudo = conteudo.replace('<Table data-testid="abastecimento-table">', '<Table className="text-xs" data-testid="abastecimento-table">')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ Abastecimentos.tsx atualizado para evitar rolagem horizontal.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Ajuste de Tabela...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    ajustar_tabela(raiz)

    print("\n🚀 Automação concluída! Siga os passos:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()