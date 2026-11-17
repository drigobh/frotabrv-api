from fastapi import HTTPException

from lib.db import client, db

CONFIG_ID = "categorias-chassi-v1"
PADROES = (
    ("CAVALO", "Cavalo Mecânico"),
    ("CARRETA", "Carreta / Semirreboque"),
)


async def transacao_chassi(operacao):
    # Serializa as escritas que criam vínculos e as exclusões que os verificam.
    async def executar(session):
        await db.chassi_controle.update_one(
            {"_id": CONFIG_ID},
            {"$inc": {"versao_vinculos": 1}},
            upsert=True,
            session=session,
        )
        return await operacao(session)

    async with await client.start_session() as session:
        return await session.with_transaction(executar)


async def inicializar_categorias_chassi():
    if await db.chassi_controle.find_one({"_id": CONFIG_ID, "categorias_inicializadas": True}):
        return

    async def inicializar(session):
        marcador = await db.chassi_controle.find_one({"_id": CONFIG_ID}, session=session)
        if marcador.get("categorias_inicializadas"):
            return
        for codigo, nome in PADROES:
            await db.chassi_categorias.update_one(
                {"_id": codigo},
                {"$setOnInsert": {"nome": nome, "nome_chave": nome.casefold(), "familia": codigo, "ativo": True}},
                upsert=True,
                session=session,
            )
        await db.chassi_controle.update_one(
            {"_id": CONFIG_ID}, {"$set": {"categorias_inicializadas": True}}, session=session
        )

    await transacao_chassi(inicializar)


async def inicializar_tipos_aplicacao():
    if await db.chassi_controle.find_one({"_id": CONFIG_ID, "tipos_aplicacao_inicializados": True}):
        return

    async def inicializar(session):
        marcador = await db.chassi_controle.find_one({"_id": CONFIG_ID}, session=session)
        if marcador.get("tipos_aplicacao_inicializados"):
            return
        for codigo, nome in PADROES:
            await db.chassi_tipos_aplicacao.update_one(
                {"_id": codigo},
                {"$setOnInsert": {"nome": nome, "nome_chave": nome.casefold(), "destino": codigo, "ativo": True}},
                upsert=True,
                session=session,
            )
        await db.chassi_controle.update_one(
            {"_id": CONFIG_ID}, {"$set": {"tipos_aplicacao_inicializados": True}}, session=session
        )
    await transacao_chassi(inicializar)


async def destino_categoria(categoria, session=None):
    if not categoria:
        return None
    tipo = await db.chassi_tipos_aplicacao.find_one({"_id": categoria["familia"]}, session=session)
    return tipo["destino"] if tipo else None


async def categoria_chassi(codigo, session=None):
    return await db.chassi_categorias.find_one({"_id": codigo}, session=session)


async def validar_template_aplicavel(template_id, familia, session):
    template = await db.chassi_templates.find_one({"id": template_id}, session=session)
    if not template:
        raise HTTPException(409, "Template de chassi não encontrado. Atualize a lista.")
    categoria = await categoria_chassi(template["categoria"], session)
    if await destino_categoria(categoria, session) != familia:
        raise HTTPException(409, "O template de chassi não é compatível com este cadastro.")
