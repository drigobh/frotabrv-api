import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_SEED_MEDIDAS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "frontend/src/pages/PneuMedidas.tsx",
        "app/backend/routers/pneu_medidas.py"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    # Adicionar rota de seed no Router
    router_path = os.path.join(raiz, "app", "backend", "routers", "pneu_medidas.py")
    with open(router_path, 'r', encoding='utf-8') as f:
        c = f.read()

    if '/seed' not in c:
        rota_seed = '''
@router.post("/seed")
async def seed_medidas(_u: dict = Depends(require("write"))):
    medidas = [
        {"codigo": "295/80 R22.5", "aro": "22.5", "tipo_construcao": "RADIAL", "requer_camara": False},
        {"codigo": "275/80 R22.5", "aro": "22.5", "tipo_construcao": "RADIAL", "requer_camara": False},
        {"codigo": "315/80 R22.5", "aro": "22.5", "tipo_construcao": "RADIAL", "requer_camara": False},
        {"codigo": "385/65 R22.5", "aro": "22.5", "tipo_construcao": "RADIAL", "requer_camara": False},
        {"codigo": "12 R22.5", "aro": "22.5", "tipo_construcao": "RADIAL", "requer_camara": False},
        {"codigo": "11.00 R22", "aro": "22.0", "tipo_construcao": "RADIAL", "requer_camara": True},
        {"codigo": "215/75 R17.5", "aro": "17.5", "tipo_construcao": "RADIAL", "requer_camara": False},
        {"codigo": "235/75 R17.5", "aro": "17.5", "tipo_construcao": "RADIAL", "requer_camara": False},
    ]
    inseridos = 0
    for m in medidas:
        existente = await db.pneu_medidas.find_one({"codigo": m["codigo"]})
        if not existente:
            m["id"] = str(uuid.uuid4())
            m["created_at"] = now_iso()
            await db.pneu_medidas.insert_one(dict(m))
            inseridos += 1
    return {"ok": True, "inseridos": inseridos}
'''
        c += rota_seed
        with open(router_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota /seed criada.")

def fix_frontend(raiz):
    # Adicionar botão "Popular Medidas" na tela
    caminho = os.path.join(raiz, "frontend", "src", "pages", "PneuMedidas.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    if 'Popular Medidas' not in c:
        # Adicionar o botão no PageHeader
        c = c.replace(
            'actions={<Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Nova Medida</Button>}',
            '''actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={popularMedidas} disabled={seed.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10 h-9">
              {seed.isPending ? "Populando..." : "Popular Medidas"}
            </Button>
            <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Nova Medida</Button>
          </div>
        }'''
        )

        # Adicionar a mutation de seed
        c = c.replace(
            'const salvar = useMutation({',
            '''const seed = useMutation({
    mutationFn: () => apiPost("/pneu-medidas/seed", {}),
    onSuccess: () => { toast.success("Medidas populadas!"); qc.invalidateQueries({ queryKey: ["pneu-medidas"] }); },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const popularMedidas = () => {
    if (confirm("Isso vai adicionar as medidas padrão de pneus. Continuar?")) {
      seed.mutate();
    }
  };

  const salvar = useMutation({'''
        )
        print("✅ Frontend: Botão 'Popular Medidas' adicionado.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso!")
    