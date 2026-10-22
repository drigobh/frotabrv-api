import os
import subprocess

def executar_limpeza():
    raiz = os.getcwd()
    print("🧹 Iniciando limpeza do Git para o envio...")

    # 1. Remove os arquivos pesados do controle do Git
    arquivos_para_remover = [
        "frontend.zip",
        "_automacao/backups/backup_FULL_sistema_20261022_120505.zip",
        "_automacao/backups/backup_backend_20261022_115447.zip",
        "_automacao/backups/backup_frontend_20261022_114707.zip",
        "frontend/.env"
    ]

    for arquivo in arquivos_para_remover:
        if os.path.exists(os.path.join(raiz, arquivo)):
            subprocess.run(["git", "rm", "--cached", arquivo], check=False)
            print(f"✅ Removido do Git: {arquivo}")

    # 2. Adiciona regras ao .gitignore para não subir mais
    gitignore_path = os.path.join(raiz, ".gitignore")
    regras = [
        "*.zip",
        "_automacao/backups/",
        "frontend/.env",
        "frontend/node_modules/"
    ]
    
    with open(gitignore_path, "a", encoding="utf-8") as f:
        f.write("\n# Regras adicionadas para evitar arquivos pesados/sensiveis\n")
        for regra in regras:
            f.write(f"{regra}\n")
    print("✅ .gitignore atualizado com as regras de proteção.")

    # 3. Faz o commit e envia novamente
    subprocess.run(["git", "add", ".gitignore"], check=True)
    subprocess.run(["git", "commit", "-m", "chore: limpando arquivos pesados e sensiveis do git"], check=True)
    
    print("🚀 Enviando para o GitHub...")
    subprocess.run(["git", "push", "origin", "main"], check=True)
    
    print("🎉 Push concluído com sucesso! O Render já vai começar a atualizar.")

if __name__ == "__main__":
    executar_limpeza()