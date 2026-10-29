import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_CNPJ_PROXY_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    arquivos = [
        "app/backend/routers/empresa.py",
        "frontend/src/pages/Empresa.tsx"
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

    # Adiciona a rota /cnpj/{cnpj} no router da empresa
    if '/cnpj/{cnpj}' not in c:
        rota_cnpj = '''
import httpx

@router.get("/cnpj/{cnpj}")
async def buscar_cnpj(cnpj: str, _u: dict = Depends(require("read"))):
    cnpj_limpo = "".join(filter(str.isdigit, cnpj))
    if len(cnpj_limpo) != 14:
        raise HTTPException(400, "CNPJ inválido")
    
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}", timeout=10)
            if res.status_code == 404:
                raise HTTPException(404, "CNPJ não encontrado na base da Receita.")
            res.raise_for_status()
            return res.json()
        except httpx.HTTPError as e:
            raise HTTPException(500, f"Erro ao consultar CNPJ: {str(e)}")
'''
        # Insere no final do arquivo
        c += rota_cnpj
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota de busca de CNPJ criada no router /empresa.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Empresa.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Substitui a chamada direta pela nossa API
    c = c.replace(
        'const res = await fetch(`https://brasilapi.com.br/api/cnpj/v1/${cnpjLimpo}`);',
        'const res = await fetch(`/api/empresa/cnpj/${cnpjLimpo}`);'
    )
    
    # Verifica se a troca funcionou
    if '/api/empresa/cnpj/' in c:
        print("✅ Frontend: Chamada apontando para o backend (sem CORS).")
    else:
        print("⚠️ Não foi possível ajustar a chamada no Frontend.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

def verificar_server(raiz):
    caminho = os.path.join(raiz, "app", "backend", "server.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if 'empresa' not in c:
        print("⚠️ O router empresa não está registrado no server.py! Adicionando...")
        c = c.replace(
            'from routers import tipos_fornecedores, parametrizacao, auth,',
            'from routers import tipos_fornecedores, parametrizacao, empresa, auth,'
        )
        c = c.replace(
            'api_router.include_router(parametrizacao.router)',
            'api_router.include_router(parametrizacao.router)\napi_router.include_router(empresa.router)'
        )
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ server.py corrigido com o registro do empresa.router.")
    else:
        print("✅ server.py já está correto.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    verificar_server(raiz)
    print("\n✅ Script aplicado! Faça o push para atualizar o Render.")