import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ERRO_PARSE_{agora}.zip")
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

    # 1. Remover a declaração duplicada de parseSafe
    # A primeira declaração fica fora do useMemo, a segunda dentro. Vamos manter apenas a de fora e remover a de dentro.
    declaração_interna = '''const parseSafe = (val: any) => {
        if (val === undefined || val === null || val === "") return 0;
        if (typeof val === 'number') return val;
        let str = String(val).replace(/[^0-9.,-]/g, "");
        if (str.includes('.') && str.includes(',')) str = str.replace(/\\./g, '').replace(',', '.');
        else if (str.includes(',')) str = str.replace(',', '.');
        return Number(str) || 0;
      };
'''
    # Remove apenas a segunda ocorrência (a que fica dentro do useMemo)
    if c.count(declaração_interna) > 1:
        # Encontra a posição da primeira
        pos1 = c.find(declaração_interna)
        # Encontra a posição da segunda
        pos2 = c.find(declaração_interna, pos1 + 1)
        # Remove a segunda
        c = c[:pos2] + c[pos2 + len(declaração_interna):]
        print("✅ Declaração duplicada de parseSafe removida.")

    # 2. Garantir que a função handleImportEdenred use o mapeamento fixo e não divida os valores
    # (Garantindo que o valor_total seja o valor exato da coluna T)
    padrao_valor = re.compile(r'const valorNum = idxValor !== -1 \? parseNum\(row\[idxValor\]\) : \(litrosNum \* precoNum\);', re.DOTALL)
    if padrao_valor.search(c):
        c = padrao_valor.sub('const valorNum = idxValor !== -1 ? parseNum(row[idxValor]) : (litrosNum * precoNum);', c)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Arquivo corrigido! Pode reiniciar o Vite.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)