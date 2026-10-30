import os

def diag():
    caminho = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")
    if not os.path.exists(caminho):
        print("❌ Arquivo não encontrado.")
        return

    with open(caminho, "r", encoding="utf-8") as f:
        c = f.read()

    # Tenta achar o array MENUS
    idx = c.find("const MENUS")
    if idx == -1:
        idx = c.find("MENUS =")
    
    if idx != -1:
        print("=== TRECHO DO ARRAY MENUS ===")
        print(c[idx:idx+3000])
    else:
        print("❌ Não achei o array MENUS. Mostrando primeiras 80 linhas:")
        print("\n".join(c.split("\n")[:80]))

if __name__ == "__main__":
    diag()