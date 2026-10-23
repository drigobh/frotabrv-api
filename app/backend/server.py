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
app.include_router(auth.router, prefix="/api/auth")
app.include_router(veiculos.router, prefix="/api/veiculos")
app.include_router(carretas.router, prefix="/api/carretas")
app.include_router(motoristas.router, prefix="/api/motoristas")
app.include_router(dashboard.router, prefix="/api/dashboard")
app.include_router(acoplamentos.router, prefix="/api/acoplamentos")
app.include_router(abastecimentos.router, prefix="/api/abastecimentos")
app.include_router(manutencoes.router, prefix="/api/manutencoes")
app.include_router(admin.router, prefix="/api/admin")

@app.on_event("startup")
async def startup():
    print("✅ API Iniciada com sucesso!")

@app.on_event("shutdown")
async def shutdown():
    print("🛑 API Finalizada.")
