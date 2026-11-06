import os
import re

# ==========================================
# 1. SIDEBAR: CRIAR FUNÇÃO DE LOGOFF E BOTÃO
# ==========================================
path_sidebar = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path_sidebar, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Remove qualquer botão "Sair" antigo (que pode estar com onClick bugado)
c = re.sub(r'<Button[^>]*>[\s\S]*?Sair[\s\S]*?</Button>', '', c, flags=re.DOTALL)

# 2. Adiciona a função de logoff no componente
if "const handleLogoff" not in c:
    match_comp = re.search(r'(export function Sidebar\(\)\s*\{)', c)
    if match_comp:
        c = c.replace(match_comp.group(1), match_comp.group(1) + """
  const handleLogoff = async () => {
    try {
      // Limpa o cache do React Query (se estiver acessível)
      if (window.__REACT_QUERY_CLIENT__) {
        window.__REACT_QUERY_CLIENT__.clear();
      }
    } catch (e) {}
    // Limpa todo o armazenamento local e de sessão
    localStorage.clear();
    sessionStorage.clear();
    // Redireciona para a tela de login, forçando recarregamento completo
    window.location.replace("/login");
  };
""")

# 3. Adiciona o novo botão de Logoff no rodapé (substituindo o antigo)
novo_botao = '''
        <Button 
          variant="ghost" 
          className={cn("w-full text-red-400 hover:text-red-300 hover:bg-red-500/10 h-9 mt-2", isCollapsed ? "justify-center px-0" : "justify-start px-3")} 
          onClick={handleLogoff}
        >
          <LogOut className={cn("size-4", !isCollapsed && "mr-2")} /> 
          {!isCollapsed && "Encerrar Sessão"}
        </Button>
'''

# Encontra o fechamento da div de rodapé (após o Link do perfil) e insere o botão
c = c.replace(
    '</Link>\n        <Button',
    '</Link>\n        ' + novo_botao + '\n        <Button'
)

with open(path_sidebar, "w", encoding="utf-8") as f:
    f.write(c)
print("✅ Sidebar: Botão de Logoff criado e função handleLogoff injetada.")

# ==========================================
# 2. APP: CONFIGURAR EXPIRAÇÃO DE SESSÃO AO FECHAR A ABA
# ==========================================
path_app = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")

with open(path_app, "r", encoding="utf-8") as f:
    app_c = f.read()

# Adiciona um listener para limpar o storage quando a aba for fechada
# (usando o evento beforeunload)
if "beforeunload" not in app_c:
    # Insere no início do componente App
    match_app = re.search(r'(export default function App\(\)\s*\{)', app_c)
    if match_app:
        app_c = app_c.replace(match_app.group(1), match_app.group(1) + """
  // Garante que o token seja removido se a aba for fechada
  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', () => {
      localStorage.removeItem('token');
      sessionStorage.clear();
    });
  }
""")

with open(path_app, "w", encoding="utf-8") as f:
    f.write(app_c)
print("✅ App.tsx: Expiração de sessão ao fechar a aba configurada.")

print("✅ Tudo pronto! Faça o git push.")