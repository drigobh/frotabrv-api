from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import os
from lib.db import ensure_indexes, client

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_indexes()
    yield
    client.close()

app = FastAPI(title="FrotaBrv API", lifespan=lifespan)

origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

@api_router.get("/health")
async def health():
    return {"status": "ok", "service": "frota-brv"}

# Importando todas as rotas
from routers import empresa
from routers import chassi_templates, pneu_marcas, pneu_medidas, pneus, planos_manutencao, tipos_fornecedores, parametrizacao, auth, movimentacoes, pecas, fornecedores, combustiveis, veiculos, carretas, motoristas, dashboard, acoplamentos, abastecimentos, manutencoes
from routers import empresa
from routers import admin

api_router.include_router(auth.router)
api_router.include_router(movimentacoes.router)
api_router.include_router(pecas.router)
api_router.include_router(fornecedores.router)
api_router.include_router(combustiveis.router)
api_router.include_router(veiculos.router)
api_router.include_router(carretas.router)
api_router.include_router(motoristas.router)
api_router.include_router(dashboard.router)
api_router.include_router(acoplamentos.router)
api_router.include_router(abastecimentos.router)
api_router.include_router(manutencoes.router)
api_router.include_router(parametrizacao.router)
api_router.include_router(planos_manutencao.router)
api_router.include_router(pneus.router)
api_router.include_router(pneu_medidas.router)
api_router.include_router(pneu_marcas.router)
api_router.include_router(chassi_templates.router)
api_router.include_router(empresa.router)
api_router.include_router(tipos_fornecedores.router)

app.include_router(api_router)
app.include_router(admin.router)
