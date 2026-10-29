import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_POPUP_MAPA_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    arquivos = [
        "app/backend/routers/fornecedores.py",
        "frontend/src/components/MapaFornecedores.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "fornecedores.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Adiciona rota para buscar o último abastecimento do fornecedor
    if '/ultimo-abastecimento' not in c:
        rota = '''
@router.get("/{id}/ultimo-abastecimento")
async def ultimo_abastecimento(id: str, _u: dict = Depends(require("read"))):
    # Busca o fornecedor para pegar o nome
    forn = await db.fornecedores.find_one({"id": id}, {"nome": 1})
    if not forn:
        raise HTTPException(404, "Fornecedor não encontrado")
    
    # Busca o último abastecimento com esse fornecedor
    abast = await db.abastecimentos.find_one(
        {"fornecedor": forn["nome"]},
        {"_id": 0},
        sort=[("data", -1)]
    )
    
    if not abast:
        return {"mensagem": "Nenhum abastecimento encontrado"}
    
    return abast
'''
        c += rota
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota /{id}/ultimo-abastecimento criada.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "MapaFornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar estado para guardar o último abastecimento
    if 'ultimoAbastecimento' not in c:
        c = c.replace(
            'const [coordsFocado, setCoordsFocado] = useState<[number, number] | null>(null);',
            'const [coordsFocado, setCoordsFocado] = useState<[number, number] | null>(null);\n  const [ultimoAbastecimento, setUltimoAbastecimento] = useState<any>(null);'
        )
        print("✅ Estado 'ultimoAbastecimento' adicionado.")

    # 2. No focarFornecedor, buscar o abastecimento se for do tipo Combustíveis
    if 'setUltimoAbastecimento(null);' not in c:
        # Adiciona a limpeza no início da função
        c = c.replace(
            'setFornecedorFocado(f);\n    setCoordsFocado(null);',
            'setFornecedorFocado(f);\n    setCoordsFocado(null);\n    setUltimoAbastecimento(null);'
        )
        
        # Adiciona a busca após obter as coordenadas
        c = c.replace(
            'if (f.latitude && f.longitude) {\n      setCoordsFocado([f.latitude, f.longitude]);\n      return;\n    }',
            '''if (f.latitude && f.longitude) {
      setCoordsFocado([f.latitude, f.longitude]);
    }'''
        )
        
        # No final da função, busca o abastecimento se for combustível
        # Precisamos substituir o final da função
        padrao_final = re.compile(r'(const focarFornecedor = async \(f: any\) => \{[\s\S]*?)(};)')
        match = padrao_final.search(c)
        if match:
            # Adiciona a busca antes do fechamento
            nova_funcao = match.group(1) + '''
    // Busca o último abastecimento se for do tipo Combustíveis
    try {
      const tiposRes = await fetch(`/api/tipos-fornecedores`);
      const tipos = await tiposRes.json();
      const tipoCombustivel = tipos.find((t: any) => t.nome.toLowerCase().includes("combustíveis e lubrificantes"));
      
      if (tipoCombustivel && f.tipo_fornecedor_id === tipoCombustivel.id) {
        const abastRes = await fetch(`/api/fornecedores/${f.id}/ultimo-abastecimento`);
        const abastData = await abastRes.json();
        setUltimoAbastecimento(abastData);
      }
    } catch (e) {
      console.error("Erro ao buscar abastecimento:", e);
    }
  };'''
            c = c[:match.start()] + nova_funcao + c[match.end():]
            print("✅ Busca de último abastecimento adicionada.")

    # 3. Atualizar o Popup do marcador para mostrar os detalhes
    padrao_popup = re.compile(r'<Popup>[\s\S]*?</Popup>')
    
    novo_popup = '''<Popup>
                      <div className="text-sm space-y-1 min-w-[250px]">
                        <p className="font-bold text-base border-b pb-1">{f.nome}</p>
                        <p><strong>Endereço:</strong> {f.endereco}</p>
                        <p><strong>Cidade:</strong> {f.cidade} - {f.estado}</p>
                        <p><strong>Contato:</strong> {f.contato || "—"}</p>
                        <p><strong>WhatsApp:</strong> {f.whatsapp || "—"}</p>
                        
                        {/* Se for combustível, mostra o último abastecimento */}
                        {f.id === fornecedorFocado?.id && ultimoAbastecimento && !ultimoAbastecimento.mensagem && (
                          <div className="mt-2 pt-2 border-t border-slate-300">
                            <p className="font-bold text-xs text-sky-600">Último Abastecimento:</p>
                            <p><strong>Data:</strong> {new Date(ultimoAbastecimento.data).toLocaleDateString('pt-BR')}</p>
                            <p><strong>Combustível:</strong> {ultimoAbastecimento.produto}</p>
                            <p><strong>Litros:</strong> {ultimoAbastecimento.litros} L</p>
                            <p><strong>Motorista:</strong> {ultimoAbastecimento.motorista_label || "—"}</p>
                            <p><strong>Cavalo:</strong> {ultimoAbastecimento.veiculo_label || "—"}</p>
                            <p><strong>Carreta:</strong> {ultimoAbastecimento.carreta_label || "—"}</p>
                          </div>
                        )}
                      </div>
                    </Popup>'''
    
    if padrao_popup.search(c):
        c = padrao_popup.sub(lambda m: novo_popup, c, count=1)
        print("✅ Popup atualizado com as informações completas.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ MapaFornecedores.tsx atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso! Faça o git push.")