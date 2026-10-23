import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_fix_testid_linha_{agora}.zip"
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

def corrigir_testid_linha(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    # Procura por qualquer linha que tenha FieldSelect e motorista_id, sem testId
    alterou = False
    for i, linha in enumerate(linhas):
        if "value={form.motorista_id}" in linha and "testId" not in linha:
            # Adiciona o testId antes do fechamento
            linhas[i] = linha.replace("/>", ' testId="abastecimento-form-motorista" />')
            # Se a linha não tiver "/>", pode estar aberta com ">"
            if "/>" not in linha:
                linhas[i] = linha.replace(">", ' testId="abastecimento-form-motorista">', 1)
            alterou = True
            print(f"⚙️ Linha {i + 1} corrigida.")
            break

    if alterou:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.writelines(linhas)
    else:
        print("⚠️ A linha do FieldSelect de motorista não foi encontrada ou já tem testId.")

    # Verifica se o arquivo original ainda tem algum FieldSelect sem testId (para o caso de ter mais de um)
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Faz uma varredura final para garantir que não há mais nenhum FieldSelect sem testId
    import re
    # Encontra todos os FieldSelect
    matches = re.findall(r'<FieldSelect[^>]+>', conteudo)
    for m in matches:
        if 'testId=' not in m:
            print(f"⚠️ Ainda existe FieldSelect sem testId: {m[:50]}...")
            # Tenta adicionar
            novo = m.replace('>', ' testId="abastecimento-form-veiculo" >')
            conteudo = conteudo.replace(m, novo)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção do testId (Linha Específica)...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_testid_linha(raiz)

    print("\n🚀 Automação concluída! Reinicie o Vite:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()