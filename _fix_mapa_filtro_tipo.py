import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MAPA_FILTRO_TIPO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    arquivos = [
        "frontend/src/components/MapaFornecedores.tsx",
        "frontend/src/pages/Fornecedores.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_mapa(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "MapaFornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar a prop 'tipos' na interface e na desestruturação
    if 'tipos: any[];' not in c:
        c = c.replace(
            'fornecedores: any[];\n}',
            'fornecedores: any[];\n  tipos: any[];\n}'
        )
        c = c.replace(
            'export function MapaFornecedores({ open, onOpenChange, fornecedores }: MapaProps) {',
            'export function MapaFornecedores({ open, onOpenChange, fornecedores, tipos }: MapaProps) {'
        )
        print("✅ Props 'tipos' adicionada ao componente.")

    # 2. Adicionar o FieldSelect (ou select nativo) na barra de filtros da lista
    if 'filtroTipo' not in c:
        # Encontra a div que tem o input de busca
        alvo = '<div className="p-4 border-b border-slate-800 space-y-2">\n              <Input \n                placeholder="Buscar fornecedor..." \n                value={filtroNome} \n                onChange={(e) => setFiltroNome(e.target.value)} \n                className="h-9 bg-slate-950" \n              />\n            </div>'
        
        novo = '''<div className="p-4 border-b border-slate-800 space-y-2">
              <Input 
                placeholder="Buscar fornecedor..." 
                value={filtroNome} 
                onChange={(e) => setFiltroNome(e.target.value)} 
                className="h-9 bg-slate-950" 
              />
              <select 
                value={filtroTipo} 
                onChange={(e) => setFiltroTipo(e.target.value)}
                className="w-full h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2 focus:outline-none focus:ring-1 focus:ring-sky-500"
              >
                <option value="">Todos os Tipos</option>
                {tipos.filter(t => t.categoria_pai_id).map(t => (
                  <option key={t.id} value={t.id}>{t.nome}</option>
                ))}
              </select>
            </div>'''
        
        if alvo in c:
            c = c.replace(alvo, novo)
            print("✅ Select de Tipo adicionado na barra de filtros.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Componente MapaFornecedores.tsx atualizado.")

def fix_fornecedores_page(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Passar a prop 'tipos' para o componente MapaFornecedores
    if '<MapaFornecedores ' in c and 'tipos={tipos}' not in c:
        c = c.replace(
            '<MapaFornecedores open={mapaAberto} onOpenChange={setMapaAberto} fornecedores={fornecedores} />',
            '<MapaFornecedores open={mapaAberto} onOpenChange={setMapaAberto} fornecedores={fornecedores} tipos={tipos} />'
        )
        print("✅ Prop 'tipos' passada para o MapaFornecedores.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Página Fornecedores.tsx atualizada.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_mapa(raiz)
    fix_fornecedores_page(raiz)
    print("\n✅ Script aplicado com sucesso!")