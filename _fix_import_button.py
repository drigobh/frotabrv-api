import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_IMPORT_BUTTON_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "RelatorioManutencao.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/RelatorioManutencao.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "RelatorioManutencao.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Verificar se o Button já está importado
    if 'from "@/components/ui/button"' not in c:
        # Adicionar o import logo após os imports do Lucide
        c = c.replace(
            'import { apiGet } from "@/lib/api";',
            'import { Button } from "@/components/ui/button";\nimport { apiGet } from "@/lib/api";'
        )
        print("✅ Import do Button adicionado.")
    else:
        print("ℹ️ Button já estava importado.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")