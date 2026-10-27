import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_CARDS_DEF_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in ["frontend/src/pages/Abastecimentos.tsx", "app/backend/routers/abastecimentos.py"]:
            caminho_abs = os.path.join(raiz, p)
            if os.path.exists(caminho_abs):
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Substitui o bloco de cálculo do valor_total para ser à prova de falhas
    padrao = re.compile(r'    valor_total = body.get\("valor_total"\)\n    if not valor_total:\n        valor_total = litros \* preco_litro\n    valor_total = round\(valor_total, 2\)', re.DOTALL)
    
    novo_bloco = '''    litros = body.get("litros") or 0
    preco_litro = body.get("preco_litro") or 0
    
    try: litros = float(litros)
    except: litros = 0
    
    try: preco_litro = float(preco_litro)
    except: preco_litro = 0

    valor_total = body.get("valor_total")
    try: valor_total = float(valor_total)
    except: valor_total = 0
    
    if valor_total == 0:
        valor_total = litros * preco_litro
        
    valor_total = round(valor_total, 2)'''

    if padrao.search(c):
        c = padrao.sub(lambda m: novo_bloco, c)
        print("✅ Backend: Lógica de cálculo do Valor Total blindada.")
    else:
        print("⚠️ Backend: Padrão não encontrado, mas o código atual pode já estar correto.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Atualizar a função parseNum dentro do handleImportEdenred para ser infalível
    padrao_parse = re.compile(r'const parseNum = \(val: any\) => \{[\s\S]*?return isNaN\(num\) \? 0 : num;\n      \};', re.DOTALL)
    
    novo_parse = '''const parseNum = (val: any) => {
        if (val === undefined || val === null || val === "") return 0;
        if (typeof val === 'number') return val;
        let str = String(val).replace(/[^0-9.,-]/g, "");
        if (str.includes('.') && str.includes(',')) str = str.replace(/\\./g, '').replace(',', '.');
        else if (str.includes(',')) str = str.replace(',', '.');
        const num = Number(str);
        return isNaN(num) ? 0 : num;
      };'''

    if padrao_parse.search(c):
        c = padrao_parse.sub(lambda m: novo_parse, c)
        print("✅ Frontend: Função parseNum robusta aplicada na importação do Edenred.")
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)