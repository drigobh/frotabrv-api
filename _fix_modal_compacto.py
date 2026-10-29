import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MODAL_COMPACTO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Empresa.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Empresa.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Empresa.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Diminuir a largura do modal de 5xl para 3xl (aprox 30% menor)
    c = c.replace('max-w-5xl', 'max-w-3xl')

    # 2. Diminuir o padding geral (de p-6 para p-5)
    c = c.replace('p-6', 'p-5')

    # 3. Diminuir o gap entre as colunas (de gap-8 para gap-6)
    c = c.replace('lg:flex-row gap-8', 'lg:flex-row gap-6')

    # 4. Diminuir a largura da coluna da logo (de w-[220px] para w-[180px])
    c = c.replace('w-full lg:w-[220px]', 'w-full lg:w-[180px]')

    # 5. Diminuir a altura da logo (de w-40 h-40 para w-32 h-32)
    c = c.replace('w-40 h-40', 'w-32 h-32')

    # 6. Diminuir a altura dos inputs (de h-11 para h-9)
    c = c.replace('h-11', 'h-9')
    
    # 7. Ajustar o botão de busca do CNPJ
    c = c.replace('h-9 w-14 bg-sky-600', 'h-9 w-12 bg-sky-600')
    
    # 8. Ajustar o gap interno das linhas do formulário (de gap-5 para gap-4)
    c = c.replace('gap-5', 'gap-4')
    
    # 9. Diminuir o botão do rodapé
    c = c.replace('h-11 bg-sky-600', 'h-9 bg-sky-600')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Modal compactado com sucesso (redução de ~30%).")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)