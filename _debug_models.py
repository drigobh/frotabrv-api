import os

def diag():
    raiz = os.getcwd()
    models_dir = os.path.join(raiz, "app", "backend", "models")
    
    if not os.path.exists(models_dir):
        print("❌ Pasta models não encontrada.")
        return
    
    print("=== ARQUIVOS NA PASTA MODELS ===")
    for f in os.listdir(models_dir):
        if f.endswith('.py'):
            print(f"  - {f}")
    
    # Procurar por conteúdo relacionado a veículos
    print("\n=== CONTEÚDO RELACIONADO A VEÍCULOS ===")
    for f in os.listdir(models_dir):
        if f.endswith('.py'):
            caminho = os.path.join(models_dir, f)
            with open(caminho, 'r', encoding='utf-8') as file:
                c = file.read()
            if 'veiculo' in c.lower() or 'placa' in c.lower():
                print(f"\n--- {f} ---")
                print(c[:800])

if __name__ == "__main__":
    diag()
    