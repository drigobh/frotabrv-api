import os
import re
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_rapido_rota_{agora}.zip"
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print("📦 Criando Backup Rápido...")
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pasta_front = os.path.join(raiz, "frontend", "src")
        for root, dirs, files in os.walk(pasta_front):
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', 'build']]
            for file in files:
                caminho_completo = os.path.join(root, file)
                caminho_relativo = os.path.relpath(caminho_completo, raiz)
                try:
                    zipf.write(caminho_completo, caminho_relativo)
                except Exception:
                    pass

def corrigir_app_tsx(raiz):
    caminho_app = os.path.join(raiz, "frontend", "src", "App.tsx")
    if not os.path.exists(caminho_app):
        print("❌ App.tsx não encontrado.")
        return

    with open(caminho_app, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Garante o import do Base
    if "import Base from" not in conteudo:
        conteudo = conteudo.replace(
            "import Abastecimentos",
            "import Base from '@/pages/Base';\nimport Abastecimentos"
        )
        print("✅ Import do Base adicionado no App.tsx.")

    # 2. Garante a rota
    if 'path="/admin/base"' not in conteudo and 'path="admin/base"' not in conteudo:
        # Tenta inserir depois da rota do Dashboard
        if '<Route index element={<Dashboard />} />' in conteudo:
            conteudo = conteudo.replace(
                '<Route index element={<Dashboard />} />',
                '<Route index element={<Dashboard />} />\n          <Route path="/admin/base" element={<Base />} />'
            )
            print("✅ Rota '/admin/base' adicionada no App.tsx (após Dashboard).")
        elif '<Route path="/abastecimentos"' in conteudo:
             conteudo = conteudo.replace(
                '<Route path="/abastecimentos"',
                '<Route path="/admin/base" element={<Base />} />\n          <Route path="/abastecimentos"'
            )
             print("✅ Rota '/admin/base' adicionada no App.tsx (antes de Abastecimentos).")
        else:
            print("⚠️ Não foi possível encontrar um ponto de ancoragem no App.tsx. A rota pode não ter sido adicionada.")
    else:
        print("ℹ️ Rota '/admin/base' já existe no App.tsx.")

    with open(caminho_app, 'w', encoding='utf-8') as f:
        f.write(conteudo)

def simplificar_base_tsx(raiz):
    # Remove o PageHeader do Base.tsx, caso ele seja o problema
    caminho_base = os.path.join(raiz, "frontend", "src", "pages", "Base.tsx")
    if not os.path.exists(caminho_base):
        return
        
    with open(caminho_base, 'r', encoding='utf-8') as f:
        conteudo = f.read()
        
    # Substitui o PageHeader por um HTML simples de título
    padrao = re.compile(r'<PageHeader[\s\S]*?/>', re.DOTALL)
    if padrao.search(conteudo):
        novo_header = '''<div className="mb-6">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Administração</p>
        <h1 className="text-2xl font-bold text-slate-100 mt-1">Limpeza de Base</h1>
        <p className="text-sm text-slate-400 mt-1">Apague os dados de tabelas específicas. O sistema gera um backup automático.</p>
      </div>'''
        conteudo = padrao.sub(novo_header, conteudo)
        
        # Remove o import do PageHeader se não for mais usado
        conteudo = conteudo.replace('import { PageHeader } from "@/components/common/PageHeader";\n', '')
        
        with open(caminho_base, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Página Base.tsx simplificada (removido PageHeader).")

if __name__ == "__main__":
    raiz = os.getcwd()
    print("🤖 Iniciando Correção Forçada da Rota Base...")
    criar_backup_rapido(raiz)
    corrigir_app_tsx(raiz)
    simplificar_base_tsx(raiz)
    print("\n🚀 Concluído! Reinicie o Vite.")