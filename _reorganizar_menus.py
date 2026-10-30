import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_REORGANIZAR_MENUS_{agora}.zip")
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

    # 1. Localizar e substituir o array MENUS inteiro
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
  {
    id: "frota", label: "Frota", icon: Truck,
    items: [
      { label: "Acoplamentos", icon: Settings, path: "/cadastros/acoplamentos" },
      { label: "Abastecimentos", icon: Fuel, path: "/abastecimentos" },
      { label: "Plano de Manutenção", icon: CalendarClock, path: "/agendamento" },
      { label: "Manutenções", icon: Wrench, path: "/manutencoes" },
      { label: "Pneus", icon: Disc, path: "/operacao/pneus" },
      { label: "Estoque", icon: Package, path: "/operacao/estoque" },
    ]
  },
  {
    id: "relatorios-gerais", label: "Relatórios Gerais", icon: BarChart3,
    items: [
      { label: "Relatório de Manutenção", icon: FileBarChart, path: "/relatorio-manutencao" },
      { label: "Performance de Fornecedores",icon: BarChart3, path: "/relatorios/fornecedores" },
      { label: "Relatório de Estoque", icon: Package, path: "/relatorios/estoque" },
    ]
  },
];'''

    if padrao_menu.search(c):
        c = padrao_menu.sub(novo_menu, c, count=1)
        print("✅ Array MENUS reorganizado com sucesso.")
    else:
        print("⚠️ Não foi possível encontrar o array MENUS.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Sidebar.tsx atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")