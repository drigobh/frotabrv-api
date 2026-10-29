import os

def diag():
    raiz = os.getcwd()
    
    # 1. Backend Model
    m_path = os.path.join(raiz, "app", "backend", "models", "manutencoes.py")
    print("=" * 50)
    print("=== MODEL: manutencoes.py ===")
    print("=" * 50)
    if os.path.exists(m_path):
        print(open(m_path, "r", encoding="utf-8").read())
    else:
        print("❌ Não encontrado.")

    # 2. Backend Router (Apenas a função de criar/atualizar)
    r_path = os.path.join(raiz, "app", "backend", "routers", "manutencoes.py")
    print("\n" + "=" * 50)
    print("=== ROUTER: manutencoes.py (Trecho de Criação) ===")
    print("=" * 50)
    if os.path.exists(r_path):
        c = open(r_path, "r", encoding="utf-8").read()
        idx = c.find('@router.post')
        if idx != -1:
            print(c[idx:idx+2500])
        else:
            print(c[:2000])
    else:
        print("❌ Não encontrado.")

    # 3. Frontend (Topo e o formulário do modal)
    f_path = os.path.join(raiz, "frontend", "src", "pages", "Manutencoes.tsx")
    print("\n" + "=" * 50)
    print("=== FRONTEND: Manutencoes.tsx (Topo e Form) ===")
    print("=" * 50)
    if os.path.exists(f_path):
        c = open(f_path, "r", encoding="utf-8").read()
        # Pega o topo (até o return)
        idx_return = c.find("return (")
        if idx_return != -1:
            print("--- TOPO ---")
            print(c[:idx_return])
        # Pega o trecho do modal (onde tem os inputs)
        idx_form = c.find("<form")
        if idx_form != -1:
            print("\n--- TRECHO DO MODAL ---")
            print(c[idx_form:idx_form+3000])
    else:
        print("❌ Não encontrado.")

if __name__ == "__main__":
    diag()