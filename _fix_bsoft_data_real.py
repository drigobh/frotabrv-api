import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_BSOFT_DATA_REAL_{agora}.zip")
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

    # O alvo é a conversão da data dentro do handleImportXLS
    padrao = re.compile(r'let dataStr = String\(row\[idxData\]\)\.trim\(\)\.split\(" "\)\[0\];', re.DOTALL)
    
    nova_conversao = '''let dataStr = String(row[idxData]).trim().split(" ")[0]; 
        
        // Conversão Inteligente de Data (Americano M/D/YY para YYYY-MM-DD)
        if (dataStr.includes("/")) {
            const parts = dataStr.split("/");
            if (parts.length === 3) {
                let month = parts[0].padStart(2, '0');
                let day = parts[1].padStart(2, '0');
                let year = parts[2];
                if (year.length === 2) year = "20" + year; // Transforma 26 em 2026
                dataStr = `${year}-${month}-${day}`;
            }
        } else if (dataStr.includes("-")) {
            // Já está no formato YYYY-MM-DD
            dataStr = dataStr;
        }'''

    if padrao.search(c):
        c = padrao.sub(nova_conversao, c)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Conversão de data do BSOFT corrigida! Agora ela envia no formato YYYY-MM-DD.")
    else:
        print("⚠️ Não encontrei a linha exata da data no handleImportXLS.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)