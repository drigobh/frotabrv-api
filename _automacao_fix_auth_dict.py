import os

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "auth.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Substitui o retorno do LoginOut por um dicionário direto com o token
    if 'return LoginOut(requires_2fa=False, user=user)' in c:
        c = c.replace(
            'return LoginOut(requires_2fa=False, user=user)',
            'return {"requires_2fa": False, "user": user, "token": token}'
        )
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota de login retorna um dicionário direto com o token.")
    else:
        print("ℹ️ Backend: Rota já retorna dicionário ou estrutura diferente. Nada a alterar.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Login.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    if 'localStorage.setItem("token", r.token)' in c:
        print("ℹ️ Frontend: Login.tsx já estava salvando o token.")
        return

    if 'beginSession();' in c:
        c = c.replace(
            'beginSession();',
            '''if (r.token) { localStorage.setItem("token", r.token); localStorage.setItem("auth_token", r.token); }
      beginSession();'''
        )
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Frontend: Login.tsx salva o token antes do beginSession.")
    else:
        print("⚠️ Frontend: Não foi possível encontrar o beginSession no Login.tsx.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)