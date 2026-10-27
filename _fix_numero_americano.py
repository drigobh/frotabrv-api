import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_NUM_AMERICANO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in ["frontend/src/pages/Abastecimentos.tsx"]:
            caminho_abs = os.path.join(raiz, p)
            if os.path.exists(caminho_abs):
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # O alvo é a função parseNum dentro do handleImportEdenred
    padrao = re.compile(r'const parseNum = \(val: any\) => \{[\s\S]*?return isNaN\(num\) \? 0 : num;\n      \};', re.DOTALL)
    
    nova_funcao = '''const parseNum = (val: any) => {
        if (val === undefined || val === null || val === "") return 0;
        if (typeof val === 'number') return val;
        let str = String(val).replace(/[^0-9.,-]/g, "");
        
        // Verifica se é padrão Americano (1,234.56) ou Brasileiro (1.234,56)
        if (str.includes('.') && str.includes(',')) {
            if (str.lastIndexOf(',') > str.lastIndexOf('.')) {
                // Padrão Brasileiro: 1.234,56
                str = str.replace(/\\./g, '').replace(',', '.');
            } else {
                // Padrão Americano: 1,234.56
                str = str.replace(/,/g, '');
            }
        } else if (str.includes(',')) {
            // Só tem vírgula, então é decimal BR (ex: 7,29)
            str = str.replace(',', '.');
        }
        
        const num = Number(str);
        return isNaN(num) ? 0 : num;
      };'''

    if padrao.search(c):
        c = padrao.sub(lambda m: nova_funcao, c)
        print("✅ Função parseNum atualizada! Agora ela entende os dois formatos de número.")
    else:
        print("⚠️ Não encontrei a função parseNum. Verifique se a função handleImportEdenred está intacta.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)