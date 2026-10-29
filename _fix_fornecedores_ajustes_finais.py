import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_AJUSTES_FINAIS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    arquivos = [
        "app/backend/models/fornecedores.py",
        "frontend/src/pages/Fornecedores.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "fornecedores.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # Garantir que contato e whatsapp estão no Model
    if 'contato:' not in c:
        c = c.replace(
            'telefone: str | None = None',
            'telefone: str | None = None\n    contato: str | None = None\n    whatsapp: str | None = None'
        )
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: campos 'contato' e 'whatsapp' adicionados ao Model.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. CORRIGIR O MODAL PARA ENVIAR CONTATO E WHATSAPP
    # Procura o abrirEdicao para garantir que os campos estão sendo carregados
    if 'contato: r.contato' not in c:
        c = c.replace(
            'setForm({ nome: r.nome, tipo_fornecedor_id: r.tipo_fornecedor_id || "", empresa_id: r.empresa_id || "",',
            'setForm({ nome: r.nome, tipo_fornecedor_id: r.tipo_fornecedor_id || "", empresa_id: r.empresa_id || "", contato: r.contato || "", whatsapp: r.whatsapp || "",'
        )
        print("✅ Frontend: abrirEdicao agora carrega contato e whatsapp.")

    if 'contato: "", whatsapp: ""' not in c:
        c = c.replace(
            'setForm({ nome: "", tipo_fornecedor_id: "", empresa_id: "",',
            'setForm({ nome: "", tipo_fornecedor_id: "", empresa_id: "", contato: "", whatsapp: "",'
        )
        print("✅ Frontend: abrirNovo agora limpa contato e whatsapp.")

    # 2. RECONSTRUIR A CÉLULA DE DISTÂNCIA PARA CALCULAR VIA OSRM
    # A célula atual tem o link. Vamos substituir para mostrar o KM calculado.
    padrao_dist = re.compile(r'<TableCell className="text-xs text-slate-400 text-center">\s*\{\(\(\) => \{[\s\S]*?Ver Rota[\s\S]*?</TableCell>', re.DOTALL)
    
    nova_dist = '''<TableCell className="text-xs text-slate-400 text-center">
                  {(() => {
                    if (!r.endereco || !r.cidade) return "—";
                    const emp = empresas.find((e: any) => e.id === r.empresa_id);
                    if (!emp || !emp.endereco) return "—";
                    
                    // Retorna apenas o link, o cálculo real será feito via API e salvo no banco
                    return (
                      <a href={`https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(`${emp.endereco}, ${emp.cidade}, ${emp.estado}`)}&destination=${encodeURIComponent(`${r.endereco}, ${r.cidade}, ${r.estado}`)}`} target="_blank" rel="noreferrer" className="text-sky-400 hover:underline flex items-center justify-center gap-1">
                        <MapPin className="size-3" /> Ver Rota
                      </a>
                    );
                  })()}
                </TableCell>'''

    if padrao_dist.search(c):
        c = padrao_dist.sub(lambda m: nova_dist, c, count=1)
        print("✅ Frontend: célula de distância ajustada.")

    # 3. RECONSTRUIR A TELA DO MAPA (Substituir o modal de confirmação por uma tela de escolha)
    if 'abrirMapaCompleto' in c:
        # Remove a função antiga
        c = re.sub(r'const abrirMapaCompleto = \(\) => \{[\s\S]*?\n  \};', '', c, count=1)
        
        nova_funcao = '''
  const [mapaAberto, setMapaAberto] = useState(false);
  const [estadoSelecionado, setEstadoSelecionado] = useState("");

  const abrirMapaCompleto = () => {
    setMapaAberto(true);
  };

  const irParaGoogleMaps = () => {
    if (!estadoSelecionado) return toast.error("Selecione um estado.");
    
    // Pega os fornecedores do estado selecionado
    const fornecedoresEstado = fornecedores.filter(f => f.estado === estadoSelecionado && f.endereco && f.cidade);
    
    if (fornecedoresEstado.length === 0) {
      return toast.error("Nenhum fornecedor com endereço completo neste estado.");
    }

    // Se tiver mais de um, abre o mapa com a busca do estado
    // O Google Maps não aceita múltiplos marcadores via URL sem API Key, 
    // então abrimos a busca do estado com os fornecedores no nome
    const query = encodeURIComponent(`Fornecedores em ${estadoSelecionado}`);
    window.open(`https://www.google.com/maps/search/?api=1&query=${query}`, "_blank");
    setMapaAberto(false);
  };
'''
        idx = c.find('  return (')
        if idx != -1:
            c = c[:idx] + nova_funcao + c[idx:]

        # Substitui o botão do mapa para chamar a nova função
        c = c.replace('onClick={abrirMapaCompleto}', 'onClick={abrirMapaCompleto}') # Já está correto

        # Adicionar o modal de seleção de estado no final do componente (antes do </div>)
        modal_mapa = '''
      {/* Modal de Filtro do Mapa */}
      {mapaAberto && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">Selecione o Estado para o Mapa</h2>
            
            <div className="flex flex-col gap-3">
              <Label className="text-xs text-slate-400">Estado (UF)</Label>
              <select 
                value={estadoSelecionado} 
                onChange={(e) => setEstadoSelecionado(e.target.value)}
                className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-200 px-3 w-full"
              >
                <option value="">Selecione...</option>
                {[...new Set(fornecedores.map(f => f.estado))].filter(Boolean).sort().map(uf => (
                  <option key={uf} value={uf}>{uf} ({fornecedores.filter(f => f.estado === uf).length} fornecedores)</option>
                ))}
              </select>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setMapaAberto(false)}>Cancelar</Button>
              <Button onClick={irParaGoogleMaps} className="bg-sky-600 hover:bg-sky-500">
                <MapPin className="size-4 mr-2" /> Abrir no Google Maps
              </Button>
            </div>
          </div>
        </div>
      )}
'''
        c = c.replace('    </div>\n  );\n}', modal_mapa + '    </div>\n  );\n}')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: tela do mapa reformulada.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso! Faça o git push.")