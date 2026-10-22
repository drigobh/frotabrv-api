import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_alinhar_v2_{agora}.zip"
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

def reescrever_abastecimentos(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Localiza o bloco <TableHeader> ... </TableHeader> e substitui
    inicio_header = conteudo.find("<TableHeader>")
    fim_header = conteudo.find("</TableHeader>") + len("</TableHeader>")
    
    if inicio_header != -1 and fim_header != -1:
        novo_header = '''<TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 whitespace-nowrap px-2 text-left">Data</TableHead>
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
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-center px-2">Ações</TableHead>
            </TableRow>
          </TableHeader>'''
        conteudo = conteudo[:inicio_header] + novo_header + conteudo[fim_header:]
        print("⚙️ Cabeçalho da tabela substituído.")

    # Localiza o bloco de células (TableRow) e substitui a linha de dados
    # O bloco começa com <TableRow key={r.id} e termina com </TableRow>
    inicio_tr = conteudo.find("<TableRow key={r.id}")
    fim_tr = conteudo.find("</TableRow>", inicio_tr) + len("</TableRow>")
    
    if inicio_tr != -1 and fim_tr != -1:
        nova_linha = '''<TableRow key={r.id} className="border-slate-800/70" data-testid={`abastecimento-row-${r.id}`}>
                <TableCell className="font-mono text-xs whitespace-nowrap px-2 text-left">{dataBR(r.data)}</TableCell>
                <TableCell className="text-center px-2">
                  {r.origem === "pdf" ? (
                    <span className="inline-flex items-center justify-center rounded bg-red-500/20 px-2 py-0.5 text-xs font-bold text-red-400" title="Importado via PDF">PDF</span>
                  ) : (
                    <span className="inline-flex items-center justify-center rounded bg-slate-500/20 px-2 py-0.5 text-xs font-bold text-slate-400" title="Inserido Manualmente">M</span>
                  )}
                </TableCell>
                <TableCell className="font-mono text-xs whitespace-nowrap px-2 text-left">{r.veiculo_label.split(" · ")[0]}</TableCell>
                <TableCell className="text-slate-300 text-xs whitespace-nowrap px-2 truncate max-w-[150px] text-left">{r.motorista_label ?? "—"}</TableCell>
                <TableCell className="tabular-nums text-xs whitespace-nowrap px-2 text-right">{num(r.litros, 1)}</TableCell>
                <TableCell className="tabular-nums text-xs whitespace-nowrap px-2 text-right">{num(r.preco_litro, 2)}</TableCell>
                <TableCell className="tabular-nums font-medium text-xs whitespace-nowrap px-2 text-right">{brl(r.valor_total)}</TableCell>
                <TableCell className="text-xs whitespace-nowrap px-2 truncate max-w-[100px] text-slate-400 text-left">{r.posto}</TableCell>
                <TableCell className="font-mono tabular-nums text-xs whitespace-nowrap px-2 text-right">{num(r.km)}</TableCell>
                <TableCell className="tabular-nums text-xs whitespace-nowrap px-2 text-right">{r.km_rodados != null ? num(r.km_rodados) : "—"}</TableCell>
                <TableCell className="tabular-nums text-xs whitespace-nowrap px-2 text-right text-sky-300">{r.media_km_l != null ? `${num(r.media_km_l, 2)}` : "—"}</TableCell>
                <TableCell className="text-center px-2">
                  <div className="flex gap-1 justify-center">
                    <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)} aria-label="Editar">
                      <Pencil className="size-4 text-sky-400" />
                    </Button>
                    {me?.perfil === "admin" && (
                      <Button size="icon-sm" variant="ghost" className="text-red-300" onClick={() => setExcluirId(r.id)} aria-label="Excluir" data-testid={`abastecimento-delete-${r.id}`}>
                        <Trash2 className="size-4" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>'''
        conteudo = conteudo[:inicio_tr] + nova_linha + conteudo[fim_tr:]
        print("⚙️ Linha de dados da tabela substituída com alinhamentos corretos.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✅ Abastecimentos.tsx atualizado com sucesso.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Alinhamento da Tabela (v2)...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    reescrever_abastecimentos(raiz)

    print("\n🚀 Automação concluída! Siga os passos:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()