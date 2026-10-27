import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_BACKEND_EDENRED_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in ["app/backend/routers/abastecimentos.py"]:
            caminho_abs = os.path.join(raiz, p)
            if os.path.exists(caminho_abs):
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Substituir o bloco de cálculo de KM e Valor Total
    padrao = re.compile(r'    km_rodados = body.get\("km_rodados"\)[\s\S]*?valor_total = round\(valor_total, 2\)', re.DOTALL)
    
    novo_bloco = '''    km_rodados = body.get("km_rodados")
    media_km_l = body.get("media_km_l")
    
    # Se for Excel (Edenred), confia nos dados da planilha
    if body.get("origem") == "excel":
        valor_total = round(litros * preco_litro, 2)
        # Se a planilha não mandou km_rodados, calcula
        if km_rodados is None:
            if ultimo and ultimo.get("km") and km_atual > ultimo["km"]:
                km_rodados = km_atual - ultimo["km"]
                if km_rodados > 0 and litros > 0 and "ARLA" not in (produto or "").upper():
                    media_km_l = km_rodados / litros
            elif km_atual > 0 and veiculo.get("hodometro_km") and km_atual > veiculo["hodometro_km"]:
                km_rodados = km_atual - veiculo["hodometro_km"]
                if km_rodados > 0 and litros > 0 and "ARLA" not in (produto or "").upper():
                    media_km_l = km_rodados / litros
    else:
        # Para PDF e Manual, mantém a lógica de cálculo
        valor_total = body.get("valor_total")
        try: valor_total = float(valor_total)
        except: valor_total = 0

        if valor_total == 0:
            valor_total = litros * preco_litro

        if km_rodados is None:
            if ultimo and ultimo.get("km") and km_atual > ultimo["km"]:
                km_rodados = km_atual - ultimo["km"]
                if km_rodados > 0 and litros > 0 and "ARLA" not in (produto or "").upper():
                    media_km_l = km_rodados / litros
            elif km_atual > 0 and veiculo.get("hodometro_km") and km_atual > veiculo["hodometro_km"]:
                km_rodados = km_atual - veiculo["hodometro_km"]
                if km_rodados > 0 and litros > 0 and "ARLA" not in (produto or "").upper():
                    media_km_l = km_rodados / litros

    valor_total = round(valor_total, 2)'''

    if padrao.search(c):
        c = padrao.sub(lambda m: novo_bloco, c)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend atualizado com sucesso! O Edenred agora terá valor total e rodados corretos.")
    else:
        print("⚠️ Não foi possível encontrar o bloco de cálculo no Backend. Verifique o arquivo manualmente.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)