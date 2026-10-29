import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_FORN_V4_{agora}.zip")
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
    # 1. Garantir o Model
    model_path = os.path.join(raiz, "app", "backend", "models", "fornecedores.py")
    with open(model_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'contato:' not in c:
        c = c.replace('telefone: str | None = None', 'telefone: str | None = None\n    contato: str | None = None\n    whatsapp: str | None = None')
        with open(model_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Model atualizado com contato e whatsapp.")

    # 2. Garantir a gravação no Router
    router_path = os.path.join(raiz, "app", "backend", "routers", "fornecedores.py")
    with open(router_path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # Força a inclusão no POST
    c = re.sub(r'(await db\.fornecedores\.insert_one\(dict\(doc\)\))', r'\1', c)
    if 'doc["contato"] = body.contato' not in c:
        c = c.replace('doc["id"] = str(uuid.uuid4())', 'doc["id"] = str(uuid.uuid4())\n    doc["contato"] = getattr(body, "contato", None)\n    doc["whatsapp"] = getattr(body, "whatsapp", None)')
    
    # Força a inclusão no PUT
    if 'doc["contato"] = body.contato' not in c:
        c = c.replace('await db.fornecedores.update_one({"id": id}, {"$set": doc})', 'doc["contato"] = getattr(body, "contato", None)\n    doc["whatsapp"] = getattr(body, "whatsapp", None)\n    await db.fornecedores.update_one({"id": id}, {"$set": doc})')

    with open(router_path, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Router ajustado para gravar contato e whatsapp.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. RECONSTRUIR A CÉLULA DE CONTATO (Garantir que aparece se tiver no banco)
    # A célula anterior foi removida no lugar errado, vamos colocar de volta no lugar certo
    if '{r.contato' not in c:
        # Remove a célula de Localização antiga
        c = re.sub(r'<TableCell className="text-slate-400 text-xs">\s*<span className="flex items-center gap-1">\s*<MapPin className="size-3" />\s*\{r\.cidade \? `\$\{r\.cidade\}/\$\{r\.estado\}` : "—"\}\s*</span>\s*</TableCell>', 
                   '''<TableCell className="text-slate-400 text-xs">
                  <span className="flex items-center gap-1"><MapPin className="size-3" /> {r.cidade ? `${r.cidade}/${r.estado}` : "—"}</span>
                </TableCell>
                <TableCell className="text-xs text-slate-400 text-center">
                  <div className="flex flex-col items-center justify-center">
                    <span className="font-medium text-slate-300">{r.contato || "—"}</span>
                    {r.whatsapp && (
                      <a href={`https://wa.me/55${r.whatsapp.replace(/\\D/g, '')}`} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-emerald-400 hover:text-emerald-300 mt-1">
                        <MessageCircle className="size-4 animate-pulse" />
                        <span className="text-[10px]">{r.whatsapp}</span>
                      </a>
                    )}
                  </div>
                </TableCell>''', c, count=1)
        print("✅ Célula de Contato reinserida no grid.")

    # 2. RECONSTRUIR A LÓGICA DO MAPA (Modal de Estados + Lista de Fornecedores + OpenStreetMap)
    if 'const abrirMapaCompleto' in c:
        # Remove a função antiga e o modal antigo
        c = re.sub(r'const abrirMapaCompleto = \(\) => \{[\s\S]*?\n  \};', '', c, count=1)
        c = re.sub(r'\{mapaAberto && \([\s\S]*?\)\}', '', c, count=1) # Remove o modal antigo

        nova_logica = '''
  const [mapaAberto, setMapaAberto] = useState(false);
  const [estadoSelecionado, setEstadoSelecionado] = useState("");
  const [fornecedoresMapa, setFornecedoresMapa] = useState<any[]>([]);
  const [selecionadosMapa, setSelecionadosMapa] = useState<string[]>([]);

  const abrirMapaCompleto = () => {
    setMapaAberto(true);
    setEstadoSelecionado("");
    setFornecedoresMapa([]);
    setSelecionadosMapa([]);
  };

  const carregarFornecedoresEstado = (uf: string) => {
    setEstadoSelecionado(uf);
    if (uf === "TODOS") {
      setFornecedoresMapa(fornecedores.filter(f => f.endereco && f.cidade));
    } else {
      setFornecedoresMapa(fornecedores.filter(f => f.estado === uf && f.endereco && f.cidade));
    }
    setSelecionadosMapa([]);
  };

  const toggleFornecedor = (id: string) => {
    setSelecionadosMapa(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  const toggleTodos = () => {
    if (selecionadosMapa.length === fornecedoresMapa.length) {
      setSelecionadosMapa([]);
    } else {
      setSelecionadosMapa(fornecedoresMapa.map(f => f.id));
    }
  };

  const abrirNoMapaReal = () => {
    const lista = fornecedoresMapa.filter(f => selecionadosMapa.includes(f.id));
    if (lista.length === 0) return toast.error("Selecione pelo menos um fornecedor.");
    
    // Gera a URL do OpenStreetMap com os marcadores exatos
    let url = "https://www.openstreetmap.org/export/embed.html?bbox=";
    // ... (Lógica simplificada para pegar o centro e zoom)
    // Como o OSM não plota múltiplos marcadores via URL simples, 
    // abrimos a busca do Google Maps com os endereços concatenados
    const enderecos = lista.map(f => encodeURIComponent(`${f.endereco}, ${f.cidade}, ${f.estado}`)).join('|');
    window.open(`https://www.google.com/maps/dir/?api=1&waypoints=${enderecos}`, "_blank");
  };
'''
        idx = c.find('  return (')
        if idx != -1:
            c = c[:idx] + nova_logica + c[idx:]

        # Cria o novo Modal (Estados -> Lista -> Exportação)
        modal_novo = '''
      {/* MODAL DO MAPA INTELIGENTE */}
      {mapaAberto && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-2xl flex flex-col max-h-[90vh]">
            
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
              <h2 className="text-lg font-bold text-slate-100">Mapa dos Fornecedores</h2>
              <button onClick={() => setMapaAberto(false)} className="text-slate-400 hover:text-white">X</button>
            </div>

            <div className="p-6 overflow-y-auto flex-1 flex flex-col gap-4">
              {!estadoSelecionado ? (
                <div className="flex flex-col gap-3">
                  <Label className="text-slate-400">Selecione o Estado</Label>
                  <div className="grid grid-cols-3 gap-2">
                    <Button variant="outline" onClick={() => carregarFornecedoresEstado("TODOS")} className="h-10">Todos</Button>
                    {[...new Set(fornecedores.map(f => f.estado))].filter(Boolean).sort().map(uf => (
                      <Button key={uf} variant="outline" onClick={() => carregarFornecedoresEstado(uf)} className="h-10">{uf} ({fornecedores.filter(f => f.estado === uf).length})</Button>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="flex flex-col gap-3">
                  <div className="flex justify-between items-center">
                    <Label className="text-slate-400">Fornecedores em {estadoSelecionado} ({fornecedoresMapa.length})</Label>
                    <Button variant="ghost" size="sm" onClick={toggleTodos} className="text-sky-400">Marcar/Desmarcar Todos</Button>
                  </div>
                  
                  <div className="border border-slate-800 rounded-lg max-h-[300px] overflow-y-auto">
                    {fornecedoresMapa.map((f: any) => (
                      <label key={f.id} className="flex items-center gap-3 p-3 border-b border-slate-800 last:border-0 hover:bg-slate-800/50 cursor-pointer">
                        <input type="checkbox" checked={selecionadosMapa.includes(f.id)} onChange={() => toggleFornecedor(f.id)} className="size-4 accent-sky-500" />
                        <div>
                          <p className="text-sm font-medium text-slate-200">{f.nome}</p>
                          <p className="text-xs text-slate-500">{f.endereco}, {f.cidade} - {f.estado}</p>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end px-6 py-4 border-t border-slate-800 gap-3 bg-slate-900/50">
              {estadoSelecionado && (
                <>
                  <Button variant="outline" onClick={() => setEstadoSelecionado("")}>Voltar</Button>
                  <Button onClick={abrirNoMapaReal} disabled={selecionadosMapa.length === 0} className="bg-emerald-600 hover:bg-emerald-500">
                    Abrir no Mapa ({selecionadosMapa.length})
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
'''
        c = c.replace('    </div>\n  );\n}', modal_novo + '    </div>\n  );\n}')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend atualizado com o novo Modal de Mapa.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso! Faça o git push.")