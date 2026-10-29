import os
import re  # <-- A correção está aqui
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_RESTAURAR_MAPA_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "frontend/src/pages/Fornecedores.tsx",
        "frontend/src/components/MapaFornecedores.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_fornecedores_page(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    padrao_rota = re.compile(r'<TableCell className="text-xs text-slate-400 text-center">\s*\{\(\(\) => \{[\s\S]*?<\/TableCell>', re.DOTALL)
    
    nova_rota = '''<TableCell className="text-xs text-slate-400 text-center">
                  {(() => {
                    const emp = empresas.find((e: any) => e.id === r.empresa_id);
                    if (!emp || !emp.endereco || !r.endereco) return "—";
                    const origem = encodeURIComponent(`${emp.endereco}, ${emp.cidade}, ${emp.estado}`);
                    const destino = encodeURIComponent(`${r.endereco}, ${r.cidade}, ${r.estado}`);
                    return (
                      <a href={`https://www.google.com/maps/dir/?api=1&origin=${origem}&destination=${destino}`} target="_blank" rel="noreferrer" className="text-sky-400 hover:underline flex items-center justify-center gap-1">
                        <MapPin className="size-3" /> Ver Rota
                      </a>
                    );
                  })()}
                </TableCell>'''
    
    if padrao_rota.search(c):
        c = padrao_rota.sub(lambda m: nova_rota, c, count=1)
        print("✅ Coluna Rota restaurada (link para o Google Maps).")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Fornecedores.tsx atualizado.")

def fix_mapa(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "MapaFornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Restaurar o MapController (para o mapa dar zoom)
    if 'function MapController(' not in c:
        c = c.replace(
            'L.Marker.prototype.options.icon = DefaultIcon;',
            '''L.Marker.prototype.options.icon = DefaultIcon;

function MapController({ center, zoom }: { center: [number, number], zoom: number }) {
  const map = useMap();
  map.setView(center, zoom);
  return null;
}'''
        )
        print("✅ Função MapController restaurada (zoom).")

    # 2. Corrigir a lógica do mapa para usar o MapController
    if '<MapController' not in c:
        c = c.replace(
            '<MapContainer center={center} zoom={zoom} style={{ height: "100%", width: "100%" }}>',
            '''<MapContainer center={center} zoom={zoom} style={{ height: "100%", width: "100%" }}>
              <MapController center={center} zoom={zoom} />'''
        )
        print("✅ MapController integrado ao MapContainer.")

    # 3. Restaurar os filtros (select de tipo e input de nome)
    if 'filtroTipo' not in c:
        c = c.replace(
            'const [estadoSelecionado, setEstadoSelecionado] = useState("");',
            'const [estadoSelecionado, setEstadoSelecionado] = useState("");\n  const [filtroNome, setFiltroNome] = useState("");\n  const [filtroTipo, setFiltroTipo] = useState("");'
        )
        c = c.replace(
            '<div className="p-4 border-b border-slate-800 space-y-2">\n              <Input \n                placeholder="Buscar fornecedor..." \n                value={filtroNome} \n                onChange={(e) => setFiltroNome(e.target.value)} \n                className="h-9 bg-slate-950" \n              />\n            </div>',
            '''<div className="p-4 border-b border-slate-800 space-y-2">
              <Input placeholder="Buscar fornecedor..." value={filtroNome} onChange={(e) => setFiltroNome(e.target.value)} className="h-9 bg-slate-950" />
              <select value={filtroTipo} onChange={(e) => setFiltroTipo(e.target.value)} className="w-full h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                <option value="">Todos os Tipos</option>
                {tipos.filter((t: any) => t.categoria_pai_id).map((t: any) => (
                  <option key={t.id} value={t.id}>{t.nome}</option>
                ))}
              </select>
            </div>'''
        )
        print("✅ Filtros de Nome e Tipo restaurados.")

    # 4. Restaurar a lógica de filtragem (fornecedoresFiltrados)
    if 'fornecedoresFiltrados' not in c:
        c = c.replace(
            'const estados = [...new Set(fornecedores.map(f => f.estado))].filter(Boolean).sort();',
            '''const estados = [...new Set(fornecedores.map(f => f.estado))].filter(Boolean).sort();

  const fornecedoresFiltrados = fornecedores.filter((f: any) => {
    let match = true;
    if (estadoSelecionado && f.estado !== estadoSelecionado) match = false;
    if (filtroNome && !f.nome.toLowerCase().includes(filtroNome.toLowerCase())) match = false;
    if (filtroTipo && f.tipo_fornecedor_id !== filtroTipo) match = false;
    return match;
  });'''
        )
        print("✅ Lógica de filtragem restaurada.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ MapaFornecedores.tsx atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_fornecedores_page(raiz)
    fix_mapa(raiz)
    print("\n✅ Script aplicado com sucesso! Faça o git push.")