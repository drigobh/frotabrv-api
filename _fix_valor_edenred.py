import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_VALOR_EDENRED_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
        zipf.write(caminho_abs, "frontend/src/pages/Abastecimentos.tsx")
    print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # O alvo é o parseNum dentro do handleImportEdenred. 
    # Vamos garantir que ele converta "2449,44" para 2449.44.
    alvo_antigo = '''const parseNum = (val: any) => {
        if (!val) return 0;
        let str = String(val).replace(/[^\\d.,-]/g, "");
        if (str.includes('.') && str.includes(',')) str = str.replace(/\\./g, '').replace(',', '.');
        else if (str.includes(',')) str = str.replace(',', '.');
        return Number(str) || 0;
      };'''

    alvo_novo = '''const parseNum = (val: any) => {
        if (!val) return 0;
        let str = String(val).trim();
        // Converte formato brasileiro (1.234,56) para (1234.56)
        if (str.includes('.') && str.includes(',')) {
            str = str.replace(/\\./g, '').replace(',', '.');
        } else if (str.includes(',')) {
            str = str.replace(',', '.');
        }
        const num = Number(str);
        return isNaN(num) ? 0 : num;
      };'''

    if alvo_antigo in c:
        c = c.replace(alvo_antigo, alvo_novo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Correção cirúrgica aplicada: O parseNum do Edenred agora converte valores com vírgula corretamente.")
    else:
        print("⚠️ O bloco parseNum não foi encontrado exatamente como esperado. Nenhuma alteração foi feita.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)