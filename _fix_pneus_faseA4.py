import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PNEUS_FASEA4_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/models/veiculos.py",
        "app/backend/models/carretas.py",
        "app/backend/routers/veiculos.py",
        "app/backend/routers/carretas.py",
        "frontend/src/pages/Veiculos.tsx",
        "frontend/src/pages/Carretas.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    # 1. Adicionar campo template_chassi_id no Model de Veículos
    veic_model = os.path.join(raiz, "app", "backend", "models", "veiculos.py")
    with open(veic_model, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'template_chassi_id' not in c:
        c = c.replace(
            'configuracao_eixos: str | None = None',
            'configuracao_eixos: str | None = None\n    template_chassi_id: str | None = None'
        )
        with open(veic_model, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: campo template_chassi_id adicionado ao Model de Veículos.")

    # 2. Adicionar campo template_chassi_id no Model de Carretas
    carr_model = os.path.join(raiz, "app", "backend", "models", "carretas.py")
    with open(carr_model, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'template_chassi_id' not in c:
        c = c.replace(
            'configuracao_eixos: str | None = None',
            'configuracao_eixos: str | None = None\n    template_chassi_id: str | None = None'
        )
        with open(carr_model, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: campo template_chassi_id adicionado ao Model de Carretas.")

def fix_frontend_veiculos(raiz):
    # Adicionar o campo Template de Chassi no modal de Veículos
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Veiculos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar a query de templates (se não existir)
    if 'queryKey: ["chassi-templates"]' not in c:
        idx = c.find('const { data: veiculos')
        if idx != -1:
            c = c[:idx] + 'const { data: templates = [] } = useQuery({ queryKey: ["chassi-templates"], queryFn: () => apiGet<any[]>("/chassi-templates") });\n  ' + c[idx:]
            print("✅ Query de templates adicionada ao Veículos.tsx.")

    # 2. Adicionar o campo no estado do form (se não existir)
    if 'template_chassi_id' not in c:
        c = c.replace(
            'configuracao_eixos: "",',
            'configuracao_eixos: "",\n    template_chassi_id: "",'
        )
        # No abrirNovo
        c = c.replace(
            'configuracao_eixos: "",',
            'configuracao_eixos: "",\n        template_chassi_id: "",'
        )
        # No abrirEdicao
        c = c.replace(
            'configuracao_eixos: r.configuracao_eixos || "",',
            'configuracao_eixos: r.configuracao_eixos || "",\n        template_chassi_id: r.template_chassi_id || "",'
        )
        print("✅ Campo template_chassi_id adicionado ao estado do form de Veículos.")

    # 3. Adicionar o FieldSelect no modal (se não existir)
    if 'Template de Chassi' not in c:
        alvo = '<Label>Configuração de Eixos</Label>'
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
    # Adicionar o campo Template de Chassi no modal de Carretas
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
            'configuracao_eixos: "",',
            'configuracao_eixos: "",\n    template_chassi_id: "",'
        )
        c = c.replace(
            'configuracao_eixos: "",',
            'configuracao_eixos: "",\n        template_chassi_id: "",'
        )
        c = c.replace(
            'configuracao_eixos: r.configuracao_eixos || "",',
            'configuracao_eixos: r.configuracao_eixos || "",\n        template_chassi_id: r.template_chassi_id || "",'
        )
        print("✅ Campo template_chassi_id adicionado ao estado do form de Carretas.")

    # 3. Adicionar o FieldSelect no modal
    if 'Template de Chassi' not in c:
        alvo = '<Label>Configuração de Eixos</Label>'
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
    fix_backend(raiz)
    fix_frontend_veiculos(raiz)
    fix_frontend_carretas(raiz)
    print("\n✅ Fase A.4 (Aplicação do Template no Veículo) aplicada com sucesso!")