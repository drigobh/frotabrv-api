import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MAPA_GEOCODE_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    arquivos = [
        "app/backend/routers/empresa.py",
        "frontend/src/components/MapaFornecedores.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "empresa.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Adiciona a rota de geocode no router da empresa
    if '/geocode' not in c:
        rota = '''
import httpx

@router.get("/geocode")
async def geocode(endereco: str, _u: dict = Depends(require("read"))):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(
                f"https://nominatim.openstreetmap.org/search?format=json&q={endereco}",
                headers={"User-Agent": "FrotaBrv/1.0 (contato@frotabrv.com)"},
                timeout=10
            )
            res.raise_for_status()
            data = res.json()
            if data and len(data) > 0:
                return {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])}
            return {"error": "Endereço não encontrado"}
        except Exception as e:
            raise HTTPException(500, f"Erro ao geocodificar: {str(e)}")
'''
        c += rota
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota /geocode criada no router /empresa.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "MapaFornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Substitui a chamada direta ao Nominatim pela chamada ao nosso Backend
    c = c.replace(
        'const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(`${f.endereco}, ${f.cidade}, ${f.estado}`)}`);',
        'const res = await fetch(`/api/empresa/geocode?endereco=${encodeURIComponent(`${f.endereco}, ${f.cidade}, ${f.estado}`)}`);'
    )
    
    # Ajusta o parse da resposta (nosso backend retorna {lat, lon} em vez de um array)
    c = c.replace(
        '''const data = await res.json();
        if (data && data.length > 0) {
          return { id: f.id, lat: Number(data[0].lat), lon: Number(data[0].lon) };
        }''',
        '''const data = await res.json();
        if (data && data.lat && data.lon) {
          return { id: f.id, lat: data.lat, lon: data.lon };
        }'''
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Chamada do geocode alterada para o Backend.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado! Faça o git push.")