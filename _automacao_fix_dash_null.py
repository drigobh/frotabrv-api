import os

def corrigir_dashboard_null(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "dashboard.py")
    
    if not os.path.exists(caminho):
        print("❌ Arquivo dashboard.py não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # A correção: usa (a.get("km_rodados") or 0) para ignorar se for nulo
    c = c.replace(
        'ranking[v_id]["km"] += a.get("km_rodados", 0)',
        'ranking[v_id]["km"] += (a.get("km_rodados") or 0)'
    )
    
    # Garantindo que os litros também não quebrem se estiverem nulos
    c = c.replace(
        'ranking[v_id]["litros"] += a.get("litros", 0)',
        'ranking[v_id]["litros"] += (a.get("litros") or 0)'
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Backend: Correção dos campos nulos aplicada no Dashboard.")

if __name__ == "__main__":
    corrigir_dashboard_null(os.getcwd())