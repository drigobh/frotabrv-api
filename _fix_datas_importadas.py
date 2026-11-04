import os
import asyncio
from lib.db import db

async def corrigir():
    pneus = await db.pneus.find({"data_compra": {"$ne": ""}}, {"_id": 0}).to_list(2000)
    total = 0
    for p in pneus:
        data = str(p.get("data_compra", "")).strip()
        if data and " " in data:
            data_limpa = data.split(" ")[0]
            await db.pneus.update_one({"id": p["id"]}, {"$set": {"data_compra": data_limpa}})
            total += 1
    print(f"✅ {total} pneus tiveram a data_compra corrigida para YYYY-MM-DD.")

if __name__ == "__main__":
    asyncio.run(corrigir())