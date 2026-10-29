import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ULTIMOS_AJUSTES_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    arquivos = [
        "app/backend/models/fornecedores.py",
        "app/backend/routers/fornecedores.py",
        "frontend/src/pages/Fornecedores.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    # 1. Atualizar Model
    model_path = os.path.join(raiz, "app", "backend", "models", "fornecedores.py")
    if os.path.exists(model_path):
        with open(model_path, 'r', encoding='utf-8') as f:
            c = f.read()
        
        if 'contato:' not in c:
            # Adiciona no FornecedorBase e no FornecedorCreate
            c = c.replace(
                'telefone: str | None = None',
                'telefone: str | None = None\n    contato: str | None = None\n    whatsapp: str | None = None'
            )
            with open(model_path, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Backend Model: campos 'contato' e 'whatsapp' adicionados.")

    # 2. Forçar gravação no Router (Criar/Atualizar)
    router_path = os.path.join(raiz, "app", "backend", "routers", "fornecedores.py")
    if os.path.exists(router_path):
        with open(router_path, 'r', encoding='utf-8') as f:
            c = f.read()
        
        # Substituir a criação para garantir que contato e whatsapp sejam salvos
        novo_criar = '''@router.post("", response_model=Fornecedor, status_code=201)
async def criar(body: FornecedorCreate, request: Request, user: dict = Depends(require("write"))):
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    doc["created_by"] = user["nome"]
    
    # Força a gravação dos campos (mesmo que não estejam no model base)
    if hasattr(body, 'contato'): doc["contato"] = body.contato
    if hasattr(body, 'whatsapp'): doc["whatsapp"] = body.whatsapp
    
    await db.fornecedores.insert_one(dict(doc))
    return Fornecedor(**doc)'''
        
        novo_atualizar = '''@router.put("/{id}", response_model=Fornecedor)
async def atualizar(id: str, body: FornecedorCreate, request: Request, user: dict = Depends(require("write"))):
    doc = body.model_dump()
    doc["updated_at"] = now_iso()
    doc["updated_by"] = user["nome"]
    
    # Força a gravação dos campos
    if hasattr(body, 'contato'): doc["contato"] = body.contato
    if hasattr(body, 'whatsapp'): doc["whatsapp"] = body.whatsapp
    
    await db.fornecedores.update_one({"id": id}, {"$set": doc})
    doc = await db.fornecedores.find_one({"id": id}, {"_id": 0})
    return Fornecedor(**doc)'''
        
        # Se o router antigo tiver uma estrutura diferente, vamos tentar substituir as funções
        # Para segurança, faremos uma substituição via regex de blocos de função
        c = re.sub(r'@router\.post\("", response_model=Fornecedor, status_code=201\)\n[\s\S]*?return Fornecedor\(\*\*doc\)', novo_criar, c)
        c = re.sub(r'@router\.put\("/\{id\}", response_model=Fornecedor\)\n[\s\S]*?return Fornecedor\(\*\*doc\)', novo_atualizar, c)
        
        with open(router_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend Router: gravação de contato e whatsapp forçada.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Renomear o botão para "Mapa dos Fornecedores"
    c = c.replace('<MapPin className="size-4 mr-2" /> Mapa', '<MapPin className="size-4 mr-2" /> Mapa dos Fornecedores')

    # 2. Adicionar opção "Todos" no select de estados
    if 'Todos os Estados' not in c:
        c = c.replace(
            '<option value="">Selecione...</option>',
            '<option value="">Selecione...</option>\n                <option value="TODOS">Todos os Estados</option>'
        )
        
        # Atualizar a função irParaGoogleMaps para aceitar TODOS
        nova_func = '''  const irParaGoogleMaps = () => {
    if (!estadoSelecionado) return toast.error("Selecione um estado.");
    
    if (estadoSelecionado === "TODOS") {
      window.open("https://www.google.com/maps/search/?api=1&query=Fornecedores+Brasil", "_blank");
      setMapaAberto(false);
      return;
    }
    
    const fornecedoresEstado = fornecedores.filter(f => f.estado === estadoSelecionado && f.endereco && f.cidade);
    if (fornecedoresEstado.length === 0) return toast.error("Nenhum fornecedor com endereço completo neste estado.");

    const query = encodeURIComponent(`Fornecedores em ${estadoSelecionado}`);
    window.open(`https://www.google.com/maps/search/?api=1&query=${query}`, "_blank");
    setMapaAberto(false);
  };'''
        c = re.sub(r'const irParaGoogleMaps = \(\) => \{[\s\S]*?\n  \};', nova_func, c, count=1)

    # 3. Renomear a coluna "Distância" para "Rota"
    c = c.replace('>Distância</TableHead>', '>Rota</TableHead>')

    # 4. Remover o "Abrir no Maps" da coluna de Localização
    # A célula de localização tem o botão. Vamos remover o bloco do botão.
    alvo_maps = '''<button onClick={() => window.open(`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${r.endereco || ""}, ${r.cidade}, ${r.estado}`)}`, "_blank")} className="text-sky-400 hover:underline text-[10px] flex items-center gap-1">
                        <MapPin className="size-3" /> Abrir no Maps
                      </button>'''
    c = c.replace(alvo_maps, '')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: botão renomeado, opção 'Todos' adicionada, coluna renomeada e função de mapa removida da localização.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Todos os ajustes aplicados com sucesso! Faça o git push.")