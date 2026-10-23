from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from lib.db import db
from routers import auth, veiculos, carretas, motoristas, dashboard, acoplamentos, abastecimentos, manutencoes, admin

from lib.security import hash_password
import os

app = FastAPI(title="FrotaBravus API")

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://frotabrv-api.onrender.com", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas com prefixos corretos
app.include_router(auth.router)
app.include_router(veiculos.router)
app.include_router(carretas.router)
app.include_router(motoristas.router)
app.include_router(dashboard.router)
app.include_router(acoplamentos.router)
app.include_router(manutencoes.router)
app.include_router(admin.router)

@app.on_event("startup")
async def startup():
    print("✅ API Iniciada com sucesso!")

@app.on_event("shutdown")
async def shutdown():
    print("🛑 API Finalizada.")
