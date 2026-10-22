"""Contas automáticas: cada abastecimento, manutenção (com custo) e frete gera/atualiza uma conta."""

import uuid

from lib.dates import now_iso
from lib.db import db


async def sincronizar_conta(
    *,
    origem: str,
    origem_id: str,
    tipo: str,
    descricao: str,
    categoria: str,
    veiculo_id: str | None,
    veiculo_label: str | None,
    valor: float,
    vencimento: str,
    criado_por: str,
    status: str = "aberta",
    pago_em: str | None = None,
) -> None:
    """Cria ou atualiza a conta da origem. Valor 0 remove a conta se ainda estiver aberta."""
    atual = await db.contas.find_one({"origem_id": origem_id}, {"_id": 0})
    if valor <= 0:
        if atual and atual["status"] == "aberta":
            await db.contas.delete_one({"origem_id": origem_id})
        return
    campos = {
        "descricao": descricao, "categoria": categoria, "veiculo_id": veiculo_id,
        "veiculo_label": veiculo_label, "valor": round(valor, 2), "vencimento": vencimento,
    }
    if atual:
        await db.contas.update_one({"origem_id": origem_id}, {"$set": campos})
        return
    await db.contas.insert_one({
        "id": str(uuid.uuid4()), "tipo": tipo, "origem": origem, "origem_id": origem_id, **campos,
        "status": status, "pago_em": pago_em, "created_by": criado_por, "created_at": now_iso(),
    })


async def remover_conta(origem_id: str) -> None:
    await db.contas.delete_one({"origem_id": origem_id})
