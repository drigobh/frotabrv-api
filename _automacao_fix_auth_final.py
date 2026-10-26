import os

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "auth.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Garante que a resposta do login contenha o token no corpo (além do Cookie)
    if 'LoginOut(requires_2fa=False, user=user)' in c and 'token=token' not in c:
        # Adiciona a classe LoginOut o campo token, se ainda não existir
        model_path = os.path.join(raiz, "app", "backend", "models", "auth.py")
        with open(model_path, 'r', encoding='utf-8') as fm:
            cm = fm.read()
        if 'class LoginOut' in cm and 'token:' not in cm:
            cm = cm.replace('class LoginOut(BaseModel):', 'class LoginOut(BaseModel):\n    token: str | None = None')
            with open(model_path, 'w', encoding='utf-8') as fm:
                fm.write(cm)
            print("✅ Modelo LoginOut atualizado com campo 'token'.")

        c = c.replace('return LoginOut(requires_2fa=False, user=user)', 'return LoginOut(requires_2fa=False, user=user, token=token)')
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota de login agora retorna o token no corpo.")
    else:
        print("ℹ️ Backend: Rota de login já estava retornando o token ou não foi encontrada.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Login.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Verifica se já salvamos o token
    if 'localStorage.setItem("token", r.token)' in c:
        print("ℹ️ Frontend: Login.tsx já estava salvando o token.")
        return

    # Insere o salvamento logo após verificar 2FA e antes do beginSession
    if 'beginSession();' in c:
        c = c.replace(
            'beginSession();',
            '''if (r.token) { localStorage.setItem("token", r.token); localStorage.setItem("auth_token", r.token); }
      beginSession();'''
        )
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Frontend: Login.tsx agora salva o token antes do beginSession.")
    else:
        print("⚠️ Frontend: Não foi possível encontrar o ponto de injeção no Login.tsx.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)