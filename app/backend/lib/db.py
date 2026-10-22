"""Shared Mongo handle — import `client`/`db` from here (server.py, routers, seed.py)."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING, IndexModel

load_dotenv(Path(__file__).parent.parent / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

logger = logging.getLogger(__name__)


def _id() -> IndexModel:
    return IndexModel([("id", ASCENDING)], name="id", unique=True)


# One entry per collection: every field a route filters, sorts, or dedupes on. Applied by ensure_indexes() at startup.
INDEXES: dict[str, list[IndexModel]] = {
    "usuarios": [_id(), IndexModel([("email", ASCENDING)], name="email", unique=True)],
    "veiculos": [_id(), IndexModel([("placa", ASCENDING)], name="placa", unique=True)],
    "carretas": [_id(), IndexModel([("codigo", ASCENDING)], name="codigo", unique=True)],
    "motoristas": [_id(), IndexModel([("cnh", ASCENDING)], name="cnh", unique=True)],
    "acoplamentos": [_id(), IndexModel([("status", ASCENDING), ("created_at", DESCENDING)], name="status_created")],
    "acoplamentos_historico": [
        _id(),
        IndexModel([("created_at", DESCENDING)], name="created_desc"),
        IndexModel([("acoplamento_id", ASCENDING), ("created_at", DESCENDING)], name="acop_created"),
    ],
    "abastecimentos": [
        _id(),
        IndexModel([("data", DESCENDING)], name="data_desc"),
        IndexModel([("veiculo_id", ASCENDING), ("km", DESCENDING)], name="veiculo_km"),
    ],
    "manutencoes": [_id(), IndexModel([("data", DESCENDING)], name="data_desc")],
    "auditoria": [_id(), IndexModel([("created_at", DESCENDING)], name="created_desc")],
    "documentos": [_id(), IndexModel([("validade", ASCENDING)], name="validade")],
    "contas": [
        _id(),
        IndexModel([("origem_id", ASCENDING)], name="origem_id"),
        IndexModel([("tipo", ASCENDING), ("status", ASCENDING), ("vencimento", DESCENDING)], name="tipo_status_venc"),
    ],
    "fretes": [_id(), IndexModel([("data", DESCENDING)], name="data_desc")],
    "config": [IndexModel([("chave", ASCENDING)], name="chave", unique=True)],
    "avisos_envios": [_id(), IndexModel([("enviado_em", DESCENDING)], name="enviado_desc")],
    "cron_runs": [IndexModel([("run_id", ASCENDING)], name="run_id", unique=True)],
    "parabens_envios": [IndexModel([("mes", ASCENDING), ("enviado_em", DESCENDING)], name="mes_enviado")],
}


async def ensure_indexes() -> None:
    for collection, models in INDEXES.items():
        for model in models:  # one at a time so a bad spec skips only itself
            try:
                await db[collection].create_indexes([model])
            except Exception as exc:  # never block boot on an index; the log line names what to fix
                logger.error("ensure_indexes(%s.%s): %s", collection, model.document["name"], exc)
