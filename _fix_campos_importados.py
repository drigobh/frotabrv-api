import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_FIX_CAMPOS_IMPORT_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/routers/pneus.py",
        "frontend/src/pages/Pneus.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend_import(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "pneus.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Atualiza a rota /importar para normalizar o tipo e cadastrar os valores das listas
    if 'normalizar_tipo' not in c:
        c = c.replace(
            '@router.post("/importar")',
            '''def normalizar_tipo(tipo_raw: str) -> str:
    t = str(tipo_raw or "").strip().upper()
    if t in ("LISO", "BORRACHUDO", "MISTO", "MISTA"):
        return "Misto"
    if t in ("DIRECIONAL",):
        return "Direcional"
    if t in ("TRACAO", "TRAÇÃO"):
        return "Tração"
    if t in ("BANDA",):
        return "Banda"
    return "Misto"

@router.post("/importar")'''
        )

        # Dentro da função importar_pneus, antes de inserir o doc, garante que marca, modelo e medida existam nas coleções
        c = c.replace(
            'doc = {',
            '''# Garante que marca, modelo e medida existam nas tabelas de apoio
            marca_nome = item.get("marca", "").strip()
            modelo_nome = item.get("modelo", "").strip()
            medida_nome = item.get("medida", "").strip()
            
            if marca_nome and not await db.marcas_pneus.find_one({"nome": marca_nome}):
                await db.marcas_pneus.insert_one({"id": str(uuid.uuid4()), "nome": marca_nome})
            if modelo_nome and not await db.modelos_pneus.find_one({"nome": modelo_nome}):
                await db.modelos_pneus.insert_one({"id": str(uuid.uuid4()), "nome": modelo_nome})
            if medida_nome and not await db.medidas_pneus.find_one({"medida": medida_nome}):
                await db.medidas_pneus.insert_one({"id": str(uuid.uuid4()), "medida": medida_nome})
                
            doc = {'''
        )

        # Normaliza o tipo antes de salvar
        c = c.replace(
            '"tipo": item.get("tipo", "Tração"),',
            '"tipo": normalizar_tipo(item.get("tipo", "Misto")),'
        )

        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota /importar atualizada (normaliza tipo + cadastra valores).")

def fix_frontend_form(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Ajusta a lista TIPOS_PNEU para incluir os valores da Bsoft
    if 'TIPOS_PNEU = ["Direcional", "Tração", "Misto", "Banda"]' in c:
        c = c.replace(
            'const TIPOS_PNEU = ["Direcional", "Tração", "Misto", "Banda"];',
            'const TIPOS_PNEU = ["Direcional", "Tração", "Misto", "Banda", "Liso", "Borrachudo"];'
        )

    # No abrirEdicao, garante que os valores fora da lista sejam adicionados ao select
    if 'const safeMarca' not in c:
        c = c.replace(
            'const abrirEdicao = (r: any) => {',
            '''const abrirEdicao = (r: any) => {
    // Se o pneu tiver um valor que não está na lista, injeta dinamicamente para o select não ficar vazio
    if (r.marca && !marcasDb.find((m: any) => m.nome === r.marca)) marcasDb.push({ id: 'temp', nome: r.marca });
    if (r.modelo && !modelosDb.find((m: any) => m.nome === r.modelo)) modelosDb.push({ id: 'temp', nome: r.modelo });
    if (r.medida && !medidasDb.find((m: any) => m.medida === r.medida)) medidasDb.push({ id: 'temp', medida: r.medida });
    '''
        )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Modal de edição atualizado (mostra valores fora da lista).")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend_import(raiz)
    fix_frontend_form(raiz)
    print("\n✅ Script aplicado com sucesso! Faça o push para o Render.")