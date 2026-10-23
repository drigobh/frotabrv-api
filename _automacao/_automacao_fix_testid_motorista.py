import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_testid_{agora}.zip"
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

def corrigir_testid(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    # Procura a linha do FieldSelect de motorista e adiciona o testId
    nova_linha = None
    for i, linha in enumerate(linhas):
        if "value={form.motorista_id}" in linha and "testId" not in linha:
            # Adiciona o testId antes do fechamento />
            linhas[i] = linha.replace("/>", ' testId="abastecimento-form-motorista" />')
            nova_linha = i
            break

    if nova_linha is not None:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.writelines(linhas)
        print(f"⚙️ testId adicionado na linha {nova_linha + 1}.")
    else:
        print("⚠️ A linha do FieldSelect de motorista não foi encontrada. Talvez já esteja corrigida.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção do testId (Motorista)...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_testid(raiz)

    print("\n🚀 Automação concluída! Reinicie o Vite:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()