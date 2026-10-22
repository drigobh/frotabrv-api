from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import os
from lib.db import ensure_indexes, client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria os índices no Mongo ao iniciar
    await ensure_indexes()
    yield
    # Fecha conexão ao desligar
    client.close()

app = FastAPI(title="FrotaBrv API", lifespan=lifespan)

# CORS (Permite que o frontend acesse a API)
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

app.include_router(api_router)
