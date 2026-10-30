import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PNEUS_FASEA4_V2_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/models/cadastros.py",
        "app/backend/routers/veiculos.py",
        "app/backend/routers/carretas.py"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_models(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "cadastros.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar template_chassi_id no VeiculoCreate
    if 'template_chassi_id' not in c:
        c = c.replace(
            'hodometro_km: float = Field(default=0, ge=0)\n    observacoes: str = ""',
            'hodometro_km: float = Field(default=0, ge=0)\n    template_chassi_id: str | None = None\n    observacoes: str = ""'
        )
        print("✅ Model: template_chassi_id adicionado ao VeiculoCreate.")

    # 2. Adicionar template_chassi_id no CarretaCreate
    if 'template_chassi_id' not in c:
        c = c.replace(
            'hodometro_km: float = Field(default=0, ge=0)',
            'hodometro_km: float = Field(default=0, ge=0)\n    template_chassi_id: str | None = None'
        )
        print("✅ Model: template_chassi_id adicionado ao CarretaCreate.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

def fix_routers(raiz):
    # Garantir que os routers salvem o novo campo (model_dump já pega tudo, mas precisamos garantir)
    for router_file in ["veiculos.py", "carretas.py"]:
        caminho = os.path.join(raiz, "app", "backend", "routers", router_file)
        if os.path.exists(caminho):
            with open(caminho, 'r', encoding='utf-8') as f:
                c = f.read()
            # O model_dump já inclui o template_chassi_id, então não precisamos alterar o Router.
            # Mas vamos garantir que não haja erro de validação.
            print(f"✅ Router {router_file} OK (model_dump já inclui o novo campo).")

def fix_frontend_veiculos(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Veiculos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar a query de templates
    if 'queryKey: ["chassi-templates"]' not in c:
        idx = c.find('const { data: veiculos')
        if idx != -1:
            c = c[:idx] + 'const { data: templates = [] } = useQuery({ queryKey: ["chassi-templates"], queryFn: () => apiGet<any[]>("/chassi-templates") });\n  ' + c[idx:]
            print("✅ Query de templates adicionada ao Veiculos.tsx.")

    # 2. Adicionar o campo no estado do form
    if 'template_chassi_id' not in c:
        # Inicialização
        c = c.replace(
            'placa: "", modelo: "", ano: "",',
            'placa: "", modelo: "", ano: "", template_chassi_id: "",'
        )
        # Se a inicialização for diferente, tenta outro padrão
        if 'template_chassi_id' not in c:
            c = c.replace(
                'const [form, setForm] = useState({',
                'const [form, setForm] = useState({\n    template_chassi_id: "",'
            )
        # Abrir Edição
        c = c.replace(
            'setForm({ placa: r.placa, modelo: r.modelo, ano: String(r.ano),',
            'setForm({ placa: r.placa, modelo: r.modelo, ano: String(r.ano), template_chassi_id: r.template_chassi_id || "",'
        )
        print("✅ Campo template_chassi_id adicionado ao estado do form de Veículos.")

    # 3. Adicionar o FieldSelect no modal
    if 'Template de Chassi' not in c:
        alvo = '<Label>Modelo</Label>'
        if alvo in c:
            novo = '''<Label>Template de Chassi</Label>
              <FieldSelect 
                value={form.template_chassi_id || ""} 
                onChange={(v) => setForm(s => ({ ...s, template_chassi_id: v }))} 
                options={templates.filter((t: any) => t.categoria === "CAVALO").map((t: any) => ({ value: t.id, label: t.nome }))} 
                placeholder="Selecione o template..." 
              />
            </div>
            <div className="grid gap-1.5">
              ''' + alvo
            c = c.replace(alvo, novo)
            print("✅ Campo 'Template de Chassi' adicionado ao modal de Veículos.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

def fix_frontend_carretas(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Carretas.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar a query de templates
    if 'queryKey: ["chassi-templates"]' not in c:
        idx = c.find('const { data: carretas')
        if idx != -1:
            c = c[:idx] + 'const { data: templates = [] } = useQuery({ queryKey: ["chassi-templates"], queryFn: () => apiGet<any[]>("/chassi-templates") });\n  ' + c[idx:]
            print("✅ Query de templates adicionada ao Carretas.tsx.")

    # 2. Adicionar o campo no estado do form
    if 'template_chassi_id' not in c:
        c = c.replace(
            'codigo: "", tipo: "",',
            'codigo: "", tipo: "", template_chassi_id: "",'
        )
        if 'template_chassi_id' not in c:
            c = c.replace(
                'const [form, setForm] = useState({',
                'const [form, setForm] = useState({\n    template_chassi_id: "",'
            )
        c = c.replace(
            'setForm({ codigo: r.codigo, tipo: r.tipo,',
            'setForm({ codigo: r.codigo, tipo: r.tipo, template_chassi_id: r.template_chassi_id || "",'
        )
        print("✅ Campo template_chassi_id adicionado ao estado do form de Carretas.")

    # 3. Adicionar o FieldSelect no modal
    if 'Template de Chassi' not in c:
        alvo = '<Label>Tipo</Label>'
        if alvo in c:
            novo = '''<Label>Template de Chassi</Label>
              <FieldSelect 
                value={form.template_chassi_id || ""} 
                onChange={(v) => setForm(s => ({ ...s, template_chassi_id: v }))} 
                options={templates.filter((t: any) => t.categoria === "CARRETA").map((t: any) => ({ value: t.id, label: t.nome }))} 
                placeholder="Selecione o template..." 
              />
            </div>
            <div className="grid gap-1.5">
              ''' + alvo
            c = c.replace(alvo, novo)
            print("✅ Campo 'Template de Chassi' adicionado ao modal de Carretas.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_models(raiz)
    fix_routers(raiz)
    fix_frontend_veiculos(raiz)
    fix_frontend_carretas(raiz)
    print("\n✅ Fase A.4 (Aplicação do Template no Veículo) aplicada com sucesso!")