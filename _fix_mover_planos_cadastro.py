import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MOVER_PLANOS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/components/layout/Sidebar.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Remove o item do menu Operação
    item_operacao = '      { label: "Cadastro de Planos", icon: Wrench, path: "/planos-manutencao" },\n'
    if item_operacao in c:
        c = c.replace(item_operacao, '')
        print("✅ Item removido do menu Operação.")

    # 2. Adiciona o item no menu Cadastros (logo após Tipos de Fornecedores)
    if 'label: "Cadastro de Planos"' not in c:
        alvo_cadastro = '{ label: "Tipos de Fornecedores", icon: Tag, path: "/cadastros/tipos-fornecedores" },'
        if alvo_cadastro in c:
            c = c.replace(
                alvo_cadastro,
                alvo_cadastro + '\n      { label: "Cadastro de Planos", icon: Wrench, path: "/cadastros/planos-manutencao" },'
            )
            print("✅ Item adicionado ao menu Cadastros.")
        else:
            # Fallback: adiciona após o item "Fornecedores"
            alvo_forn = '{ label: "Fornecedores", icon: Truck, path: "/fornecedores" },'
            if alvo_forn in c:
                c = c.replace(
                    alvo_forn,
                    alvo_forn + '\n      { label: "Cadastro de Planos", icon: Wrench, path: "/cadastros/planos-manutencao" },'
                )
                print("✅ Item adicionado ao menu Cadastros (via fallback).")

    # 3. Atualiza a rota no App.tsx de /planos-manutencao para /cadastros/planos-manutencao
    app_path = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(app_path, 'r', encoding='utf-8') as f:
        c_app = f.read()
    
    if '/cadastros/planos-manutencao' not in c_app:
        c_app = c_app.replace(
            '<Route path="/planos-manutencao" element={<PlanosManutencao />} />',
            '<Route path="/cadastros/planos-manutencao" element={<PlanosManutencao />} />'
        )
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(c_app)
        print("✅ Rota atualizada no App.tsx para /cadastros/planos-manutencao.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Sidebar atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")
    