import os
import requests

# ATENÇÃO: Coloque aqui a URL do seu backend no Render ou localhost
# Exemplo: http://localhost:8000 ou https://sua-api.onrender.com
BASE_URL = "http://localhost:8000/api" 

# Você precisará de um token de admin. Se o seu sistema usa cookie/sessão, 
# pode ser mais fácil fazer isso direto pelo frontend depois.
# Se o sistema usa Bearer Token, cole ele aqui:
TOKEN = "SEU_TOKEN_AQUI"

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

dados = [
    {
        "nome": "1. Insumos Operacionais e Manutenção",
        "sub": [
            "Combustíveis e lubrificantes",
            "Peças e componentes",
            "Oficinas e serviços mecânicos"
        ]
    },
    {
        "nome": "2. Serviços de Apoio e Gestão",
        "sub": [
            "Tecnologia e rastreamento",
            "Pedágio e meios de pagamento",
            "Seguros",
            "Serviços gerais e administrativos"
        ]
    },
    {
        "nome": "3. Terceirização de Transporte (Agregados e Terceiros)",
        "sub": [
            "Transportadores autônomos de cargas (TAC) / Agregados",
            "Empresas parceiras de apoio"
        ]
    },
    {
        "nome": "4. Infraestrutura e Movimentação de Carga",
        "sub": [
            "Fabricantes de carrocerias e implementos",
            "Locadoras de veículos e frotas",
            "Equipamentos de movimentação",
            "Sistemas de armazenagem (Estruturas)"
        ]
    },
    {
        "nome": "5. Segurança e Gerenciamento de Risco (GR)",
        "sub": [
            "Gerenciadoras de risco",
            "Empresas de pronta resposta",
            "Sistemas de segurança física"
        ]
    },
    {
        "nome": "6. Sustentabilidade e ESG",
        "sub": [
            "Gestão de resíduos",
            "Consultorias de transição energética"
        ]
    },
    {
        "nome": "7. Recursos Humanos e Capacitação",
        "sub": [
            "Treinamento e direção defensiva",
            "Agências de recrutamento especializadas",
            "Plataformas de saúde ocupacional"
        ]
    }
]

def seed():
    print("Iniciando cadastro das categorias...")
    for cat in dados:
        # Cria a categoria pai
        res = requests.post(f"{BASE_URL}/tipos-fornecedores", json={"nome": cat["nome"]}, headers=HEADERS)
        if res.status_code == 201:
            pai_id = res.json()["id"]
            print(f"✅ Categoria criada: {cat['nome']}")
            
            # Cria as subcategorias
            for sub in cat["sub"]:
                res_sub = requests.post(f"{BASE_URL}/tipos-fornecedores", json={"nome": sub, "categoria_pai_id": pai_id}, headers=HEADERS)
                if res_sub.status_code == 201:
                    print(f"   └─ ✅ Subcategoria: {sub}")
                else:
                    print(f"   └─ ❌ Erro ao criar {sub}: {res_sub.text}")
        else:
            print(f"❌ Erro ao criar categoria {cat['nome']}: {res.text}")

if __name__ == "__main__":
    seed()