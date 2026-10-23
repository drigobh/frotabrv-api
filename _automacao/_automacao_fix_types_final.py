import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_types_final_{agora}.zip"
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

def corrigir_types(raiz):
    # 1. Criar/atualizar o arquivo vite-env.d.ts
    caminho_env = os.path.join(raiz, "frontend", "src", "vite-env.d.ts")
    conteudo_env = '''/// <reference types="vite/client" />

declare module '*?url' {
  const src: string;
  export default src;
}
'''
    with open(caminho_env, 'w', encoding='utf-8') as f:
        f.write(conteudo_env)
    print("⚙️ Arquivo vite-env.d.ts criado/atualizado.")

    # 2. Corrigir o testId do FieldSelect de motorista no Abastecimentos
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Adiciona testId no FieldSelect do motorista (se não existir)
    if 'testId="abastecimento-form-motorista"' not in conteudo:
        conteudo = conteudo.replace(
            '<FieldSelect value={form.motorista_id} onChange={set("motorista_id")} options={[{ value: NENHUM, label: "— Não informado —" }, ...(motoristas.data ?? []).filter(m => m.ativo).map((m) => ({ value: m.id, label: m.nome }))]} />',
            '<FieldSelect value={form.motorista_id} onChange={set("motorista_id")} options={[{ value: NENHUM, label: "— Não informado —" }, ...(motoristas.data ?? []).filter(m => m.ativo).map((m) => ({ value: m.id, label: m.nome }))]} testId="abastecimento-form-motorista" />'
        )
        print("⚙️ testId do FieldSelect de motorista adicionado.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção Final de Types...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_types(raiz)

    print("\n🚀 Automação concluída! Reinicie o Vite:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()