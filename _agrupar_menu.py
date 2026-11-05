import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Procura se já existe um "Relatórios Gerais" para não duplicar
if "Relatórios Gerais" in c:
    print("ℹ️ O menu 'Relatórios Gerais' já existe. Vou apenas mover o link de Pneus para dentro dele se necessário.")
else:
    print("⚠️ O menu 'Relatórios Gerais' ainda não existe no código. Vou criar a estrutura básica.")

# Vamos procurar a linha onde o link de "Relatórios Pneus" foi inserido
# E vamos transformá-lo em um item dentro de um grupo.

# Como não sei a estrutura exata (pode ser objeto ou JSX), farei uma injeção segura.
# Se for objeto de navegação (ex: { label: "Pneus", ... }):
if "to: \"/operacao/relatorios-pneus\"" in c or "to: '/operacao/relatorios-pneus'" in c:
    print("📄 Estrutura baseada em Objetos detectada.")
    
    # Encontra o link exato que inserimos
    match = re.search(r'(\{[^{}]*to:\s*["\']\/operacao\/relatorios-pneus["\'][^{}]*\})', c)
    if match:
        link_str = match.group(1)
        # Remove o link do nível principal
        c = c.replace(link_str, "")
        
        # Cria a nova estrutura de grupo (Relatórios Gerais)
        # Inserindo logo após o link de Pneus principal
        novo_grupo = f'''
        {{ 
          label: "Relatórios Gerais", 
          icon: BarChart3, 
          children: [
            {link_str.replace("label: \"Relatórios Pneus\"", "label: \"Pneus\"")}
          ]
        }},
        '''
        
        # Coloca o novo grupo depois do link de veículos ou de pneus
        ancora = re.search(r'(\{[^{}]*to:\s*["\']\/operacao\/pneus["\'][^{}]*\})', c)
        if ancora:
            c = c.replace(ancora.group(1), ancora.group(1) + "," + novo_grupo)
            print("✅ Grupo 'Relatórios Gerais' criado e link movido para dentro.")

# Se for JSX (ex: <Link to="...">):
elif "/operacao/relatorios-pneus" in c:
    print("📄 Estrutura baseada em JSX detectada.")
    
    match = re.search(r'(<Link[^>]*to=["\']\/operacao\/relatorios-pneus["\'][^>]*>[\s\S]*?<\/Link>)', c)
    if match:
        link_jsx = match.group(1)
        c = c.replace(link_jsx, "")
        
        novo_grupo_jsx = f'''
        <div className="space-y-1">
          <div className="px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider mt-4 mb-2">Relatórios Gerais</div>
          {link_jsx}
        </div>
        '''
        
        ancora = re.search(r'(<Link[^>]*to=["\']\/operacao\/pneus["\'][^>]*>[\s\S]*?<\/Link>)', c)
        if ancora:
            c = c.replace(ancora.group(1), ancora.group(1) + "\n" + novo_grupo_jsx)
            print("✅ Grupo 'Relatórios Gerais' inserido acima do link.")

# Garante que o ícone BarChart3 esteja importado
if "BarChart3" not in c.split("export")[0]:
    c = re.sub(r'(import\s+\{[^}]*)\}', r'\1, BarChart3 }', c, count=1)
    print("✅ Ícone BarChart3 importado.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Sidebar.tsx atualizado! Verifique o visual no navegador após o Vite compilar.")