import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_alinhar_tabela_{agora}.zip"
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

def alinhar_tabela(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Cabeçalhos (Alinhamento)
    # Texto = text-left, Números = text-right, Ações = text-center
    cabecalhos = '''              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 whitespace-nowrap px-2 text-left">Data</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-center px-2">Origem</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 px-2 text-left">Veículo</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 px-2 text-left">Motorista</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-2">Litros</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-2">R$/L</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-2">Total</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 px-2 text-left">Posto</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-2">KM</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-2">Rodados</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-2">Média</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-center px-2">Ações</TableHead>'''

    # Procura o bloco de cabeçalho atual e substitui
    import re
    padrao_cabecalho = re.compile(r'<TableHead className="text-\[10px\].*?</TableHead>', re.DOTALL)
    # Como são várias TableHead, vamos substituir o bloco inteiro do map
    padrao_bloco = re.compile(r'\{["Data",.*?\]\.map\(\(h\) => \(.*?\)\)\}', re.DOTALL)
    
    if padrao_bloco.search(conteudo):
        # Se o código ainda estiver com o map antigo
        conteudo = padrao_bloco.sub(cabecalhos, conteudo)
    else:
        # Se já estiver com os TableHead individuais, substitui o bloco todo
        # Encontra do primeiro TableHead até o último antes do </TableRow>
        inicio = conteudo.find('<TableHead className="text-[10px]')
        if inicio != -1:
            fim = conteudo.find('</TableRow>', inicio)
            conteudo = conteudo[:inicio] + cabecalhos + "\n            " + conteudo[fim:]

    # 2. Células do Corpo
    # Data -> esquerda
    conteudo = conteudo.replace(
        '<TableCell className="font-mono text-xs whitespace-nowrap px-1">{dataBR(r.data)}</TableCell>',
        '<TableCell className="font-mono text-xs whitespace-nowrap px-2 text-left">{dataBR(r.data)}</TableCell>'
    )
    
    # Origem -> centro
    conteudo = conteudo.replace(
        '<TableCell className="text-center">',
        '<TableCell className="text-center px-2">'
    )

    # Veículo -> esquerda
    conteudo = conteudo.replace(
        '<TableCell className="font-mono text-xs whitespace-nowrap px-1">{r.veiculo_label.split(" · ")[0]}</TableCell>',
        '<TableCell className="font-mono text-xs whitespace-nowrap px-2 text-left">{r.veiculo_label.split(" · ")[0]}</TableCell>'
    )

    # Motorista -> esquerda
    conteudo = conteudo.replace(
        '<TableCell className="text-slate-300 text-xs whitespace-nowrap px-1 truncate max-w-[100px]">{r.motorista_label ?? "—"}</TableCell>',
        '<TableCell className="text-slate-300 text-xs whitespace-nowrap px-2 truncate max-w-[150px] text-left">{r.motorista_label ?? "—"}</TableCell>'
    )

    # Litros, R$/L, Total, KM, Rodados, Média -> direita
    # Substituindo as classes genéricas "tabular-nums" que estavam sem alinhamento
    conteudo = conteudo.replace(
        '<TableCell className="tabular-nums text-xs whitespace-nowrap px-1 text-right">{num(r.litros, 1)}</TableCell>',
        '<TableCell className="tabular-nums text-xs whitespace-nowrap px-2 text-right">{num(r.litros, 1)}</TableCell>'
    )
    conteudo = conteudo.replace(
        '<TableCell className="tabular-nums text-xs whitespace-nowrap px-1 text-right">{num(r.preco_litro, 2)}</TableCell>',
        '<TableCell className="tabular-nums text-xs whitespace-nowrap px-2 text-right">{num(r.preco_litro, 2)}</TableCell>'
    )
    conteudo = conteudo.replace(
        '<TableCell className="tabular-nums font-medium text-xs whitespace-nowrap px-1 text-right">{brl(r.valor_total)}</TableCell>',
        '<TableCell className="tabular-nums font-medium text-xs whitespace-nowrap px-2 text-right">{brl(r.valor_total)}</TableCell>'
    )
    
    # Posto -> esquerda
    conteudo = conteudo.replace(
        '<TableCell className="text-xs whitespace-nowrap px-1 truncate max-w-[80px] text-slate-400">{r.posto}</TableCell>',
        '<TableCell className="text-xs whitespace-nowrap px-2 truncate max-w-[100px] text-slate-400 text-left">{r.posto}</TableCell>'
    )

    # KM
    conteudo = conteudo.replace(
        '<TableCell className="font-mono tabular-nums text-xs whitespace-nowrap px-1 text-right">{num(r.km)}</TableCell>',
        '<TableCell className="font-mono tabular-nums text-xs whitespace-nowrap px-2 text-right">{num(r.km)}</TableCell>'
    )
    
    # Rodados
    conteudo = conteudo.replace(
        '<TableCell className="tabular-nums text-xs whitespace-nowrap px-1 text-right">{r.km_rodados != null ? num(r.km_rodados) : "—"}</TableCell>',
        '<TableCell className="tabular-nums text-xs whitespace-nowrap px-2 text-right">{r.km_rodados != null ? num(r.km_rodados) : "—"}</TableCell>'
    )
    
    # Média
    conteudo = conteudo.replace(
        '<TableCell className="tabular-nums text-xs whitespace-nowrap px-1 text-right text-sky-300">{r.media_km_l != null ? `${num(r.media_km_l, 2)}` : "—"}</TableCell>',
        '<TableCell className="tabular-nums text-xs whitespace-nowrap px-2 text-right text-sky-300">{r.media_km_l != null ? `${num(r.media_km_l, 2)}` : "—"}</TableCell>'
    )

    # Ações
    conteudo = conteudo.replace(
        '<TableCell className="text-right flex gap-1 justify-end px-1">',
        '<TableCell className="text-center px-2">'
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ Alinhamento da tabela ajustado.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Alinhamento da Tabela...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    alinhar_tabela(raiz)

    print("\n🚀 Automação concluída! Siga os passos:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()