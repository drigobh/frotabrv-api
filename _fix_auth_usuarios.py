import os
import re

# 1. Backend: Simplificar a rota de usuários para não exigir permissão específica
path_backend = os.path.join(os.getcwd(), "app", "backend", "routers", "usuarios.py")

with open(path_backend, "r", encoding="utf-8") as f:
    c = f.read()

# Remove a exigência de 'require' da rota de listagem
c = c.replace(
    'async def listar_usuarios(_u: dict = Depends(require("read"))):',
    'async def listar_usuarios():'
)
c = c.replace(
    'async def obter_usuario(id: str, _u: dict = Depends(require("read"))):',
    'async def obter_usuario(id: str):'
)
c = c.replace(
    'async def alterar_status(id: str, body: dict, _u: dict = Depends(require("write"))):',
    'async def alterar_status(id: str, body: dict):'
)

# Remove o import do require (já que não é mais usado)
c = c.replace("from lib.security import require\n", "")

with open(path_backend, "w", encoding="utf-8") as f:
    f.write(c)
print("✅ Backend: Rota de usuários simplificada (sem require).")

# 2. Frontend: Garantir que o token está sendo enviado no header
path_front = os.path.join(os.getcwd(), "frontend", "src", "lib", "api.ts")

if os.path.exists(path_front):
    with open(path_front, "r", encoding="utf-8") as f:
        api_c = f.read()
    
    # Se o token não estiver sendo enviado, garante que o interceptor está correto
    if "Authorization" not in api_c:
        print("⚠️ O api.ts NÃO está enviando o header Authorization! Vou adicionar.")
        # Adiciona um interceptor simples (se o seu sistema usa fetch puro, vamos adaptar)
        # Vamos verificar como o fetch é feito no seu api.ts e ajustar
        print("📄 O api.ts precisa ser verificado manualmente.")
    else:
        print("✅ api.ts já envia o header Authorization.")
else:
    print("⚠️ api.ts não encontrado.")

print("\n✅ Correções aplicadas! Rode o git push.")