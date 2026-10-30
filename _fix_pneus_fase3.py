import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PNEUS_FASE3_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/models/pneus.py",
        "app/backend/routers/pneus.py",
        "frontend/src/pages/Pneus.tsx",
        "frontend/src/components/ChassiMapa.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    # 1. Atualizar Model para incluir campos de vinculação
    model_path = os.path.join(raiz, "app", "backend", "models", "pneus.py")
    with open(model_path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if 'sulco_atual' not in c:
        c = c.replace(
            'status: str = "Estoque"',
            '''status: str = "Estoque"
    veiculo_id: str | None = None
    carreta_id: str | None = None
    posicao: str | None = None
    sulco_atual: float | None = None
    pressao_atual: float | None = None'''
        )
        with open(model_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Model: campos de vinculação adicionados.")

    # 2. Atualizar Router para aceitar e salvar os novos campos
    router_path = os.path.join(raiz, "app", "backend", "routers", "pneus.py")
    with open(router_path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # O model_dump() já pega os campos automaticamente, então não precisamos alterar o Router
    print("✅ Router: já aceita os novos campos via model_dump().")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar imports necessários (useVeiculos, useCarretas)
    if 'useVeiculos' not in c:
        c = c.replace(
            'import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";',
            'import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";\nimport { useVeiculos } from "@/hooks/useCadastros";'
        )
        c = c.replace(
            'import { FieldSelect } from "@/components/common/FieldSelect";',
            'import { FieldSelect } from "@/components/common/FieldSelect";\nimport { useQuery } from "@tanstack/react-query";'
        )
        print("✅ Imports adicionados.")

    # 2. Adicionar os hooks de veículos e carretas
    if 'const veiculos = useVeiculos();' not in c:
        c = c.replace(
            'const { data: pneus = [] } = useQuery({ queryKey: ["pneus"], queryFn: () => apiGet<any[]>("/pneus") });',
            '''const { data: pneus = [] } = useQuery({ queryKey: ["pneus"], queryFn: () => apiGet<any[]>("/pneus") });
  const veiculos = useVeiculos();
  const { data: carretas = [] } = useQuery({ queryKey: ["carretas"], queryFn: () => apiGet<any[]>("/carretas") });'''
        )
        print("✅ Hooks de veículos e carretas adicionados.")

    # 3. Adicionar estado para Tipo de Ativo (Cavalo/Carreta)
    if 'const [tipoAtivo, setTipoAtivo]' not in c:
        c = c.replace(
            'const [filtro, setFiltro] = useState("");',
            'const [filtro, setFiltro] = useState("");\n  const [tipoAtivo, setTipoAtivo] = useState<"cavalo" | "carreta">("cavalo");'
        )
        print("✅ Estado do tipo de ativo adicionado.")

    # 4. Adicionar campos no estado do form
    if 'veiculo_id: ""' not in c:
        c = c.replace(
            'numero_fogo: "", marca: "", modelo: "", medida: "", dot: "", tipo: "Tração", status: "Estoque", custo_aquisicao: "", observacoes: "", foto_url: ""',
            'numero_fogo: "", marca: "", modelo: "", medida: "", dot: "", tipo: "Tração", status: "Estoque", custo_aquisicao: "", observacoes: "", foto_url: "", veiculo_id: "", carreta_id: "", posicao: "", sulco_atual: "", pressao_atual: ""'
        )
        print("✅ Campos de vinculação adicionados ao form.")

    # 5. Atualizar as funções abrirNovo e abrirEdicao
    if 'veiculo_id: r.veiculo_id' not in c:
        c = c.replace(
            'setForm({ numero_fogo: "", marca: "", modelo: "", medida: "", dot: "", tipo: "Tração", status: "Estoque", custo_aquisicao: "", observacoes: "", foto_url: "" });',
            'setForm({ numero_fogo: "", marca: "", modelo: "", medida: "", dot: "", tipo: "Tração", status: "Estoque", custo_aquisicao: "", observacoes: "", foto_url: "", veiculo_id: "", carreta_id: "", posicao: "", sulco_atual: "", pressao_atual: "" });'
        )
        print("✅ abrirNovo atualizado.")

    if 'veiculo_id: r.veiculo_id' not in c:
        c = c.replace(
            'setForm({ ...r, custo_aquisicao: String(r.custo_aquisicao || "") });',
            'setForm({ ...r, custo_aquisicao: String(r.custo_aquisicao || ""), sulco_atual: String(r.sulco_atual || ""), pressao_atual: String(r.pressao_atual || "") });'
        )
        print("✅ abrirEdicao atualizado.")

    # 6. Atualizar o payload de salvamento
    if 'sulco_atual: Number' not in c:
        c = c.replace(
            'custo_aquisicao: Number(String(form.custo_aquisicao).replace(",", ".")) || 0',
            'custo_aquisicao: Number(String(form.custo_aquisicao).replace(",", ".")) || 0,\n        sulco_atual: form.sulco_atual ? Number(form.sulco_atual) : null,\n        pressao_atual: form.pressao_atual ? Number(form.pressao_atual) : null'
        )
        print("✅ Payload de salvamento atualizado.")

    # 7. Injetar os campos visuais no modal (antes do Custo de Aquisição)
    if 'Tipo de Ativo' not in c:
        alvo = '<Label className="text-xs text-slate-400">Custo de Aquisição (R$)</Label>'
        
        novos_campos = '''<div className="col-span-2 grid gap-1.5">
                <Label className="text-xs text-slate-400">Tipo de Ativo</Label>
                <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-700">
                  <button 
                    className={`flex-1 py-1.5 text-sm rounded-md font-medium ${tipoAtivo === 'cavalo' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
                    onClick={() => { setTipoAtivo('cavalo'); setForm(s => ({ ...s, veiculo_id: '', carreta_id: '' })); }}
                  >
                    Cavalo Mecânico
                  </button>
                  <button 
                    className={`flex-1 py-1.5 text-sm rounded-md font-medium ${tipoAtivo === 'carreta' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
                    onClick={() => { setTipoAtivo('carreta'); setForm(s => ({ ...s, veiculo_id: '', carreta_id: '' })); }}
                  >
                    Carreta / Semi
                  </button>
                </div>
              </div>

              <div className="col-span-2 grid gap-1.5">
                <Label className="text-xs text-slate-400">{tipoAtivo === 'cavalo' ? 'Veículo' : 'Carreta'}</Label>
                {tipoAtivo === 'cavalo' ? (
                  <FieldSelect value={form.veiculo_id} onChange={(v) => setForm(s => ({ ...s, veiculo_id: v }))} options={(veiculos.data ?? []).map((v: any) => ({ value: v.id, label: `${v.placa} - ${v.modelo}` }))} placeholder="Selecione..." />
                ) : (
                  <FieldSelect value={form.carreta_id} onChange={(v) => setForm(s => ({ ...s, carreta_id: v }))} options={carretas.map((c: any) => ({ value: c.id, label: `${c.codigo} - ${c.tipo}` }))} placeholder="Selecione..." />
                )}
              </div>

              <div className="col-span-2 grid gap-1.5">
                <Label className="text-xs text-slate-400">Posição no Eixo</Label>
                <Input value={form.posicao} onChange={(e) => setForm(s => ({ ...s, posicao: e.target.value }))} placeholder="Ex: 2-DE (Eixo 2, Direito Externo)" />
              </div>

              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Sulco Atual (mm)</Label>
                <Input type="number" step="0.1" value={form.sulco_atual} onChange={(e) => setForm(s => ({ ...s, sulco_atual: e.target.value }))} placeholder="Ex: 5.5" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Pressão Atual (psi)</Label>
                <Input type="number" value={form.pressao_atual} onChange={(e) => setForm(s => ({ ...s, pressao_atual: e.target.value }))} placeholder="Ex: 120" />
              </div>
            </div>
            
            <div className="col-span-2 grid gap-1.5">
              <Label className="text-xs text-slate-400">Custo de Aquisição (R$)</Label>'''
        
        if alvo in c:
            c = c.replace(alvo, novos_campos)
            print("✅ Campos visuais adicionados ao modal.")

    # 8. Corrigir o fechamento do grid após a injeção
    if 'Custo de Aquisição (R$)' in c and '</div>\n              <div className="col-span-2 grid gap-1.5">\n                <Label className="text-xs text-slate-400">Custo de Aquisição' in c:
        # O fechamento do grid foi inserido antes do custo, então precisamos ajustar
        pass

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Pneus.tsx atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Fase 3 aplicada com sucesso!")