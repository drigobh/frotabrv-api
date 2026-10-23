import os
import shutil
import datetime
import zipfile
import re

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_reparar_motorista_{agora}.zip"
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

def reparar_linha_motorista(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Encontra o bloco onde está o campo do motorista e o substitui inteiro
    # Padrão antigo (mesmo que esteja quebrado)
    padrao = re.compile(r'<FieldSelect\s+value=\{form\.motorista_id\}.*?/>', re.DOTALL)
    
    novo_bloco = '''<FieldSelect
                value={form.motorista_id}
                onChange={set("motorista_id")}
                options={[
                  { value: NENHUM, label: "— Não informado —" },
                  ...(motoristas.data ?? []).filter((m: any) => m.ativo).map((m: any) => ({ value: m.id, label: m.nome }))
                ]}
                testId="abastecimento-form-motorista"
              />'''

    if padrao.search(conteudo):
        conteudo = padrao.sub(novo_bloco, conteudo)
        print("⚙️ Bloco do FieldSelect do motorista corrigido.")
    else:
        print("⚠️ Não foi possível encontrar o bloco original. Tentando corrigir manualmente...")
        # Fallback: remove a linha quebrada e insere o bloco correto
        linhas = conteudo.split('\n')
        for i in range(len(linhas)):
            if "value={form.motorista_id}" in linhas[i]:
                # Remove as 3 próximas linhas para garantir
                del linhas[i:i+5]
                linhas.insert(i, novo_bloco)
                break
        conteudo = '\n'.join(linhas)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✅ Arquivo Abastecimentos.tsx atualizado.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Reparo do FieldSelect (Motorista)...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    reparar_linha_motorista(raiz)

    print("\n🚀 Automação concluída! Reinicie o Vite:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()