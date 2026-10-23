import os
import shutil
import datetime
import zipfile
import re

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_fix_botao_{agora}.zip"
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

def corrigir_botao_upload(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    if not os.path.exists(caminho):
        print("❌ Arquivo Abastecimentos.tsx não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Encontra o bloco <div className="flex gap-2"> que contém os botões de importação
    # e substitui por uma versão com <label> envolvendo os inputs
    padrao_botoes = re.compile(
        r'<div className="flex gap-2">[\s\S]*?<Button onClick=\{abrirNovo\}>[\s\S]*?</Button>\s*</div>',
        re.DOTALL
    )

    novo_bloco_botoes = '''<div className="flex gap-2">
            <label className="inline-flex">
              <input type="file" accept=".xls,.xlsx" onChange={handleImportXLS} className="hidden" />
              <Button variant="outline" asChild>
                <span><Upload className="size-4 mr-2" /> Importar XLS</span>
              </Button>
            </label>
            <label className="inline-flex">
              <input type="file" accept=".pdf" onChange={handleImportPDF} className="hidden" />
              <Button variant="outline" asChild>
                <span><FileText className="size-4 mr-2" /> Importar NF</span>
              </Button>
            </label>
            <Button onClick={abrirNovo}>
              <Plus className="size-4" /> Novo abastecimento
            </Button>
          </div>'''

    if padrao_botoes.search(conteudo):
        conteudo = padrao_botoes.sub(novo_bloco_botoes, conteudo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Bloco de botões de importação substituído com <label>.")
    else:
        print("⚠️ Bloco de botões não encontrado. Tentando substituição alternativa...")
        
        # Fallback: substituir apenas os inputs e botões específicos
        conteudo = conteudo.replace(
            '<input type="file" accept=".xls,.xlsx" ref={xlsInputRef} onChange={handleImportXLS} className="hidden" />\n            <Button variant="outline" onClick={() => xlsInputRef.current?.click()}>\n              <Upload className="size-4 mr-2" /> Importar XLS\n            </Button>',
            '''<label className="inline-flex">
              <input type="file" accept=".xls,.xlsx" onChange={handleImportXLS} className="hidden" />
              <Button variant="outline" asChild>
                <span><Upload className="size-4 mr-2" /> Importar XLS</span>
              </Button>
            </label>'''
        )
        conteudo = conteudo.replace(
            '<input type="file" accept=".pdf" ref={fileInputRef} onChange={handleImportPDF} className="hidden" />\n            <Button variant="outline" onClick={() => fileInputRef.current?.click()}>\n              <FileText className="size-4 mr-2" /> Importar NF\n            </Button>',
            '''<label className="inline-flex">
              <input type="file" accept=".pdf" onChange={handleImportPDF} className="hidden" />
              <Button variant="outline" asChild>
                <span><FileText className="size-4 mr-2" /> Importar NF</span>
              </Button>
            </label>'''
        )
        
        # Remove as referências aos refs que não são mais necessárias
        conteudo = conteudo.replace('  const fileInputRef = useRef<HTMLInputElement>(null);\n', '')
        conteudo = conteudo.replace('  const xlsInputRef = useRef<HTMLInputElement>(null);\n', '')
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Botões corrigidos via substituição alternativa.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção dos Botões de Upload...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_botao_upload(raiz)

    print("\n🚀 Automação concluída! Reinicie o Vite:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo e teste a importação.")

if __name__ == "__main__":
    executar()