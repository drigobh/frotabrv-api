import os
import requests
import urllib.parse
from datetime import datetime

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
        res = requests.get(url, headers=_headers(), timeout=15)
        
        if res.status_code == 404:
            # Sessão não existe, vamos criá-la
            return criar_sessao()
        
        data = res.json()
        status = data.get("status", "UNKNOWN")
        
        # Se a sessão está STOPPED ou UNKNOWN, tenta iniciar
        if status in ["STOPPED", "UNKNOWN"]:
            iniciar_sessao()
            # Re-verifica após iniciar
            res2 = requests.get(url, headers=_headers(), timeout=15)
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
        return {"conectado": False, "erro": str(e), "url_conectada": WAHA_URL}

def criar_sessao() -> dict:
    try:
        url = f"{WAHA_URL}/api/sessions"
        payload = {"name": WAHA_SESSION, "start": True}
        res = requests.post(url, json=payload, headers=_headers(), timeout=15)
        if res.status_code in [200, 201]:
            return {"conectado": False, "status": "STARTING", "erro": "Sessão criada. Aguardando QR Code.", "url_conectada": WAHA_URL}
        else:
            return {"conectado": False, "status": "FAILED", "erro": f"Erro ao criar sessão: {res.text}", "url_conectada": WAHA_URL}
    except Exception as e:
        return {"conectado": False, "erro": str(e), "url_conectada": WAHA_URL}

def iniciar_sessao() -> bool:
    try:
        url = f"{WAHA_URL}/api/sessions/{WAHA_SESSION}/start"
        res = requests.post(url, json={}, headers=_headers(), timeout=15)
        return res.status_code in [200, 201]
    except Exception:
        return False

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
        res = requests.post(url, json=payload, headers=_headers(), timeout=15)
        
        if res.status_code in [200, 201]:
            return {"sucesso": True, "detalhes": res.json()}
        else:
            return {"sucesso": False, "erro": f"HTTP {res.status_code}: {res.text}"}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}
