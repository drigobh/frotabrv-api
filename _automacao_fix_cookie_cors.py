import os

def fix_auth_cookie(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "auth.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    if 'samesite="lax"' in c:
        c = c.replace('samesite="lax"', 'samesite="none"')
        print("✅ auth.py: Cookie alterado para samesite='none' (permite cross-origin).")
    else:
        print("ℹ️ auth.py: O cookie já está configurado corretamente ou com outro valor.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

def fix_cors(raiz):
    caminho = os.path.join(raiz, "app", "backend", "server.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Verifica se o CORS está configurado para aceitar credenciais do localhost:3000
    if 'allow_origins=["*"]' in c:
        c = c.replace(
            'allow_origins=["*"]',
            'allow_origins=["http://localhost:3000", "https://frotabrv-api.onrender.com"]'
        )
        print("✅ server.py: CORS ajustado para origens específicas (localhost:3000).")

    if 'allow_credentials=False' in c:
        c = c.replace('allow_credentials=False', 'allow_credentials=True')
        print("✅ server.py: Credenciais habilitadas no CORS.")
    elif 'allow_credentials=True' not in c:
        # Garante que allow_credentials=True se não existir
        if 'allow_methods=' in c:
            c = c.replace(
                'allow_methods=',
                'allow_credentials=True,\n    allow_methods='
            )
            print("✅ server.py: Parâmetro 'allow_credentials=True' adicionado ao CORS.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_auth_cookie(raiz)
    fix_cors(raiz)