import os
import subprocess

def executar_limpeza_profunda():
    print("🧹 Iniciando limpeza profunda do histórico do Git...")

    # 1. Remove o arquivo gigante do commit anterior (reescreve o histórico)
    subprocess.run(["git", "filter-branch", "--force", "--index-filter", 
                    "git rm --cached --ignore-unmatch frontend.zip _automacao/backups/*.zip frontend/.env", 
                    "--prune-empty", "--tag-name-filter", "cat", "--", "--all"], check=False)

    # 2. Limpa a lixeira do Git (garbage collector)
    subprocess.run(["git", "for-each-ref", "--format=%(refname)", "refs/original/", "|", "xargs", "-n", "1", "git", "update-ref", "-d"], shell=True)
    subprocess.run(["git", "reflog", "expire", "--expire=now", "--all"], check=False)
    subprocess.run(["git", "gc", "--prune=now", "--aggressive"], check=False)

    # 3. Tenta enviar novamente
    print("🚀 Tentando enviar novamente para o GitHub...")
    subprocess.run(["git", "push", "origin", "main", "--force"], check=True)

    print("🎉 Push concluído! O Render vai atualizar automaticamente.")

if __name__ == "__main__":
    executar_limpeza_profunda()
    