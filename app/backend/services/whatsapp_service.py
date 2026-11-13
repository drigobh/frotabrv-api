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
        url = f"{WAHA_URL}/api/sessions/{WAHA_SESSION}"
        # Timeout de 60s para aguentar o cold start do Render
        res = requests.get(url, headers=_headers(), timeout=60)
        
        # Se retornar 404, a sessão não existe. Vamos criá-la.
        if res.status_code == 404:
            return criar_e_iniciar_sessao()
            
        # Se não for 200, pode ser um erro do Render (ex: 502).
        if res.status_code != 200:
            return {"conectado": False, "status": f"ERRO_{res.status_code}", "erro": f"O WAHA retornou {res.status_code}. Pode estar acordando.", "url_conectada": WAHA_URL}

        data = res.json()
        status = data.get("status", "UNKNOWN")
        
        # Se a sessão está parada, tenta iniciar.
        if status in ["STOPPED", "UNKNOWN"]:
            requests.post(f"{WAHA_URL}/api/sessions/{WAHA_SESSION}/start", json={}, headers=_headers(), timeout=60)
            time.sleep(5)
            res2 = requests.get(url, headers=_headers(), timeout=60)
            if res2.status_code == 200:
                data = res2.json()
                status = data.get("status", "UNKNOWN")
        
        return {
            "conectado": status == "WORKING",
            "status": status,
            "smartphone_conectado": status == "WORKING",
            "erro": "" if status == "WORKING" else f"Status: {status}",
            "url_conectada": WAHA_URL
        }
    except requests.exceptions.Timeout:
        return {"conectado": False, "erro": "Timeout: O WAHA está demorando para acordar. Tente novamente em 1 minuto.", "url_conectada": WAHA_URL}
    except Exception as e:
        return {"conectado": False, "erro": f"Erro de conexão: {str(e)}", "url_conectada": WAHA_URL}

def criar_e_iniciar_sessao() -> dict:
    try:
        url_create = f"{WAHA_URL}/api/sessions"
        payload = {"name": WAHA_SESSION, "start": True}
        res = requests.post(url_create, json=payload, headers=_headers(), timeout=60)
        
        if res.status_code in [200, 201]:
            time.sleep(8)
            url_status = f"{WAHA_URL}/api/sessions/{WAHA_SESSION}"
            res_status = requests.get(url_status, headers=_headers(), timeout=60)
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
    
    chat_id = f"{numero_limpo}@c.us"
    
    try:
        url = f"{WAHA_URL}/api/sendText"
        payload = {
            "session": WAHA_SESSION,
            "chatId": chat_id,
            "text": mensagem
        }
        res = requests.post(url, json=payload, headers=_headers(), timeout=60)
        
        if res.status_code in [200, 201]:
            return {"sucesso": True, "detalhes": res.json()}
        else:
            return {"sucesso": False, "erro": f"HTTP {res.status_code}: {res.text[:100]}"}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}
