import os
import requests
import urllib.parse
from datetime import datetime

WAHA_URL = os.getenv("WAHA_URL", "http://localhost:3000")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")
WAHA_SESSION = os.getenv("WAHA_SESSION", "default")

def configurado() -> bool:
    return bool(WAHA_URL)

def verificar_status() -> dict:
    if not configurado():
        return {"conectado": False, "erro": "WAHA_URL não configurada."}
    try:
        url = f"{WAHA_URL}/api/sessions/{WAHA_SESSION}"
        headers = {"X-Api-Key": WAHA_API_KEY} if WAHA_API_KEY else {}
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        status = data.get("status", "UNKNOWN")
        return {
            "conectado": status == "WORKING",
            "status": status,
            "smartphone_conectado": status == "WORKING",
            "erro": "" if status == "WORKING" else f"Status: {status}"
        }
    except Exception as e:
        return {"conectado": False, "erro": str(e)}

def enviar_mensagem(telefone: str, mensagem: str) -> dict:
    if not configurado():
        return {"sucesso": False, "erro": "WAHA_URL não configurada."}
    
    numero_limpo = "".join(filter(str.isdigit, telefone))
    if len(numero_limpo) < 10:
        return {"sucesso": False, "erro": "Número de telefone inválido."}
    
    # Formato do chatId do WhatsApp: {numero}@c.us
    chat_id = f"{numero_limpo}@c.us"
    
    try:
        url = f"{WAHA_URL}/api/sendText"
        headers = {"X-Api-Key": WAHA_API_KEY, "Content-Type": "application/json"} if WAHA_API_KEY else {"Content-Type": "application/json"}
        payload = {
            "session": WAHA_SESSION,
            "chatId": chat_id,
            "text": mensagem
        }
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if res.status_code in [200, 201]:
            return {"sucesso": True, "detalhes": res.json()}
        else:
            return {"sucesso": False, "erro": f"HTTP {res.status_code}: {res.text}"}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}
