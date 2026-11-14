import os

path_service = os.path.join(os.getcwd(), "app", "backend", "services", "whatsapp_service.py")

with open(path_service, "r", encoding="utf-8") as f:
    c = f.read()

if 'WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")' in c:
    print("✅ O código do backend está configurado para ler a variável WAHA_API_KEY.")
else:
    print("❌ O código do backend NÃO está configurado para ler a variável. Corrija o arquivo whatsapp_service.py.")