import os

def diag():
    caminho = os.path.join(os.getcwd(), "frontend", "src", "components", "ChassiMapa.tsx")
    if not os.path.exists(caminho):
        print("❌ ChassiMapa.tsx não encontrado.")
        return

    with open(caminho, "r", encoding="utf-8") as f:
        c = f.read()

    print("=== PRIMEIRAS 60 LINHAS ===")
    print("\n".join(c.split("\n")[:60]))
    print("\n=== TRECHO DO CARD DO PNEU (renderCardPneu) ===")
    idx = c.find("const renderCardPneu")
    if idx != -1:
        print(c[idx:idx+1500])
    else:
        print("❌ Não achei a função renderCardPneu.")
    print("\n=== TRECHO FINAL (return do componente) ===")
    idx = c.find("return (")
    if idx != -1:
        print(c[idx:idx+1000])

if __name__ == "__main__":
    diag()