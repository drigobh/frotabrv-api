import os
import re

def fix_backend_login(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "auth.py")
    
    if not os.path.exists(caminho):
        print("❌ Arquivo auth.py não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Verifica se já retorna token
    if '"token":' in c:
        print("ℹ️ A rota de login já retorna o token.")
        return

    # Encontra o bloco de sucesso do login e injeta o token no retorno
    padrao = re.compile(r'(return\s*\{\s*"requires_2fa":\s*False,\s*"user":\s*[^}]+\})', re.DOTALL)
    
    if padrao.search(c):
        c = padrao.sub(r'\1, "token": token', c)
        print("✅ Retorno do login atualizado com o token.")
    else:
        # Fallback genérico: procura por 'return {' e adiciona o token antes do fechamento
        # Avisa que o arquivo pode ter uma estrutura diferente
        print("⚠️ Estrutura de retorno não encontrada no formato esperado. Tentando substituição genérica.")
        
        # Tenta encontrar onde o token é gerado e adicioná-lo à resposta
        # Se o token for gerado como 'access_token', precisamos garantir que esteja no retorno
        if 'create_access_token' in c and 'return {' in c:
            # Substitui o último 'return {' do arquivo por um que inclui o token
            matches = list(re.finditer(r'return\s*\{', c))
            if matches:
                ultimo_match = matches[-1]
                pos = ultimo_match.start()
                # Adiciona a chave "token" se não existir
                # Simplificando: apenas adiciona um campo no dict de retorno, mas precisa ser preciso
                # Vou usar uma string que o FastAPI entende: capturamos o token gerado
                c = c.replace('return {"requires_2fa": False, "user": user}', 'return {"requires_2fa": False, "user": user, "token": token}')
                c = c.replace('return {"requires_2fa": False, "user": user, "access_token": token}', 'return {"requires_2fa": False, "user": user, "token": token}')

    # Como fallback definitivo, injetamos o token diretamente na resposta, 
    # independentemente da estrutura, desde que a variável token exista.
    # Vamos garantir que, se 'token' está definido, ele seja retornado.
    if 'return {"requires_2fa": False, "user": user}' in c:
        c = c.replace('return {"requires_2fa": False, "user": user}', 'return {"requires_2fa": False, "user": user, "token": token}')
    
    # Se ainda não tem "token" no retorno, avisa
    if '"token":' not in c:
        print("❌ Não foi possível injetar o token no retorno. Verifique o código manualmente.")
    else:
        print("✅ Token injetado no retorno do login.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    fix_backend_login(os.getcwd())