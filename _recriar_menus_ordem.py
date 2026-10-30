import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_RECRIAR_MENUS_{agora}.zip")
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

    # 1. LOCALIZAR E SUBSTITUIR O ARRAY MENUS INTEIRO
    padrao_menu = re.compile(r'const MENUS = \[[\s\S]*?\];', re.DOTALL)
    
    novo_menu = '''const MENUS = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, path: "/", isDashboard: true, items: [] },
  {
    id: "administracao", label: "Administração", icon: Shield,
    items: [
      { label: "Usuários", icon: UserCog, path: "/admin/usuarios" },
      { label: "Auditoria", icon: FileBox, path: "/admin/auditoria" },
      { label: "Avisos", icon: Bell, path: "/admin/avisos" },
      { label: "Segurança", icon: Shield, path: "/admin/seguranca" },
      { label: "Empresa", icon: Building, path: "/admin/empresa" },
      { label: "Parametrização", icon: Settings, path: "/admin/parametrizacao" },
      { label: "Base (Limpeza)", icon: FileText, path: "/admin/base" },
    ]
  },
  {
    id: "cadastros", label: "Cadastro", icon: FolderOpen,
    items: [
      { label: "Veículos", icon: Truck, path:"/cadastros/veiculos" },
      { label: "Carretas", icon: Car, path: "/cadastros/carretas" },
      { label: "Motoristas", icon: Users, path: "/cadastros/motoristas" },
      { label: "Combustíveis", icon: Fuel, path: "/cadastros/combustiveis" },
      { label: "Fornecedores", icon: Briefcase, path: "/cadastros/fornecedores" },
      { label: "Tipos de Fornecedores", icon:Tag, path: "/cadastros/tipos-fornecedores" },
      { label: "Cadastro de Planos", icon: Wrench, path: "/cadastros/planos-manutencao" },
    ]
  },
  { id: "financeiro", label: "Financeiro", icon: DollarSign, path: "/financeiro", items: [] },
  { id: "frota", label: "Frota", icon: Truck, path: "/frota", items: [] },
  {
    id: "gestao", label: "Gestão", icon: BarChart3,
    items: [
      { label: "Relatório de Manutenção", icon: FileBarChart, path: "/relatorio-manutencao" },
      { label: "Performance de Fornecedores",icon: BarChart3, path: "/relatorios/fornecedores" },
      { label: "Relatório de Estoque", icon: Package, path: "/relatorios/estoque" },
    ]
  },
  {
    id: "operacao", label: "Operação", icon: Activity,
    items: [
      { label: "Acoplamentos", icon: Settings, path: "/cadastros/acoplamentos" },
      { label: "Abastecimentos", icon: Fuel, path: "/abastecimentos" },
      { label: "Plano de Manutenção", icon: CalendarClock, path: "/agendamento" },
      { label: "Manutenções", icon: Wrench, path: "/manutencoes" },
      { label: "Pneus", icon: Disc, path: "/operacao/pneus" },
      { label: "Monitoramento", icon: Activity, path: "/operacao/monitoramento" },
      { label: "Estoque", icon: Package, path: "/operacao/estoque" },
    ]
  },
];'''

    if padrao_menu.search(c):
        c = padrao_menu.sub(novo_menu, c, count=1)
        print("✅ Array MENUS reescrito com a ordem alfabética e os novos menus.")
    else:
        print("⚠️ Não foi possível encontrar o array MENUS.")

    # 2. GARANTIR IMPORTS (FolderOpen)
    import_match = re.search(r'import\s*\{([^}]+)\}\s*from\s*["\']lucide-react["\']', c)
    if import_match:
        atuais = import_match.group(1)
        if 'FolderOpen' not in atuais:
            novos = atuais + ", FolderOpen"
            c = c[:import_match.start(1)] + novos + c[import_match.end(1):]
            print("✅ Import do FolderOpen adicionado.")
    else:
        print("⚠️ Import do lucide-react não encontrado para adicionar FolderOpen.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Sidebar.tsx atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")