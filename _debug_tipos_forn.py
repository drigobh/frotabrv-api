import os

def diag():
    caminho = os.path.join(os.getcwd(), "frontend", "src", "pages", "TiposFornecedores.tsx")
    if not os.path.exists(caminho):
        print("❌ Arquivo não encontrado.")
        return

    with open(caminho, "r", encoding="utf-8") as f:
        c = f.read()

    # Mostra o trecho do PageHeader (onde fica o botão "Nova Marca" ou "Novo Tipo")
    idx = c.find('<PageHeader')
    if idx != -1:
        print("=== TRECHO DO PAGEHEADER ===")
        print(c[idx:idx+1000])
    else:
        print("❌ Não achei o PageHeader.")

if __name__ == "__main__":
    diag()