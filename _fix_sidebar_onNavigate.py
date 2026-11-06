import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Garantir que a assinatura do componente aceite onNavigate
if "onNavigate" not in c.split("export function Sidebar")[1].split(")")[0]:
    c = c.replace(
        'export function Sidebar() {',
        'export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {'
    )
    # Se a assinatura for diferente
    c = re.sub(r'export function Sidebar\([^)]*\)', 'export function Sidebar({ onNavigate }: { onNavigate?: () => void })', c, count=1)

# 2. Chamar onNavigate ao clicar em qualquer link do menu (para fechar o mobile)
# Vamos adicionar o onClick nos Links do menu principal e submenus
c = c.replace(
    'to={item.path}',
    'to={item.path} onClick={onNavigate}'
)
c = c.replace(
    'to={menu.path}',
    'to={menu.path} onClick={onNavigate}'
)
c = c.replace(
    'to="/perfil"',
    'to="/perfil" onClick={onNavigate}'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Sidebar.tsx corrigido: aceita onNavigate e fecha o menu mobile ao clicar.")