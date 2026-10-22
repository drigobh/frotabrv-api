import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_fix_botao_pdf_{agora}.zip"
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

def corrigir_botoes(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Encontra o bloco de botões que está quebrado e substitui por uma estrutura correta
    bloco_antigo = '''        actions={
          <input type="file" accept=".pdf" ref={fileInputRef} onChange={handleImportPDF} className="hidden" />
          <Button variant="outline" onClick={() => fileInputRef.current?.click()} data-testid="abastecimento-import-pdf">
            <FileText className="size-4 mr-2" /> Importar NF
          </Button>
          <Button onClick={abrirNovo} data-testid="abastecimento-new-button">
            <Plus className="size-4" /> Novo abastecimento
          </Button>
        }'''

    bloco_novo = '''        actions={
          <div className="flex gap-2">
            <input type="file" accept=".pdf" ref={fileInputRef} onChange={handleImportPDF} className="hidden" />
            <Button variant="outline" onClick={() => fileInputRef.current?.click()} data-testid="abastecimento-import-pdf">
              <FileText className="size-4 mr-2" /> Importar NF
            </Button>
            <Button onClick={abrirNovo} data-testid="abastecimento-new-button">
              <Plus className="size-4" /> Novo abastecimento
            </Button>
          </div>
        }'''

    if bloco_antigo in conteudo:
        conteudo = conteudo.replace(bloco_antigo, bloco_novo)
        print("⚙️ Estrutura dos botões corrigida (envolvidos em uma div flex).")
    else:
        print("⚠️ O bloco exato não foi encontrado. Tentando uma abordagem alternativa...")
        # Tenta encontrar apenas a injeção do botão e consertar
        if '<div className="flex gap-2">' not in conteudo and 'Importar NF' in conteudo:
            # Remove o botão solto e recria a estrutura
            import re
            # Encontra a tag <Button ... Novo abastecimento> e tudo em volta
            padrao = re.compile(r'<input type="file".*?</Button>\s*<Button.*?</Button>', re.DOTALL)
            if padrao.search(conteudo):
                conteudo = padrao.sub(bloco_novo.replace('        actions={\n', '').replace('\n        }', ''), conteudo)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ Arquivo Abastecimentos.tsx atualizado.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção do Botão PDF...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_botoes(raiz)

    print("\n🚀 Automação concluída! Siga os passos:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()