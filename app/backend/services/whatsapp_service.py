import os
import requests
import urllib.parse
import time

WAHA_URL = os.getenv("WAHA_URL", "https://frotabrv-wahazap.onrender.com")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")
WAHA_SESSION = os.getenv("WAHA_SESSION", "default")

def configurado() -> bool:
    return bool(WAHA_URL)

def _headers():
    if WAHA_API_KEY:
        return {"X-Api-Key": WAHA_API_KEY}
    return {}

def verificar_status() -> dict:
    if not configurado():
        return {"conectado": False, "erro": "WAHA_URL não configurada.", "url_conectada": WAHA_URL}
    
    try:
        # 1. Tenta obter a sessão específica
        url = f"{WAHA_URL}/api/sessions/{WAHA_SESSION}"
        res = requests.get(url, headers=_headers(), timeout=30) # Timeout maior para cold start
        
        if res.status_code == 404:
            # Sessão não existe, criar
            return criar_e_iniciar_sessao()
        
        data = res.json()
        status = data.get("status", "UNKNOWN")
        
        # 2. Se a sessão está parada ou desconhecida, tenta iniciar
        if status in ["STOPPED", "UNKNOWN"]:
            requests.post(f"{WAHA_URL}/api/sessions/{WAHA_SESSION}/start", json={}, headers=_headers(), timeout=30)
            # Aguarda um tempo para o engine inicializar
            time.sleep(5)
            # Re-verifica
            res2 = requests.get(url, headers=_headers(), timeout=30)
            data = res2.json()
            status = data.get("status", "UNKNOWN")
        
        return {
            "conectado": status == "WORKING",
            "status": status,
            "smartphone_conectado": status == "WORKING",
            "erro": "" if status == "WORKING" else f"Status: {status}",
            "url_conectada": WAHA_URL
        }
    except Exception as e:
        return {"conectado": False, "erro": f"Erro de conexão: {str(e)}", "url_conectada": WAHA_URL}

def criar_e_iniciar_sessao() -> dict:
    try:
        # Cria a sessão
        url_create = f"{WAHA_URL}/api/sessions"
        payload = {"name": WAHA_SESSION, "start": True}
        res = requests.post(url_create, json=payload, headers=_headers(), timeout=30)
        
        if res.status_code in [200, 201]:
            # Aguarda a inicialização
            time.sleep(8)
            # Verifica o status
            url_status = f"{WAHA_URL}/api/sessions/{WAHA_SESSION}"
            res_status = requests.get(url_status, headers=_headers(), timeout=30)
            data = res_status.json()
            status = data.get("status", "UNKNOWN")
            
            return {
                "conectado": status == "WORKING",
                "status": status,
                "smartphone_conectado": status == "WORKING",
                "erro": "" if status == "WORKING" else f"Sessão criada. Status: {status}",
                "url_conectada": WAHA_URL
            }
        else:
            return {"conectado": False, "status": "FAILED", "erro": f"Erro ao criar sessão: {res.text}", "url_conectada": WAHA_URL}
    except Exception as e:
        return {"conectado": False, "erro": f"Erro ao criar sessão: {str(e)}", "url_conectada": WAHA_URL}

def enviar_mensagem(telefone: str, mensagem: str) -> dict:
    if not configurado():
        return {"sucesso": False, "erro": "WAHA_URL não configurada."}
    
    numero_limpo = "".join(filter(str.isdigit, telefone))
    if len(numero_limpo) < 10:
        return {"sucesso": False, "erro": "Número de telefone inválido."}
    
    # Formato correto do WAHA: {numero}@c.us
    chat_id = f"{numero_limpo}@c.us"
    
    try:
        url = f"{WAHA_URL}/api/sendText"
        payload = {
            "session": WAHA_SESSION,
            "chatId": chat_id,
            "text": mensagem
        }
        res = requests.post(url, json=payload, headers=_headers(), timeout=30)
        
        if res.status_code in [200, 201]:
            return {"sucesso": True, "detalhes": res.json()}
        else:
            return {"sucesso": False, "erro": f"HTTP {res.status_code}: {res.text}"}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}
