import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv(os.path.join(os.getcwd(), "app", "backend", ".env"))

async def reativar_admin():
    mongo_url = os.getenv("MONGO_URL")
    if not mongo_url:
        print("❌ Variável MONGO_URL não encontrada no .env")
        return

    print("🔌 Conectando ao MongoDB...")
    client = AsyncIOMotorClient(mongo_url)
    db = client.frotabrv
    
    # Atualiza o usuário admin@frotabrv.com para ativo
    resultado = await db.usuarios.update_one(
        {"email": "admin@frotabrv.com"},
        {"$set": {"ativo": True}}
    )
    
    if resultado.modified_count > 0:
        print("✅ Usuário admin@frotabrv.com reativado com sucesso!")
    else:
        print("⚠️ Usuário não encontrado ou já estava ativo.")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(reativar_admin())