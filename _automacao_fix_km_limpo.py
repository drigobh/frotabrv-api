import os
import re

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Substituir a função calcular_km inteira por uma versão com limpeza de dados (limpar_km)
    padrao = re.compile(r'def calcular_km\([\s\S]*?return km_rodados, media_km_l', re.DOTALL)
    
    nova_funcao = '''def limpar_km(val):
    if val is None: return 0
    s = str(val).strip()
    if s.endswith(".0"): s = s[:-2]
    s = "".join(filter(str.isdigit, s))
    return int(s) if s else 0

def calcular_km(km_atual, litros, produto, ultimo, veiculo):
    km_atual = limpar_km(km_atual)
    km_rodados = None
    media_km_l = None

    if ultimo and ultimo.get("km"):
        ultimo_km = limpar_km(ultimo["km"])
        km_rodados = km_atual - ultimo_km
    elif veiculo.get("hodometro_km") is not None:
        veiculo_km = limpar_km(veiculo["hodometro_km"])
        km_rodados = km_atual - veiculo_km

    if km_rodados is not None:
        if km_rodados < 0:
            km_rodados = None
        elif km_rodados > 0 and litros > 0 and "ARLA" not in (produto or "").upper():
            media_km_l = km_rodados / litros
        elif km_rodados == 0:
            media_km_l = 0

    return km_rodados, media_km_l'''

    if padrao.search(c):
        c = padrao.sub(lambda m: nova_funcao, c)
    else:
        # Fallback caso o regex não encontre
        c = c.replace('def calcular_km(km_atual, litros, produto, ultimo, veiculo):', 'def limpar_km(val):\n    if val is None: return 0\n    s = str(val).strip()\n    if s.endswith(".0"): s = s[:-2]\n    s = "".join(filter(str.isdigit, s))\n    return int(s) if s else 0\n\ndef calcular_km(km_atual, litros, produto, ultimo, veiculo):\n    km_atual = limpar_km(km_atual)')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Backend: Função calcular_km blindada contra erros de formatação de números.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Garantir que o KM no salvamento manual seja sempre um inteiro puro (sem pontos ou vírgulas)
    if 'km: Number(form.km),' in c:
        c = c.replace('km: Number(form.km),', 'km: Number(String(form.km).replace(/\\D/g, "")),')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Entrada de KM sanitizada para salvar apenas inteiros.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)