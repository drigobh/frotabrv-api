import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_CALCULO_ED_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    for p in ["frontend/src/pages/Abastecimentos.tsx", "app/backend/routers/abastecimentos.py"]:
        caminho_abs = os.path.join(raiz, p)
        if os.path.exists(caminho_abs):
            with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Substituir a lógica de cálculo do km_rodados e media_km_l
    antigo = '''    if body.get("origem") == "excel" and body.get("km_rodados") is not None:
        km_rodados = parse_num(body.get("km_rodados"))
        media_km_l = parse_num(body.get("media_km_l"))
    else:
        km_rodados, media_km_l = calcular_km(km_atual, litros, produto, ultimo, veiculo)'''

    novo = '''    provided_km = body.get("km_rodados")
    provided_media = body.get("media_km_l")
    
    # Só usa os valores da planilha se forem válidos (maiores que 0)
    if body.get("origem") == "excel" and provided_km is not None and provided_km > 0 and provided_media is not None and provided_media > 0:
        km_rodados = provided_km
        media_km_l = provided_media
    else:
        # Se a planilha mandou 0 ou nulo, recalcula com base no hodômetro
        km_rodados, media_km_l = calcular_km(km_atual, litros, produto, ultimo, veiculo)'''

    if antigo in c:
        c = c.replace(antigo, novo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Lógica de cálculo ajustada para ignorar zeros da planilha.")
    else:
        print("⚠️ Backend: Trecho exato não encontrado.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Atualizar a função handleImportEdenred para enviar null se o valor for 0 ou negativo
    padrao = re.compile(r'const kmRodadosNum = idxKmRodados !== -1 \? parseNum\(row\[idxKmRodados\]\) : null;\s*const mediaNum = idxMedia !== -1 \? parseNum\(row\[idxMedia\]\) : null;')
    
    novo_trecho = '''const kmRodadosNum = idxKmRodados !== -1 ? parseNum(row[idxKmRodados]) : null;
        const mediaNum = idxMedia !== -1 ? parseNum(row[idxMedia]) : null;
        const finalKmRodados = (kmRodadosNum !== null && kmRodadosNum > 0) ? kmRodadosNum : null;
        const finalMedia = (mediaNum !== null && mediaNum > 0) ? mediaNum : null;'''

    if padrao.search(c):
        c = padrao.sub(novo_trecho, c)
        
        # Atualizar o payload para usar finalKmRodados e finalMedia
        c = c.replace('km_rodados: kmRodadosNum,', 'km_rodados: finalKmRodados,')
        c = c.replace('media_km_l: mediaNum,', 'media_km_l: finalMedia,')
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Frontend: Valores zerados agora são enviados como nulos para o backend calcular.")
    else:
        print("⚠️ Frontend: Trecho exato não encontrado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso!")