import os
import re

def fix_login(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Login.tsx")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Encontra a linha exata onde o login é processado
    # O seu arquivo original usa: const login = useMutation({ ... onSuccess: (r) => { ... } })
    # Vou substituir o onSuccess inteiro para incluir o salvamento do token.
    
    padrao = re.compile(
        r'onSuccess:\s*\(r\)\s*=>\s*\{[\s\S]*?(beginSession\(\);)?[\s\S]*?navigate\("/",\s*\{\s*replace:\s*true\s*\}\);[\s\S]*?\}',
        re.DOTALL
    )

    novo_on_success = '''onSuccess: (r) => {
      setErro(null);
      if (r.requires_2fa) {
        setPrecisa2fa(true);
        toast.info("Informe o código do Google Authenticator");
        return;
      }
      // Salva o token recebido do backend
      if (r.token) {
        localStorage.setItem("token", r.token);
        localStorage.setItem("auth_token", r.token);
      }
      beginSession();
      navigate("/", { replace: true });
    }'''

    if padrao.search(c):
        c = padrao.sub(novo_on_success, c)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Login.tsx corrigido: O token agora é salvo antes do navigate.")
    else:
        print("⚠️ Não foi possível encontrar o bloco onSuccess. Tentando substituição por linha simples...")
        
        # Fallback: substitui a linha do beginSession
        if 'beginSession();' in c:
            c = c.replace(
                'beginSession();',
                'if (r.token) { localStorage.setItem("token", r.token); localStorage.setItem("auth_token", r.token); }\n      beginSession();'
            )
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Token salvo antes do beginSession (fallback).")
        else:
            print("❌ Não foi possível encontrar o ponto de injeção no Login.tsx.")

if __name__ == "__main__":
    fix_login(os.getcwd())